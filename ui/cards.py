"""Reusable data cards: KPI metrics, status badges, score gauge."""
from __future__ import annotations

import re
from typing import Optional

import streamlit as st
from ui.icons import icon

_ICON_CLASSES = {
    "green": "green", "success": "green",
    "teal": "teal", "sky": "sky", "blue": "",
    "violet": "violet", "purple": "violet",
    "amber": "amber", "warning": "amber",
    "red": "red", "danger": "red",
}


def render_kpi_card(
    label: str,
    value: str,
    icon_name: str = "chart-line",
    delta: Optional[str] = None,
    delta_tone: str = "auto",      # auto | positive | negative | inverse | off | flat
    sub: Optional[str] = None,
    value_unit: str = "",
    icon_tone: str = "blue",
) -> None:
    """Renders a premium KPI card with label, large value, delta and icon."""
    icon_cls = _ICON_CLASSES.get(icon_tone, "")
    icon_html = f'<div class="ri-kpi-icon {icon_cls}">{icon(icon_name, 16)}</div>'

    delta_html = ""
    if delta:
        s = str(delta).strip()
        is_negative = s.startswith("-")
        has_numeric = bool(re.match(r"^[+-]?\s*\d", s))

        if has_numeric and delta_tone != "off":
            if delta_tone == "inverse":
                up_cls, down_cls = "down", "up"
            elif delta_tone == "positive":
                up_cls, down_cls = "up", "up"
            elif delta_tone == "negative":
                up_cls, down_cls = "down", "down"
            else:
                up_cls, down_cls = "up", "down"
            arrow = "arrow-down-right" if is_negative else "arrow-up-right"
            delta_html = f'<div class="ri-kpi-delta {down_cls if is_negative else up_cls}">{icon(arrow, 13)}<span>{s}</span></div>'
        else:
            delta_html = f'<div class="ri-kpi-delta flat">{icon("activity", 13)}<span>{s}</span></div>'

    unit_html = f'<span class="ri-kpi-unit">{value_unit}</span>' if value_unit else ""
    sub_html = f'<div class="ri-kpi-sub">{sub}</div>' if sub else ""

    st.markdown(
        f'<div class="ri-kpi">'
        f'<div class="ri-kpi-top">'
        f'<div class="ri-kpi-label">{label}</div>'
        f'{icon_html}'
        f'</div>'
        f'<div class="ri-kpi-value">{value}{unit_html}</div>'
        f'{delta_html}'
        f'{sub_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_status_badge(status_str: str, tone: Optional[str] = None) -> None:
    """Renders a status pill with icon + text label (never color-only)."""
    lowered = (status_str or "").lower()
    if tone:
        tone = tone.lower()
    elif "passed" in lowered or "good" in lowered or "healthy" in lowered or "\u2705" in lowered:
        tone = "passed"
    elif "warning" in lowered or "warn" in lowered:
        tone = "warning"
    elif "critical" in lowered or "failed" in lowered or "error" in lowered:
        tone = "critical"
    else:
        tone = "info"

    icons = {"passed": "circle-check", "warning": "circle-alert", "critical": "circle-x", "info": "info"}
    st.markdown(
        f'<span class="ri-badge {tone}">{icon(icons.get(tone, "info"), 12)}<span>{status_str}</span></span>',
        unsafe_allow_html=True,
    )


def render_score_gauge(score: float, max_score: float = 100.0,
                       label: str = "Data Quality Score",
                       status_text: Optional[str] = None) -> None:
    """Renders a circular progress gauge for a quality score."""
    pct = min(max(float(score) / float(max_score), 0.0), 1.0) * 100
    color = "#34D399" if pct >= 80 else ("#FBBF24" if pct >= 60 else "#F87171")
    status_html = f'<div class="ri-score-status" style="color:{color}">{status_text}</div>' if status_text else ""
    st.markdown(
        f'<div class="ri-score-card">'
        f'<div class="ri-score-ring" style="background: conic-gradient({color} {pct}%, rgba(148,163,184,0.10) {pct}%);">'
        f'<div class="ri-score-inner">'
        f'<div class="ri-score-value">{score:.0f}</div>'
        f'<div class="ri-score-max">/ {max_score:.0f}</div>'
        f'</div>'
        f'</div>'
        f'<div class="ri-score-label">{label}</div>'
        f'{status_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_panel(children_html: str, title: str | None = None, icon_name: str | None = None) -> None:
    """Renders a generic card/panel with optional title bar."""
    title_html = f'<div class="ri-panel-title">{icon(icon_name or "box", 15)}<span>{title}</span></div>' if title else ""
    st.markdown(f'<div class="ri-panel">{title_html}{children_html}</div>', unsafe_allow_html=True)


def render_insight_card(label: str, value: str, note: str, icon_name: str = "info",
                        tone: str = "blue") -> None:
    """Renders a compact business-insight card with icon, label, value, and note."""
    tone_cls = {"green": "green", "amber": "amber", "red": "red",
                "blue": "blue", "violet": "violet"}.get(tone, "blue")
    st.markdown(
        f'<div class="ri-insight">'
        f'<div class="ri-insight-icon {tone_cls}">{icon(icon_name, 17)}</div>'
        f'<div class="ri-insight-body">'
        f'<div class="ri-insight-label">{label}</div>'
        f'<div class="ri-insight-value">{value}</div>'
        f'<div class="ri-insight-note">{note}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )