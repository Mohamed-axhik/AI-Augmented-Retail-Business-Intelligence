"""Anomaly Intelligence components: severity KPIs, detail cards, table."""
from __future__ import annotations

import pandas as pd
import streamlit as st
from src.utils.formatting import format_currency
from ui.cards import render_kpi_card
from ui.icons import icon

ANOMALY_SEVERITIES = {"extreme", "significant"}


def classify_anomaly(record: dict, z_threshold: float = 2.2) -> str:
    """Classifies an anomaly record as 'extreme' or 'significant'."""
    z = abs(record.get("z_score", 0) or 0)
    return "extreme" if z >= 3.0 else "significant"


def summarize_anomalies(records: list[dict], z_threshold: float = 2.2) -> dict:
    """Returns summary counts grouped by severity and direction."""
    total = len(records)
    extreme = sum(1 for r in records if classify_anomaly(r, z_threshold) == "extreme")
    significant = total - extreme
    spikes = sum(1 for r in records if r["deviation_pct"] > 0)
    dips = total - spikes
    latest = records[0]["date"] if records else "—"
    return {
        "total": total, "extreme": extreme, "significant": significant,
        "spikes": spikes, "dips": dips, "latest": latest,
    }


def render_anomaly_kpis(summary: dict) -> None:
    """Renders the anomaly intelligence KPI row."""
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Total Anomalies", f"{summary['total']}", icon_name="activity",
                        icon_tone="blue", sub="across selected period")
    with c2:
        render_kpi_card("Significant", f"{summary['significant']}", icon_name="alert-triangle",
                        icon_tone="amber", sub=f"{summary['spikes']} spikes · {summary['dips']} dips")
    with c3:
        render_kpi_card("Extreme", f"{summary['extreme']}", icon_name="zap",
                        icon_tone="red", sub="|z| ≥ 3.0")
    with c4:
        render_kpi_card("Latest Anomaly", str(summary["latest"]), icon_name="clock",
                        icon_tone="violet", sub="most recent detected date")


def render_anomaly_detail_card(record: dict) -> None:
    """Renders a rich anomaly detail card with drivers and full stats."""
    is_up = record["deviation_pct"] >= 0
    tone_cls = "up" if is_up else "down"
    dev_color = C_DANGER if not is_up else C_WARNING
    z = abs(record["z_score"])
    badge = "Extreme" if z >= 3.0 else "Significant"
    badge_tone = "critical" if z >= 3.0 else "warning"

    drivers_html = ""
    if record.get("possible_drivers"):
        items = "".join(
            f'<span class="ri-anomaly-driver">{icon("git-branch", 11)}<span>{d}</span></span>'
            for d in record["possible_drivers"]
        )
        drivers_html = f'<div class="ri-anomaly-drivers">{items}</div>'

    drivers_display = drivers_html or (
        '<span style="font-size:0.78rem;color:#8B99B5;">No driver breakdown available.</span>'
    )
    st.markdown(
        f'<div class="ri-anomaly">'
        f'<div class="ri-anomaly-head">'
        f'<div class="ri-anomaly-title {tone_cls}">'
        f'{icon("diamond", 16)}'
        f'<span>{"SIGNIFICANT" if badge == "Significant" else "EXTREME"} {"REVENUE SPIKE" if is_up else "REVENUE DIP"}</span>'
        f'</div>'
        f'<span class="ri-badge {badge_tone}">{icon("zap" if badge=="Extreme" else "alert-triangle", 12)}<span>{badge}</span></span>'
        f'</div>'
        f'<div class="ri-anomaly-grid">'
        f'<div class="ri-anomaly-stat">'
        f'<div class="ri-anomaly-k">Date</div>'
        f'<div class="ri-anomaly-v" style="font-size:0.82rem;">{record.get("date", "—")}</div>'
        f'</div>'
        f'<div class="ri-anomaly-stat">'
        f'<div class="ri-anomaly-k">Z-Score</div>'
        f'<div class="ri-anomaly-v" style="color:{dev_color}">{record["z_score"]:+.2f}</div>'
        f'</div>'
        f'<div class="ri-anomaly-stat">'
        f'<div class="ri-anomaly-k">Severity</div>'
        f'<div class="ri-anomaly-v" style="font-size:0.82rem;">{badge}</div>'
        f'</div>'
        f'</div>'
        f'<div class="ri-anomaly-grid">'
        f'<div class="ri-anomaly-stat">'
        f'<div class="ri-anomaly-k">Actual Revenue</div>'
        f'<div class="ri-anomaly-v">{format_currency(record["actual_revenue"])}</div>'
        f'</div>'
        f'<div class="ri-anomaly-stat">'
        f'<div class="ri-anomaly-k">Expected Baseline</div>'
        f'<div class="ri-anomaly-v">{format_currency(record["expected_revenue"])}</div>'
        f'</div>'
        f'<div class="ri-anomaly-stat">'
        f'<div class="ri-anomaly-k">Deviation</div>'
        f'<div class="ri-anomaly-v" style="color:{dev_color}">{record["deviation_pct"]:+.1f}%</div>'
        f'</div>'
        f'</div>'
        f'<div class="ri-anomaly-stat" style="padding:7px 10px;">'
        f'<div class="ri-anomaly-k" style="margin-bottom:4px;">Contributing Factors</div>'
        f'{drivers_display}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


C_DANGER = "#F87171"
C_WARNING = "#FBBF24"


def build_anomaly_table(records: list[dict]) -> pd.DataFrame:
    """Builds a display-ready anomaly table."""
    rows = []
    for r in records:
        rows.append({
            "Date": r["date"],
            "Type": "Spike" if r["deviation_pct"] >= 0 else "Dip",
            "Severity": "Extreme" if abs(r["z_score"]) >= 3.0 else "Significant",
            "Actual": format_currency(r["actual_revenue"]),
            "Expected": format_currency(r["expected_revenue"]),
            "Deviation": f"{r['deviation_pct']:+.1f}%",
            "Z-Score": f"{r['z_score']:+.2f}",
        })
    return pd.DataFrame(rows)