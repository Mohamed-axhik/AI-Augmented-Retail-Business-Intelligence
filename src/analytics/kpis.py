import pandas as pd
from typing import Dict, Any
from src.analytics.growth import calculate_growth_rates

def _safe_unique_count(series: pd.Series, exclude_values) -> int:
    """Counts unique non-excluded values in a series."""
    if series is None:
        return 0
    mask = ~series.astype(str).isin(exclude_values)
    return int(series[mask].nunique())

def calculate_executive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates executive-level business KPIs from standardized canonical DataFrame.
    Includes e-commerce metrics: customers, return rate, items per order.
    """
    empty_result = {
        "total_revenue": 0.0,
        "total_profit": None,
        "profit_margin_pct": None,
        "total_orders": 0,
        "units_sold": 0,
        "aov": 0.0,
        "total_customers": 0,
        "revenue_per_customer": 0.0,
        "avg_items_per_order": 0.0,
        "return_rate_pct": 0.0,
        "mom_growth_pct": None,
        "yoy_growth_pct": None,
        "has_profit_data": False,
        "has_inventory_data": False,
        "has_customer_data": False
    }
    if df.empty:
        return empty_result

    total_revenue = float(df["revenue"].sum())
    units_sold = int(df["quantity"].sum())
    gross_units = int(df.loc[df["quantity"] > 0, "quantity"].sum())
    returned_units = int(df.loc[df["quantity"] < 0, "quantity"].sum())

    # Unique orders calculation
    if "order_id" in df.columns and not df["order_id"].isin(["ORD-UNKNOWN"]).all():
        total_orders = int(df["order_id"].nunique())
    else:
        total_orders = len(df)

    aov = float(total_revenue / total_orders) if total_orders > 0 else 0.0
    avg_items_per_order = float(gross_units / total_orders) if total_orders > 0 else 0.0

    # Return rate: returned revenue vs gross (positive) revenue
    gross_revenue = float(df.loc[df["quantity"] > 0, "revenue"].sum())
    returned_revenue = float(df.loc[df["quantity"] < 0, "revenue"].sum())
    return_rate_pct = float(abs(returned_revenue) / gross_revenue * 100.0) if gross_revenue > 0 else 0.0

    # Customer metrics
    has_customer_data = "customer_id" in df.columns and not df["customer_id"].isin(["Unspecified"]).all()
    total_customers = 0
    revenue_per_customer = 0.0
    if has_customer_data:
        total_customers = _safe_unique_count(df["customer_id"], {"Unspecified", "nan", ""})
        revenue_per_customer = float(total_revenue / total_customers) if total_customers > 0 else 0.0

    # Profit calculations
    has_profit_data = "profit" in df.columns and not df["profit"].isnull().all()
    if has_profit_data:
        total_profit = float(df["profit"].sum())
        profit_margin_pct = float((total_profit / total_revenue) * 100.0) if total_revenue > 0 else 0.0
    else:
        total_profit = None
        profit_margin_pct = None

    # Growth rates
    growth_info = calculate_growth_rates(df)

    # Check inventory availability
    has_inventory_data = "inventory" in df.columns and not df["inventory"].isnull().all()

    return {
        "total_revenue": round(total_revenue, 2),
        "total_profit": round(total_profit, 2) if total_profit is not None else None,
        "profit_margin_pct": round(profit_margin_pct, 2) if profit_margin_pct is not None else None,
        "total_orders": total_orders,
        "units_sold": units_sold,
        "gross_units_sold": gross_units,
        "returned_units": returned_units,
        "aov": round(aov, 2),
        "avg_items_per_order": round(avg_items_per_order, 2),
        "return_rate_pct": round(return_rate_pct, 2),
        "total_customers": total_customers,
        "revenue_per_customer": round(revenue_per_customer, 2),
        "has_customer_data": has_customer_data,
        "mom_growth_pct": growth_info["mom_growth_pct"],
        "mom_revenue_delta": growth_info["mom_revenue_delta"],
        "yoy_growth_pct": growth_info["yoy_growth_pct"],
        "yoy_revenue_delta": growth_info["yoy_revenue_delta"],
        "latest_month": growth_info["latest_month"],
        "has_profit_data": has_profit_data,
        "has_inventory_data": has_inventory_data
    }