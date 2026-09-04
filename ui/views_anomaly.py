"""Anomaly Intelligence Center page."""
from __future__ import annotations

import streamlit as st
from src.anomaly.detector import detect_statistical_anomalies
from ui.anomaly_components import (
    build_anomaly_table,
    render_anomaly_detail_card,
    render_anomaly_kpis,
    summarize_anomalies,
)
from ui.charts import render_anomaly_distribution_chart, render_anomaly_timeline
from ui.layout import render_empty_state, render_hero, render_section_header


def render_anomaly_detection(df):
    """Renders the Anomaly Intelligence Center."""
    render_hero(
        "ANOMALY INTELLIGENCE",
        "Statistical Anomaly Detection",
        "Automated detection of unusual revenue spikes and dips, with root-cause driver breakdown.",
    )

    if df.empty:
        render_empty_state("No data available",
                           "The current filters exclude every row. Widen the date range or "
                           "clear the category / store filters in the sidebar.",
                           icon_name="filter")
        return

    st.caption("Anomaly sensitivity — lower thresholds flag smaller deviations")
    z_sens = st.slider("Z-Score Threshold", min_value=1.5, max_value=3.5,
                       value=2.2, step=0.1, key="z_threshold")

    daily_df, anomaly_records = detect_statistical_anomalies(df, z_threshold=z_sens)
    summary = summarize_anomalies(anomaly_records, z_threshold=z_sens)

    render_section_header("activity", "Detection Summary",
                          f"{len(df['date'].dt.date.unique()):,} days analyzed · Z ≥ {z_sens:.1f}")
    render_anomaly_kpis(summary)

    render_section_header("chart-line", "Revenue Baseline & Anomaly Timeline",
                          "Dashed line shows the expected baseline; diamonds mark statistically significant events")
    st.plotly_chart(render_anomaly_timeline(daily_df),
                    width="stretch", config={"displayModeBar": False})

    if anomaly_records:
        render_section_header("zap", "Anomaly Intensity",
                              "Z-score magnitude of every detected event — beyond ±3.0 is classified as extreme")

        c_intensity, c_insight = st.columns([6, 6])
        with c_intensity:
            st.plotly_chart(render_anomaly_distribution_chart(daily_df),
                            width="stretch", config={"displayModeBar": False})
        with c_insight:
            st.markdown(
                f'<div class="ri-panel" style="height:100%;">'
                f'<div class="ri-panel-title">{_icon("info")}<span>Interpretation Guide</span></div>'
                f'<div style="font-size:0.84rem;color:#C3CEDA;line-height:1.7;">'
                f'<b style="color:#EEF2F8;">Z-score</b> measures how far actual revenue sits from the '
                f'14-day expected baseline in standard deviations.<br><br>'
                f'<b style="color:#EEF2F8;">Spike (▲)</b> — revenue above baseline, frequently driven by '
                f'promotions, order bursts or category surges.<br>'
                f'<b style="color:#EEF2F8;">Dip (▼)</b> — revenue below baseline, often tied to stockouts, '
                f'service outages or seasonal troughs.<br><br>'
                f'<span style="color:#FBBF24;">Amber</span> markers = significant (2.2 ≤ |z| &lt; 3.0) · '
                f'<span style="color:#F87171;">red</span> markers = extreme (|z| ≥ 3.0).'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        render_section_header("layers", f"Detected Anomaly Events ({len(anomaly_records)})",
                              "Each event includes deviation magnitude, severity and probable drivers")
        table_df = build_anomaly_table(anomaly_records)
        st.dataframe(table_df, width="stretch", hide_index=True, height=360)

        render_section_header("target", "Anomaly Deep Dive",
                              "Full breakdown for the most significant detected events")
        for a in anomaly_records[:3]:
            render_anomaly_detail_card(a)
    else:
        render_empty_state(
            "No anomalies detected",
            f"Your selected period contains no statistically significant anomalies at the "
            f"{z_sens:.1f} Z-score threshold. Sales are within expected variance.",
            icon_name="circle-check",
        )


def _icon(name: str) -> str:
    from ui.icons import icon
    return icon(name, 15)