"""Executive Overview — the flagship dashboard page."""
from __future__ import annotations

import streamlit as st
from src.analytics.categories import get_category_performance
from src.analytics.inventory import calculate_inventory_kpis
from src.analytics.kpis import calculate_executive_kpis
from src.analytics.sales import get_sales_over_time
from src.utils.formatting import format_currency, format_number, format_pct
from ui.cards import render_insight_card, render_kpi_card
from ui.charts import render_category_donut, render_revenue_trend_chart
from ui.layout import render_empty_state, render_hero, render_section_header
from ui.theme import CH


def _metadata(df) -> list:
    min_d = df["date"].min().strftime("%d %b %Y")
    max_d = df["date"].max().strftime("%d %b %Y")
    return [
        ("database", "Dataset", "Online Retail II"),
        ("calendar", "Period", f"{min_d} — {max_d}"),
        ("layers", "Records", f"{len(df):,}"),
        ("target", "Granularity", "Daily"),
    ]


def render_executive_overview(df):
    """Renders the Executive Overview page."""
    render_hero(
        "RETAIL PERFORMANCE",
        "Business Intelligence Overview",
        "Understand revenue, customers, products and anomalies from your retail data.",
        metadata=_metadata(df),
    )

    # Validate required columns exist
    required_cols = {"revenue", "quantity", "date"}
    missing = required_cols - set(df.columns)
    if missing:
        render_empty_state(
            "Missing required columns",
            f"The dataset is missing required columns: {', '.join(sorted(missing))}. "
            "Please update the schema mapping on the Data Quality page.",
            icon_name="alert-triangle",
        )
        return

    if df.empty:
        render_empty_state(
            "No data available",
            "The current filters exclude every row. Widen the date range or clear the "
            "category / store filters in the sidebar.",
            icon_name="filter",
        )
        return

    kpis = calculate_executive_kpis(df)

    render_section_header("grid", "Core Business KPIs",
                          "Headline metrics across revenue, orders, customers and growth")

    row1 = st.columns(4)
    with row1[0]:
        mom = kpis["mom_growth_pct"]
        render_kpi_card(
            "Total Revenue", format_currency(kpis["total_revenue"]),
            icon_name="banknote", icon_tone="blue",
            delta=f"{mom:+.1f}% MoM" if mom is not None else None,
            value_unit="", sub=f"{format_number(kpis['total_orders'])} orders in period",
        )
    with row1[1]:
        if kpis["has_profit_data"]:
            render_kpi_card("Total Profit", format_currency(kpis["total_profit"]),
                            icon_name="coins", icon_tone="teal",
                            sub="gross profit for the period")
        else:
            render_kpi_card("Total Profit", "N/A", icon_name="coins", icon_tone="teal",
                            delta="No cost field mapped", delta_tone="off")
    with row1[2]:
        if kpis["has_profit_data"]:
            render_kpi_card("Profit Margin", format_pct(kpis["profit_margin_pct"], include_sign=False),
                            icon_name="percent", icon_tone="violet",
                            sub="profit ÷ revenue")
        else:
            render_kpi_card("Profit Margin", "N/A", icon_name="percent", icon_tone="violet",
                            delta="Requires cost data", delta_tone="off")
    with row1[3]:
        render_kpi_card("Average Order Value", format_currency(kpis["aov"]),
                        icon_name="receipt", icon_tone="sky",
                        sub="revenue ÷ orders")

    row2 = st.columns(4)
    with row2[0]:
        render_kpi_card("Total Orders", format_number(kpis["total_orders"]),
                        icon_name="cart", icon_tone="sky")
    with row2[1]:
        render_kpi_card("Units Sold", format_number(kpis["units_sold"]),
                        icon_name="package", icon_tone="teal")
    with row2[2]:
        render_kpi_card("MoM Growth",
                        format_pct(kpis["mom_growth_pct"]) if kpis["mom_growth_pct"] is not None else "N/A",
                        icon_name="trending-up", icon_tone="green")
    with row2[3]:
        render_kpi_card("YoY Growth",
                        format_pct(kpis["yoy_growth_pct"]) if kpis["yoy_growth_pct"] is not None else "N/A",
                        icon_name="calendar", icon_tone="violet",
                        delta="Needs 1yr of data" if kpis["yoy_growth_pct"] is None else None,
                        delta_tone="off" if kpis["yoy_growth_pct"] is None else "auto")

    row3 = st.columns(4)
    with row3[0]:
        if kpis["has_customer_data"]:
            render_kpi_card("Unique Customers", format_number(kpis["total_customers"]),
                            icon_name="users", icon_tone="blue")
        else:
            render_kpi_card("Unique Customers", "N/A", icon_name="users", icon_tone="blue",
                            delta="No customer column", delta_tone="off")
    with row3[1]:
        render_kpi_card("Revenue per Customer", format_currency(kpis["revenue_per_customer"]),
                        icon_name="banknote", icon_tone="amber")
    with row3[2]:
        render_kpi_card("Units per Order", f"{kpis['avg_items_per_order']:.1f}",
                        icon_name="box", icon_tone="teal",
                        sub="total units incl. bulk lines ÷ orders")
    with row3[3]:
        render_kpi_card(
            "Return Rate", f"{kpis['return_rate_pct']:.1f}%",
            icon_name="gift", icon_tone="red",
            delta=f"{format_number(abs(kpis['returned_units']))} units returned",
            delta_tone="inverse" if kpis["return_rate_pct"] > 0 else "normal",
        )

    render_section_header("chart-line", "Revenue & Category Analysis",
                          "Daily revenue trajectory with a 7-day average, and the category contribution mix")

    sales_daily = get_sales_over_time(df, freq="D")
    cat_df = get_category_performance(df)

    c_left, c_right = st.columns([7, 5])
    with c_left:
        st.plotly_chart(render_revenue_trend_chart(sales_daily, freq="D"),
                        width="stretch", config={"displayModeBar": False})
    with c_right:
        if not cat_df.empty:
            st.plotly_chart(render_category_donut(cat_df, height=CH.PRIMARY),
                            width="stretch",
                            config={"displayModeBar": False})
        else:
            render_empty_state("No category data", "Category dimension is unavailable in this dataset.",
                               icon_name="tag")

    # Business insights row
    render_section_header("sparkles", "Business Insights",
                          "Automated signals derived from deterministic analytics")

    ins1, ins2, ins3 = st.columns(3)
    with ins1:
        if kpis["has_customer_data"] and kpis["total_customers"] > 0:
            repeat_pct = kpis.get("return_rate_pct", 0)
            render_insight_card(
                "Return Rate",
                f"{kpis['return_rate_pct']:.1f}%",
                "Units returned as % of gross revenue",
                icon_name="gift",
                tone="red" if kpis["return_rate_pct"] > 10 else ("amber" if kpis["return_rate_pct"] > 5 else "green"),
            )
        else:
            render_insight_card("Customer Coverage", "No customer ID", "Customer analytics require customer column",
                                icon_name="users", tone="amber")
    with ins2:
        if cat_df.shape[0] > 0:
            top_cat = cat_df.iloc[0]
            render_insight_card(
                "Top Category",
                top_cat["category"],
                f"{top_cat['revenue_share_pct']:.1f}% of total revenue",
                icon_name="tag", tone="blue",
            )
        else:
            render_insight_card("Top Category", "N/A", "No category data available",
                                icon_name="tag", tone="blue")
    with ins3:
        render_insight_card(
            "Revenue per Customer",
            format_currency(kpis["revenue_per_customer"]),
            f"Across {format_number(kpis['total_customers'])} unique customers",
            icon_name="banknote", tone="violet",
        )

    inv_kpis = calculate_inventory_kpis(df)
    if inv_kpis.get("available"):
        render_section_header("box", "Inventory Intelligence",
                              "Stock position, valuation, turnover and stockout risk exposure")
        i_row = st.columns(4)
        with i_row[0]:
            render_kpi_card("Stock Units", format_number(inv_kpis["total_stock_units"]),
                            icon_name="box", icon_tone="sky")
        with i_row[1]:
            render_kpi_card("Inventory Valuation", format_currency(inv_kpis["total_inventory_valuation"]),
                            icon_name="coins", icon_tone="amber")
        with i_row[2]:
            if inv_kpis.get("inventory_turnover") is not None:
                render_kpi_card("Inventory Turnover", f"{inv_kpis['inventory_turnover']}x",
                                icon_name="refresh-cw", icon_tone="teal")
            else:
                render_kpi_card("Inventory Turnover", "N/A", icon_name="refresh-cw", icon_tone="teal",
                                delta="No COGS data", delta_tone="off")
        with i_row[3]:
            render_kpi_card(
                "Stockout Risk Items", format_number(inv_kpis["stockout_risk_count"]),
                icon_name="alert-triangle",
                icon_tone="red" if inv_kpis["stockout_risk_count"] else "green",
                delta="At risk" if inv_kpis["stockout_risk_count"] else "Healthy",
                delta_tone="inverse" if inv_kpis["stockout_risk_count"] else "normal",
            )