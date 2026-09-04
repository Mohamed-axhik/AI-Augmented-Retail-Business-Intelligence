import pandas as pd
from typing import Dict, Any
from src.analytics.kpis import calculate_executive_kpis
from src.analytics.categories import get_category_performance
from src.analytics.products import get_product_performance, get_top_bottom_products
from src.analytics.stores import get_store_performance
from src.analytics.customers import calculate_customer_kpis
from src.anomaly.detector import detect_statistical_anomalies

def build_business_context(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Builds a compact structured analytical context payload for the LLM.
    Contains pre-computed deterministic metrics only.
    """
    if df.empty:
        return {"status": "Empty Dataset"}

    kpis = calculate_executive_kpis(df)
    cat_df = get_category_performance(df)
    prod_df = get_product_performance(df)
    top_prod, bottom_prod = get_top_bottom_products(prod_df, top_n=5)
    store_df, region_df = get_store_performance(df)
    customer_kpis = calculate_customer_kpis(df)
    _, anomalies = detect_statistical_anomalies(df)

    date_min = df["date"].min().strftime("%Y-%m-%d")
    date_max = df["date"].max().strftime("%Y-%m-%d")

    # Store summary falls back to country-level market analysis when store data is unavailable
    if len(store_df) > 1:
        location_summary = store_df[["store", "region", "revenue", "revenue_share_pct"]].head(5).to_dict("records")
    else:
        location_summary = region_df[["region", "revenue", "revenue_share_pct"]].head(5).rename(columns={"region": "country"}).to_dict("records")

    customer_summary = {k: v for k, v in customer_kpis.items() if k != "customer_df"}

    context = {
        "date_range": f"{date_min} to {date_max}",
        "executive_kpis": kpis,
        "category_summary": cat_df.to_dict("records") if not cat_df.empty else [],
        "top_5_products": top_prod[["product_name", "category", "revenue", "revenue_share_pct"]].to_dict("records") if not top_prod.empty else [],
        "bottom_5_products": bottom_prod[["product_name", "category", "revenue"]].to_dict("records") if not bottom_prod.empty else [],
        "store_summary": location_summary,
        "customer_summary": customer_summary,
        "detected_anomalies_count": len(anomalies),
        "recent_anomalies": anomalies[:3]
    }

    return context
