"""Customer Analytics page."""
from __future__ import annotations

import streamlit as st
from src.analytics.customers import (
    calculate_customer_kpis,
    get_customer_acquisition_trend,
    get_customer_revenue_distribution,
    get_customer_segments,
    get_top_customers,
)
from src.utils.formatting import format_currency, format_number
from ui.cards import render_insight_card, render_kpi_card
from ui.charts import (
    render_customer_acquisition_chart,
    render_customer_concentration_chart,
    render_customer_segments_donut,
    render_top_customers_bar,
)
from ui.layout import render_empty_state, render_hero, render_section_header


def render_customer_analytics(df):
    """Renders the Customer Analytics page."""
    render_hero(
        "CUSTOMER INTELLIGENCE",
        "Customer Analytics",
        "Customer base growth, loyalty segmentation and revenue concentration.",
    )

    if df.empty:
        render_empty_state("No data available",
                           "The current filters exclude every row. Widen the date range or "
                           "clear the category / store filters in the sidebar.",
                           icon_name="filter")
        return

    kpis = calculate_customer_kpis(df)
    if not kpis["available"]:
        render_empty_state("Customer analytics unavailable", kpis["reason"], icon_name="users")
        return

    cust_agg = kpis["customer_df"]

    render_section_header("users", "Customer Base KPIs",
                          "Acquisition, loyalty and value metrics for the selected period")

    row1 = st.columns(4)
    with row1[0]:
        render_kpi_card("Total Customers", format_number(kpis["total_customers"]),
                        icon_name="users", icon_tone="blue")
    with row1[1]:
        render_kpi_card("New Customers · Latest Month", format_number(kpis["new_customers"]),
                        icon_name="star", icon_tone="teal")
    with row1[2]:
        render_kpi_card("Repeat Purchase Rate", f"{kpis['repeat_rate_pct']:.1f}%",
                        icon_name="refresh-cw", icon_tone="sky",
                        delta=f"{kpis['repeat_customers']} repeat buyers", delta_tone="flat")
    with row1[3]:
        render_kpi_card("Avg Revenue per Customer", format_currency(kpis["avg_revenue_per_customer"]),
                        icon_name="banknote", icon_tone="amber")

    row2 = st.columns(4)
    with row2[0]:
        render_kpi_card("Avg Orders per Customer", f"{kpis['avg_orders_per_customer']:.2f}",
                        icon_name="receipt", icon_tone="sky")
    with row2[1]:
        render_kpi_card("Avg Items per Customer", f"{kpis['avg_items_per_customer']:.2f}",
                        icon_name="package", icon_tone="teal")
    with row2[2]:
        render_kpi_card("Top Customer Share", f"{kpis['top_customer_share_pct']:.1f}%",
                        icon_name="crown", icon_tone="violet")
    with row2[3]:
        render_kpi_card("Unattributed Revenue", f"{kpis['unattributed_revenue_pct']:.1f}%",
                        icon_name="circle-alert", icon_tone="amber",
                        delta="No customer ID on rows", delta_tone="flat")

    # Customer insights
    render_section_header("sparkles", "Customer Insights",
                          "Automated signals from customer analytics")

    ins1, ins2, ins3 = st.columns(3)
    with ins1:
        repeat_rate = kpis["repeat_rate_pct"]
        render_insight_card(
            "Customer Retention",
            f"{repeat_rate:.1f}%",
            "Repeat purchase rate across all customers",
            icon_name="refresh-cw",
            tone="green" if repeat_rate > 30 else ("amber" if repeat_rate > 15 else "red"),
        )
    with ins2:
        render_insight_card(
            "Revenue Concentration",
            f"{kpis['top_customer_share_pct']:.1f}%",
            f"Share held by single highest-value customer",
            icon_name="crown",
            tone="amber" if kpis["top_customer_share_pct"] > 10 else "green",
        )
    with ins3:
        render_insight_card(
            "Unattributed Revenue",
            f"{kpis['unattributed_revenue_pct']:.1f}%",
            "Revenue without a linked customer ID",
            icon_name="circle-alert",
            tone="red" if kpis["unattributed_revenue_pct"] > 20 else ("amber" if kpis["unattributed_revenue_pct"] > 5 else "green"),
        )

    render_section_header("trending-up", "Customer Acquisition & Loyalty Mix",
                          "New customer inflow over time and the loyalty segment distribution")
    trend_df = get_customer_acquisition_trend(df)
    seg_df = get_customer_segments(cust_agg)

    c1, c2 = st.columns([7, 5])
    with c1:
        if not trend_df.empty:
            st.plotly_chart(render_customer_acquisition_chart(trend_df),
                            width="stretch", config={"displayModeBar": False})
        else:
            render_empty_state("No acquisition trend", "No customer identifier data in the period.",
                               icon_name="chart-line")
    with c2:
        if not seg_df.empty:
            st.plotly_chart(render_customer_segments_donut(seg_df),
                            width="stretch", config={"displayModeBar": False})
        else:
            render_empty_state("No segments", "Unable to build loyalty segments.",
                               icon_name="users")

    render_section_header("crown", "Top Customers & Revenue Concentration",
                          "Highest-value customers and the share of revenue they drive")
    top_n = st.slider("Select Top N Customers", min_value=5, max_value=30, value=10)
    top_customers = get_top_customers(cust_agg, top_n=top_n)
    conc_df = get_customer_revenue_distribution(cust_agg, top_n=top_n)

    c3, c4 = st.columns(2)
    with c3:
        if not top_customers.empty:
            st.plotly_chart(render_top_customers_bar(top_customers),
                            width="stretch", config={"displayModeBar": False})
    with c4:
        if not conc_df.empty:
            st.plotly_chart(render_customer_concentration_chart(conc_df),
                            width="stretch", config={"displayModeBar": False})

    render_section_header("layers", "Top Customer Detail Table",
                          "Ranked metrics for the highest-value buyers")
    if not top_customers.empty:
        detail = top_customers.copy()
        detail = detail.rename(columns={
            "customer_id": "Customer ID", "revenue": "Revenue (£)",
            "orders": "Orders", "items": "Items",
            "first_order": "First Order", "region": "Country",
        })
        detail["Revenue (£)"] = detail["Revenue (£)"].map(lambda v: f"£{v:,.2f}")
        detail["First Order"] = detail["First Order"].dt.strftime("%d %b %Y")
        st.dataframe(detail, width="stretch", hide_index=True, height=360)