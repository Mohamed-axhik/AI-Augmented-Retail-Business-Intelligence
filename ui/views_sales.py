"""Sales & Trend Analytics page."""
from __future__ import annotations

import streamlit as st
from src.analytics.sales import get_sales_over_time
from src.utils.formatting import format_currency, format_number, format_pct
from ui.cards import render_kpi_card
from ui.charts import render_aov_chart, render_orders_chart, render_sales_performance_chart
from ui.layout import render_empty_state, render_hero, render_section_header

FREQ_MAP = {"Daily": "D", "Weekly": "W", "Monthly": "MS", "Quarterly": "QS"}


def render_sales_analytics(df):
    """Renders the Sales Analytics page."""
    render_hero(
        "SALES ANALYTICS",
        "Sales Performance & Trends",
        "Granular time-series aggregations, period comparisons and velocity metrics.",
    )

    if df.empty:
        render_empty_state("No data available",
                           "The current filters exclude every row. Widen the date range or "
                           "clear the category / store filters in the sidebar.",
                           icon_name="filter")
        return

    # Top KPI row
    render_section_header("grid", "Sales KPIs",
                          "Key performance indicators for the selected period")
    total_revenue = df["revenue"].sum()
    total_orders = df["order_id"].nunique() if "order_id" in df.columns else len(df)
    total_units = int(df["quantity"].sum())
    aov = total_revenue / total_orders if total_orders > 0 else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Total Revenue", format_currency(total_revenue),
                        icon_name="banknote", icon_tone="blue")
    with k2:
        render_kpi_card("Total Orders", format_number(total_orders),
                        icon_name="cart", icon_tone="sky")
    with k3:
        render_kpi_card("Units Sold", format_number(total_units),
                        icon_name="package", icon_tone="teal")
    with k4:
        render_kpi_card("Average Order Value", format_currency(aov),
                        icon_name="receipt", icon_tone="violet")

    freq_label = st.radio("Aggregation Granularity", list(FREQ_MAP.keys()),
                          index=2, horizontal=True)
    freq_code = FREQ_MAP[freq_label]
    sales_resampled = get_sales_over_time(df, freq=freq_code)

    if sales_resampled.empty:
        render_empty_state("No time-series data found",
                           "The selected filters produced an empty time series.",
                           icon_name="chart-line")
        return

    st.plotly_chart(
        render_sales_performance_chart(sales_resampled, freq_label=freq_label, freq=freq_code),
        width="stretch", config={"displayModeBar": False},
    )

    render_section_header("cart", "Orders & Order Value Velocity",
                          f"Volume and basket-size trends at {freq_label.lower()} granularity")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(render_orders_chart(sales_resampled, freq_label),
                        width="stretch", config={"displayModeBar": False})
    with c2:
        st.plotly_chart(render_aov_chart(sales_resampled, freq_label),
                        width="stretch", config={"displayModeBar": False})

    render_section_header("layers", "Resampled Sales Data",
                          "Raw aggregated values behind the charts above")

    has_profit = "profit" in sales_resampled.columns
    fmt = {
        "revenue": "£{:,.2f}",
        "aov": "£{:,.2f}",
        "orders": "{:,.0f}",
    }
    if has_profit:
        fmt["profit"] = "£{:,.2f}"
    display = sales_resampled.rename(columns={
        "date": "Period", "revenue": "Revenue", "profit": "Profit",
        "orders": "Orders", "aov": "AOV", "quantity": "Units",
        "profit_margin_pct": "Margin %", "revenue_7d_ma": "7-Period MA",
        "revenue_30d_ma": "30-Period MA",
    })
    st.dataframe(display.style.format(fmt), width="stretch",
                 hide_index=True, height=360)