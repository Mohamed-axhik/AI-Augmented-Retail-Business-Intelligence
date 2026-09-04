import pandas as pd
from typing import Dict, Any

def get_sales_over_time(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    """
    Resamples sales data by frequency:
    'D' (Daily), 'W' (Weekly), 'MS' (Monthly), 'QS' (Quarterly).
    """
    if df.empty or "date" not in df.columns:
        return pd.DataFrame()

    df_indexed = df.set_index("date")

    agg_dict = {
        "revenue": "sum",
        "quantity": "sum",
        "order_id": "nunique"
    }

    has_profit = "profit" in df.columns and not df["profit"].isnull().all()
    if has_profit:
        agg_dict["profit"] = "sum"

    resampled = df_indexed.resample(freq).agg(agg_dict).reset_index()
    resampled.rename(columns={"order_id": "orders"}, inplace=True)

    # Derived metrics
    resampled["aov"] = (resampled["revenue"] / resampled["orders"]).fillna(0.0)
    
    if has_profit:
        resampled["profit_margin_pct"] = ((resampled["profit"] / resampled["revenue"]) * 100.0).fillna(0.0)

    # 7-period and 30-period rolling moving averages for trend smoothing
    resampled["revenue_7d_ma"] = resampled["revenue"].rolling(window=7, min_periods=1).mean()
    resampled["revenue_30d_ma"] = resampled["revenue"].rolling(window=30, min_periods=1).mean()

    return resampled
