"""Category & Product Performance page."""
from __future__ import annotations

import streamlit as st
from src.analytics.categories import get_category_performance
from src.analytics.products import get_product_performance, get_top_bottom_products
from src.utils.formatting import format_currency
from ui.cards import render_insight_card
from ui.charts import (
    render_bottom_products_bar,
    render_category_bar,
    render_pareto_chart,
    render_top_products_bar,
)
from ui.layout import render_empty_state, render_hero, render_section_header


def render_category_and_product(df):
    """Renders the Category & Product Performance page."""
    render_hero(
        "PRODUCT INTELLIGENCE",
        "Category & Product Performance",
        "Contribution analysis, Pareto 80/20 distribution and product rankings.",
    )

    if df.empty:
        render_empty_state("No data available",
                           "The current filters exclude every row. Widen the date range or "
                           "clear the category / store filters in the sidebar.",
                           icon_name="filter")
        return

    cat_df = get_category_performance(df)
    prod_df = get_product_performance(df)

    # Insight cards
    render_section_header("sparkles", "Product Insights",
                          "Key signals from category and product performance")

    ins1, ins2, ins3 = st.columns(3)
    with ins1:
        if not cat_df.empty:
            top_cat = cat_df.iloc[0]
            render_insight_card("Top Category", top_cat["category"],
                                f"{top_cat['revenue_share_pct']:.1f}% of total revenue",
                                icon_name="tag", tone="blue")
        else:
            render_insight_card("Top Category", "N/A", "No category data",
                                icon_name="tag", tone="blue")
    with ins2:
        if not prod_df.empty:
            top_prod = prod_df.iloc[0]
            render_insight_card("Top Product", str(top_prod["product_name"])[:28],
                                f"{format_currency(top_prod['revenue'])} revenue",
                                icon_name="package", tone="violet")
        else:
            render_insight_card("Top Product", "N/A", "No product data",
                                icon_name="package", tone="violet")
    with ins3:
        if not prod_df.empty and "cum_revenue_share_pct" in prod_df.columns:
            conc_80 = prod_df[prod_df["cum_revenue_share_pct"] <= 80].shape[0]
            total_products = prod_df.shape[0]
            pct_products = (conc_80 / total_products * 100) if total_products > 0 else 0
            render_insight_card("Revenue Concentration",
                                f"{pct_products:.0f}% of products",
                                f"drive up to 80% of total revenue",
                                icon_name="target", tone="amber")
        else:
            render_insight_card("Revenue Concentration", "N/A", "Pareto data unavailable",
                                icon_name="target", tone="amber")

    render_section_header("tag", "Category Performance",
                          "Revenue, profitability and share by category")

    if not cat_df.empty:
        c1, c2 = st.columns([5, 7])
        with c1:
            st.plotly_chart(render_category_bar(cat_df),
                            width="stretch", config={"displayModeBar": False})
        with c2:
            has_profit = "profit" in cat_df.columns
            fmt = {
                "category": "{}",
                "revenue": "£{:,.2f}",
                "revenue_share_pct": "{:.1f}%",
                "orders": "{:,.0f}",
                "aov": "£{:,.2f}",
            }
            if has_profit:
                fmt["profit"] = "£{:,.2f}"
                fmt["profit_margin_pct"] = "{:.1f}%"
            display = cat_df.rename(columns={
                "category": "Category", "revenue": "Revenue",
                "revenue_share_pct": "Share", "orders": "Orders",
                "aov": "AOV", "profit": "Profit",
                "profit_margin_pct": "Margin",
            })
            st.dataframe(display.style.format(fmt), width="stretch",
                         hide_index=True, height=360)
    else:
        render_empty_state("No category data", "The category dimension is unavailable in this dataset.",
                           icon_name="tag")

    render_section_header("package", "Top & Bottom Performing Products",
                          "Ranked product contribution by revenue")
    top_n = st.slider("Select Top / Bottom N Products", min_value=3, max_value=15, value=5)
    top_prods, bottom_prods = get_top_bottom_products(prod_df, top_n=top_n)

    col1, col2 = st.columns(2)
    with col1:
        if not top_prods.empty:
            st.plotly_chart(render_top_products_bar(top_prods),
                            width="stretch", config={"displayModeBar": False})
    with col2:
        if not bottom_prods.empty:
            st.plotly_chart(render_bottom_products_bar(bottom_prods),
                            width="stretch", config={"displayModeBar": False})

    render_section_header("chart-line", "Pareto Analysis",
                          "Cumulative revenue contribution curve (80/20 rule) — top 50 products")
    if not prod_df.empty:
        st.plotly_chart(render_pareto_chart(prod_df),
                        width="stretch", config={"displayModeBar": False})
    else:
        render_empty_state("No product data", "No products available in the current filters.",
                           icon_name="package")