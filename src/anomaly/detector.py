import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from src.utils.formatting import CURRENCY_SYMBOL

def detect_statistical_anomalies(df: pd.DataFrame, z_threshold: float = 2.2) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    """
    Detects statistical revenue anomalies using Z-score and rolling baseline deviations.
    Identifies top root-cause drivers (category, product, store) for each anomaly date.
    Returns (annotated_daily_df, anomaly_list).
    """
    if df.empty or "date" not in df.columns:
        return pd.DataFrame(), []

    # Daily aggregation
    daily = df.groupby(df["date"].dt.date).agg({
        "revenue": "sum",
        "quantity": "sum",
        "order_id": "nunique"
    }).reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily.rename(columns={"order_id": "orders"}, inplace=True)

    if len(daily) < 5:
        return daily, []

    # Calculate rolling baseline stats (14-day window)
    daily["rolling_mean"] = daily["revenue"].rolling(window=14, min_periods=3, center=True).mean()
    daily["rolling_std"] = daily["revenue"].rolling(window=14, min_periods=3, center=True).std().fillna(1.0)
    
    # Global fallback if rolling std is zero
    global_mean = daily["revenue"].mean()
    global_std = daily["revenue"].std() if daily["revenue"].std() > 0 else 1.0

    daily["rolling_mean"] = daily["rolling_mean"].fillna(global_mean)
    daily["rolling_std"] = daily["rolling_std"].replace(0, global_std).fillna(global_std)

    # Z-Score calculation
    daily["z_score"] = (daily["revenue"] - daily["rolling_mean"]) / daily["rolling_std"]

    # IQR calculation
    q1 = daily["revenue"].quantile(0.25)
    q3 = daily["revenue"].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)

    # Anomaly flag
    daily["is_anomaly"] = (daily["z_score"].abs() > z_threshold) | (daily["revenue"] > upper_bound) | (daily["revenue"] < lower_bound)

    anomaly_records = []
    anomaly_dates = daily[daily["is_anomaly"]]

    # ------------------------------------------------------------------
    # Driver lookup, vectorized: precompute per-day top contributors once
    # instead of re-scanning the full frame for every anomaly date.
    # ------------------------------------------------------------------
    work = df.assign(_day=df["date"].dt.date)

    def _top_by_day(group_col: str):
        """Returns (label_map, value_map) of the top contributor per day."""
        sums = work.groupby(["_day", group_col])["revenue"].sum().reset_index(name="_rev")
        top = sums.loc[sums.groupby("_day")["_rev"].idxmax()]
        return top.set_index("_day")[group_col], top.set_index("_day")["_rev"]

    top_cat_map, top_cat_rev_map = _top_by_day("category")
    top_prod_map, top_prod_rev_map = _top_by_day("product_name")

    store_nunique_map = work.groupby("_day")["store"].nunique() if "store" in work.columns else None
    top_store_map, _ = _top_by_day("store") if "store" in work.columns else (None, None)
    top_region_map, _ = _top_by_day("region") if "region" in work.columns else (None, None)

    for _, row in anomaly_dates.iterrows():
        anomaly_date = row["date"]
        actual_rev = float(row["revenue"])
        expected_rev = float(row["rolling_mean"])
        dev_pct = round(((actual_rev - expected_rev) / expected_rev) * 100.0, 1) if expected_rev > 0 else 0.0

        day = anomaly_date.date()
        drivers = []

        if day in top_cat_map.index:
            cat = top_cat_map.loc[day]
            cat_rev = top_cat_rev_map.loc[day]
            drivers.append(f"Category: {cat} ({CURRENCY_SYMBOL}{cat_rev:,.0f})")

        if day in top_prod_map.index:
            prod = top_prod_map.loc[day]
            prod_rev = top_prod_rev_map.loc[day]
            drivers.append(f"Product: {prod} ({CURRENCY_SYMBOL}{prod_rev:,.0f})")

        if store_nunique_map is not None and day in store_nunique_map.index:
            if store_nunique_map.loc[day] > 1:
                if day in top_store_map.index:
                    drivers.append(f"Store: {top_store_map.loc[day]}")
            elif top_region_map is not None and day in top_region_map.index:
                drivers.append(f"Country: {top_region_map.loc[day]}")

        anomaly_type = "🔴 Spike (High)" if actual_rev > expected_rev else "🔵 Dip (Low)"

        anomaly_records.append({
            "date": anomaly_date.strftime("%Y-%m-%d"),
            "actual_revenue": round(actual_rev, 2),
            "expected_revenue": round(expected_rev, 2),
            "deviation_pct": dev_pct,
            "z_score": round(float(row["z_score"]), 2),
            "anomaly_type": anomaly_type,
            "possible_drivers": drivers
        })

    return daily, anomaly_records
