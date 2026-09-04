"""Store & Market Performance page."""
from __future__ import annotations

import streamlit as st
from src.analytics.stores import get_store_performance
from ui.charts import render_market_bar, render_region_donut, render_store_bar
from ui.layout import render_empty_state, render_hero, render_section_header


def render_store_performance(df):
    """Renders the Store / Market & Regional Performance page."""
    render_hero(
        "MARKET INTELLIGENCE",
        "Store & Market Performance",
        "Store rankings, country-level revenue share and location profitability.",
    )

    if df.empty:
        render_empty_state("No data available",
                           "The current filters exclude every row. Widen the date range or "
                           "clear the category / store filters in the sidebar.",
                           icon_name="filter")
        return

    store_df, region_df = get_store_performance(df)

    if region_df.empty:
        render_empty_state("No location data", "No store or region dimension was detected in this dataset.",
                           icon_name="store")
        return

    is_market_mode = len(store_df) <= 1 and len(region_df) > 1

    if is_market_mode:
        render_section_header("store", "Country / Market Distribution",
                              "Store dimension unavailable — showing country-level market analysis")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(render_region_donut(region_df, "Revenue by Country"),
                            width="stretch", config={"displayModeBar": False})
        with c2:
            st.plotly_chart(render_market_bar(region_df),
                            width="stretch", config={"displayModeBar": False})

        render_section_header("layers", "Country / Market Performance Table",
                              "Ranked market metrics across all countries")
        fmt = {
            "region": "{}",
            "revenue": "£{:,.2f}",
            "revenue_share_pct": "{:.1f}%",
            "orders": "{:,.0f}",
            "aov": "£{:,.2f}",
        }
        if "customers" in region_df.columns:
            fmt["customers"] = "{:,.0f}"
        display = region_df.copy()
        display["aov"] = (display["revenue"] / display["orders"]).round(2)
        display = display.rename(columns={
            "region": "Country", "revenue": "Revenue", "revenue_share_pct": "Share",
            "orders": "Orders", "aov": "AOV", "customers": "Customers",
        })
        st.dataframe(display.style.format(fmt), width="stretch", hide_index=True, height=400)
        return

    render_section_header("store", "Regional & Store Distribution",
                          "Revenue share by region and ranked store performance")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(render_region_donut(region_df, "Regional Revenue Distribution"),
                        width="stretch", config={"displayModeBar": False})
    with c2:
        st.plotly_chart(render_store_bar(store_df),
                        width="stretch", config={"displayModeBar": False})

    render_section_header("layers", "Store Performance Detail Table",
                          "Ranked store metrics across all locations")
    has_profit = "profit" in store_df.columns
    fmt = {
        "store": "{}",
        "region": "{}",
        "revenue": "£{:,.2f}",
        "revenue_share_pct": "{:.1f}%",
        "orders": "{:,.0f}",
        "aov": "£{:,.2f}",
    }
    if has_profit:
        fmt["profit"] = "£{:,.2f}"
        fmt["profit_margin_pct"] = "{:.1f}%"
    display = store_df.rename(columns={
        "store": "Store", "region": "Region", "revenue": "Revenue",
        "revenue_share_pct": "Share", "orders": "Orders", "aov": "AOV",
        "profit": "Profit", "profit_margin_pct": "Margin",
    })
    st.dataframe(display.style.format(fmt), width="stretch", hide_index=True, height=400)