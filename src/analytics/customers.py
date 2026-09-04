import pandas as pd
from typing import Dict, Any, Tuple

EXCLUDED_CUSTOMERS = {"Unspecified", "nan", "None", ""}

def _filter_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Returns rows with real customer identifiers only."""
    if "customer_id" not in df.columns:
        return pd.DataFrame()
    return df[~df["customer_id"].astype(str).isin(EXCLUDED_CUSTOMERS)]

def calculate_customer_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes customer-level KPIs: total, new, repeat customers and engagement metrics.
    """
    if df.empty or "customer_id" not in df.columns:
        return {
            "available": False,
            "reason": "Customer analytics unavailable because no customer identifier column was detected in the dataset.",
            "total_customers": 0,
            "new_customers": 0,
            "repeat_customers": 0,
            "repeat_rate_pct": 0.0,
            "avg_revenue_per_customer": 0.0,
            "avg_orders_per_customer": 0.0,
            "avg_items_per_customer": 0.0,
            "top_customer_share_pct": 0.0,
            "unattributed_revenue_pct": 0.0
        }

    cust_df = _filter_customers(df)
    if cust_df.empty:
        return {
            "available": False,
            "reason": "Customer analytics unavailable because all transactions lack customer identifiers.",
            "total_customers": 0,
            "new_customers": 0,
            "repeat_customers": 0,
            "repeat_rate_pct": 0.0,
            "avg_revenue_per_customer": 0.0,
            "avg_orders_per_customer": 0.0,
            "avg_items_per_customer": 0.0,
            "top_customer_share_pct": 0.0,
            "unattributed_revenue_pct": 0.0
        }

    total_revenue = float(df["revenue"].sum())
    attributed_revenue = float(cust_df["revenue"].sum())

    # Per-customer aggregation
    cust_agg = cust_df.groupby("customer_id").agg(
        revenue=("revenue", "sum"),
        orders=("order_id", "nunique"),
        items=("quantity", "sum"),
        first_order=("date", "min"),
        region=("region", "first")
    ).reset_index()

    total_customers = len(cust_agg)
    repeat_customers = int((cust_agg["orders"] >= 2).sum())
    repeat_rate_pct = float(repeat_customers / total_customers * 100.0) if total_customers > 0 else 0.0

    # New customers = first order within the filtered date window
    first_order_month = cust_agg["first_order"].dt.to_period("M")
    latest_month = df["date"].dt.to_period("M").max()
    new_customers = int((first_order_month == latest_month).sum())

    avg_revenue_per_customer = float(attributed_revenue / total_customers) if total_customers > 0 else 0.0
    avg_orders_per_customer = float(cust_agg["orders"].sum() / total_customers) if total_customers > 0 else 0.0
    avg_items_per_customer = float(cust_agg["items"].sum() / total_customers) if total_customers > 0 else 0.0

    top_revenue = float(cust_agg["revenue"].max())
    top_customer_share_pct = float(top_revenue / total_revenue * 100.0) if total_revenue > 0 else 0.0
    unattributed_revenue_pct = float((1 - attributed_revenue / total_revenue) * 100.0) if total_revenue > 0 else 0.0

    return {
        "available": True,
        "reason": None,
        "total_customers": total_customers,
        "new_customers": new_customers,
        "repeat_customers": repeat_customers,
        "repeat_rate_pct": round(repeat_rate_pct, 2),
        "avg_revenue_per_customer": round(avg_revenue_per_customer, 2),
        "avg_orders_per_customer": round(avg_orders_per_customer, 2),
        "avg_items_per_customer": round(avg_items_per_customer, 2),
        "top_customer_share_pct": round(top_customer_share_pct, 2),
        "unattributed_revenue_pct": round(unattributed_revenue_pct, 2),
        "customer_df": cust_agg
    }

def get_top_customers(cust_agg: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Returns top N customers ranked by revenue."""
    if cust_agg is None or cust_agg.empty:
        return pd.DataFrame()
    return cust_agg.sort_values("revenue", ascending=False).head(top_n).copy()

def get_customer_acquisition_trend(df: pd.DataFrame, freq: str = "MS") -> pd.DataFrame:
    """Computes new customer acquisition per time period."""
    cust_df = _filter_customers(df)
    if cust_df.empty:
        return pd.DataFrame()

    first_orders = cust_df.sort_values("date").groupby("customer_id")["date"].min().reset_index()
    trend = first_orders.set_index("date").resample(freq).size().reset_index(name="new_customers")
    trend["cumulative_customers"] = trend["new_customers"].cumsum()
    return trend

def get_customer_segments(cust_agg: pd.DataFrame) -> pd.DataFrame:
    """Segments customers by number of orders (loyalty tiers)."""
    if cust_agg is None or cust_agg.empty:
        return pd.DataFrame()

    def segment(orders):
        if orders == 1:
            return "1 Order (One-time)"
        if orders <= 5:
            return "2-5 Orders (Occasional)"
        if orders <= 15:
            return "6-15 Orders (Regular)"
        return "16+ Orders (Loyal)"

    segments = cust_agg.copy()
    segments["segment"] = segments["orders"].apply(segment)
    seg_df = segments.groupby("segment").agg(
        customers=("customer_id", "count"),
        revenue=("revenue", "sum")
    ).reset_index()
    seg_df["revenue_share_pct"] = ((seg_df["revenue"] / seg_df["revenue"].sum()) * 100.0).round(2)
    seg_df["customer_share_pct"] = ((seg_df["customers"] / seg_df["customers"].sum()) * 100.0).round(2)
    order_map = {"1 Order (One-time)": 0, "2-5 Orders (Occasional)": 1, "6-15 Orders (Regular)": 2, "16+ Orders (Loyal)": 3}
    seg_df["sort_order"] = seg_df["segment"].map(order_map)
    return seg_df.sort_values("sort_order").drop(columns=["sort_order"]).reset_index(drop=True)

def get_customer_revenue_distribution(cust_agg: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """Cumulative revenue concentration across top N customers."""
    if cust_agg is None or cust_agg.empty:
        return pd.DataFrame()
    sorted_cust = cust_agg.sort_values("revenue", ascending=False).reset_index(drop=True)
    total_rev = sorted_cust["revenue"].sum()
    sorted_cust["cum_share_pct"] = (sorted_cust["revenue"].cumsum() / total_rev * 100.0).round(2) if total_rev > 0 else 0.0
    top = sorted_cust.head(top_n).copy()
    top["rank"] = range(1, len(top) + 1)
    return top