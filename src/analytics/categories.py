import pandas as pd
from typing import Dict, Any

def get_category_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes performance metrics aggregated by product category.
    """
    if df.empty or "category" not in df.columns:
        return pd.DataFrame()

    total_revenue = df["revenue"].sum()
    has_profit = "profit" in df.columns and not df["profit"].isnull().all()
    total_profit = df["profit"].sum() if has_profit else 0.0

    agg_dict = {
        "revenue": "sum",
        "quantity": "sum",
        "order_id": "nunique"
    }

    if has_profit:
        agg_dict["profit"] = "sum"

    cat_df = df.groupby("category").agg(agg_dict).reset_index()
    cat_df.rename(columns={"order_id": "orders"}, inplace=True)

    # Percentage contributions
    cat_df["revenue_share_pct"] = ((cat_df["revenue"] / total_revenue) * 100.0).round(2) if total_revenue > 0 else 0.0

    if has_profit:
        cat_df["profit_margin_pct"] = ((cat_df["profit"] / cat_df["revenue"]) * 100.0).round(2)
        cat_df["profit_share_pct"] = ((cat_df["profit"] / total_profit) * 100.0).round(2) if total_profit > 0 else 0.0

    cat_df["aov"] = (cat_df["revenue"] / cat_df["orders"]).round(2)
    cat_df = cat_df.sort_values("revenue", ascending=False).reset_index(drop=True)

    return cat_df
