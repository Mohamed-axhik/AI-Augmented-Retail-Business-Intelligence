import pandas as pd
from typing import Tuple, Dict, Any

def get_store_performance(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Computes store-level and regional-level performance summaries.
    Returns (store_df, region_df).
    """
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    total_revenue = df["revenue"].sum()
    has_profit = "profit" in df.columns and not df["profit"].isnull().all()

    # Store Aggregation
    store_agg = {
        "region": "first",
        "revenue": "sum",
        "quantity": "sum",
        "order_id": "nunique"
    }
    if has_profit:
        store_agg["profit"] = "sum"

    store_df = df.groupby("store").agg(store_agg).reset_index()
    store_df.rename(columns={"order_id": "orders"}, inplace=True)
    store_df["aov"] = (store_df["revenue"] / store_df["orders"]).round(2)
    store_df["revenue_share_pct"] = ((store_df["revenue"] / total_revenue) * 100.0).round(2) if total_revenue > 0 else 0.0

    if has_profit:
        store_df["profit_margin_pct"] = ((store_df["profit"] / store_df["revenue"]) * 100.0).round(2)

    store_df = store_df.sort_values("revenue", ascending=False).reset_index(drop=True)

    # Regional Aggregation
    reg_agg = {
        "store": "nunique",
        "revenue": "sum",
        "quantity": "sum",
        "order_id": "nunique"
    }
    has_customers = "customer_id" in df.columns and not df["customer_id"].isin(["Unspecified"]).all()
    if has_customers:
        reg_agg["customer_id"] = "nunique"
    if has_profit:
        reg_agg["profit"] = "sum"

    region_df = df.groupby("region").agg(reg_agg).reset_index()
    region_df.rename(columns={"store": "store_count", "order_id": "orders"}, inplace=True)
    if has_customers:
        region_df.rename(columns={"customer_id": "customers"}, inplace=True)
    region_df["revenue_share_pct"] = ((region_df["revenue"] / total_revenue) * 100.0).round(2) if total_revenue > 0 else 0.0

    if has_profit:
        region_df["profit_margin_pct"] = ((region_df["profit"] / region_df["revenue"]) * 100.0).round(2)

    region_df = region_df.sort_values("revenue", ascending=False).reset_index(drop=True)

    return store_df, region_df
