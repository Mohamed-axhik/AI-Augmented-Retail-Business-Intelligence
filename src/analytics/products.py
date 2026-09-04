import pandas as pd
from typing import Tuple, Dict, Any

def get_product_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes performance metrics aggregated by product name.
    """
    if df.empty or "product_name" not in df.columns:
        return pd.DataFrame()

    total_revenue = df["revenue"].sum()
    has_profit = "profit" in df.columns and not df["profit"].isnull().all()
    total_profit = df["profit"].sum() if has_profit else 0.0

    agg_dict = {
        "category": "first",
        "revenue": "sum",
        "quantity": "sum",
        "unit_price": "mean",
        "order_id": "nunique"
    }

    if has_profit:
        agg_dict["profit"] = "sum"

    prod_df = df.groupby("product_name").agg(agg_dict).reset_index()
    prod_df.rename(columns={"order_id": "orders", "unit_price": "avg_unit_price"}, inplace=True)

    prod_df["revenue_share_pct"] = ((prod_df["revenue"] / total_revenue) * 100.0).round(2) if total_revenue > 0 else 0.0

    if has_profit:
        prod_df["profit_margin_pct"] = ((prod_df["profit"] / prod_df["revenue"]) * 100.0).round(2)
        prod_df["profit_share_pct"] = ((prod_df["profit"] / total_profit) * 100.0).round(2) if total_profit > 0 else 0.0

    # Pareto cumulative share calculation
    prod_df = prod_df.sort_values("revenue", ascending=False).reset_index(drop=True)
    prod_df["cum_revenue_share_pct"] = prod_df["revenue_share_pct"].cumsum().round(2)

    return prod_df

def get_top_bottom_products(prod_df: pd.DataFrame, top_n: int = 10) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns (top_n_products, bottom_n_products) sorted by revenue.
    """
    if prod_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    top_products = prod_df.head(top_n).copy()
    bottom_products = prod_df.tail(top_n).sort_values("revenue", ascending=True).copy()

    return top_products, bottom_products
