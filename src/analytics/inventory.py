import pandas as pd
import numpy as np
from typing import Dict, Any

def calculate_inventory_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes Level 3 Retail Inventory Intelligence metrics.
    Gracefully disables features if inventory or cost data is unavailable.
    """
    has_inventory = "inventory" in df.columns and not df["inventory"].isnull().all()
    has_cost = "cost" in df.columns and not df["cost"].isnull().all()

    if not has_inventory:
        return {
            "available": False,
            "reason": "Inventory metrics unavailable because required inventory fields were not detected in the dataset."
        }

    # Aggregate inventory by product (latest snapshot)
    latest_inv_df = df.groupby("product_name").agg({
        "inventory": "last",
        "quantity": "sum",
        "revenue": "sum",
        "category": "first",
        "unit_price": "last",
        "cost": "last" if has_cost else "first"
    }).reset_index()

    total_stock_units = int(latest_inv_df["inventory"].sum())
    
    # Valuation
    if has_cost:
        total_inventory_valuation = float((latest_inv_df["inventory"] * latest_inv_df["cost"]).sum())
        total_cogs = float((df["quantity"] * df["cost"]).sum())
        avg_inventory_valuation = total_inventory_valuation if total_inventory_valuation > 0 else 1.0
        inventory_turnover = round(total_cogs / avg_inventory_valuation, 2)
    else:
        total_inventory_valuation = float((latest_inv_df["inventory"] * latest_inv_df["unit_price"]).sum())
        inventory_turnover = None

    # Stockout risk indicators (Stock <= 5)
    stockout_items = latest_inv_df[latest_inv_df["inventory"] <= 5].copy()
    stockout_count = len(stockout_items)

    # Fast vs Slow Movers (Sales Velocity = Total Quantity Sold / Stock Level)
    latest_inv_df["sales_velocity"] = np.where(
        latest_inv_df["inventory"] > 0,
        (latest_inv_df["quantity"] / latest_inv_df["inventory"]).round(2),
        latest_inv_df["quantity"]
    )

    fast_movers = latest_inv_df.sort_values("sales_velocity", ascending=False).head(5)
    slow_movers = latest_inv_df[latest_inv_df["inventory"] > 10].sort_values("sales_velocity", ascending=True).head(5)

    return {
        "available": True,
        "total_stock_units": total_stock_units,
        "total_inventory_valuation": round(total_inventory_valuation, 2),
        "inventory_turnover": inventory_turnover,
        "has_cogs": has_cost,
        "stockout_risk_count": stockout_count,
        "stockout_items": stockout_items[["product_name", "category", "inventory", "unit_price"]].to_dict("records"),
        "fast_movers": fast_movers[["product_name", "category", "quantity", "inventory", "sales_velocity"]].to_dict("records"),
        "slow_movers": slow_movers[["product_name", "category", "quantity", "inventory", "sales_velocity"]].to_dict("records")
    }
