import pytest
import pandas as pd
import numpy as np
from src.processing.transformer import transform_to_canonical
from src.analytics.kpis import calculate_executive_kpis
from src.analytics.categories import get_category_performance

def test_kpi_calculations():
    data = {
        "date": pd.to_datetime(["2025-01-01", "2025-01-15", "2025-02-01"]),
        "order_id": ["ORD-1", "ORD-2", "ORD-3"],
        "product_name": ["Phone", "Laptop", "Phone"],
        "category": ["Electronics", "Electronics", "Electronics"],
        "quantity": [1, 2, 1],
        "unit_price": [1000, 2000, 1000],
        "revenue": [1000, 4000, 1000],
        "cost": [700, 1500, 700]
    }
    df = pd.DataFrame(data)
    mapping = {col: col for col in df.columns}
    canonical_df = transform_to_canonical(df, mapping)
    
    kpis = calculate_executive_kpis(canonical_df)
    assert kpis["total_revenue"] == 6000.0
    assert kpis["total_orders"] == 3
    assert kpis["units_sold"] == 4
    assert kpis["aov"] == 2000.0
    assert kpis["total_profit"] == 1600.0

def test_graceful_missing_cost_kpis():
    data = {
        "date": pd.to_datetime(["2025-01-01"]),
        "product_name": ["Shirt"],
        "category": ["Apparel"],
        "quantity": [2],
        "unit_price": [500],
        "revenue": [1000]
    }
    df = pd.DataFrame(data)
    mapping = {col: col for col in df.columns}
    canonical_df = transform_to_canonical(df, mapping)
    
    kpis = calculate_executive_kpis(canonical_df)
    assert kpis["total_revenue"] == 1000.0
    assert kpis["has_profit_data"] is False
    assert kpis["total_profit"] is None
    assert kpis["profit_margin_pct"] is None
