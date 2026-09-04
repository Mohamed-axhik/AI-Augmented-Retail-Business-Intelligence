"""Data observability components: quality metrics and validation checklist."""
from __future__ import annotations

import streamlit as st
from ui.icons import icon

STATUS_ICONS = {"passed": "circle-check", "warning": "circle-alert",
                "critical": "circle-x", "info": "info"}


def quality_tone(value: float, warn_above: float, crit_above: float,
                 higher_is_better: bool = False) -> str:
    """Maps a numeric quality metric to a tone bucket (passed/warning/critical)."""
    if higher_is_better:
        if value >= crit_above:
            return "passed"
        if value >= warn_above:
            return "warning"
        return "critical"
    if value > crit_above:
        return "critical"
    if value > warn_above:
        return "warning"
    return "passed"


def render_quality_metric(label: str, value: str, tone: str,
                          detail: str | None = None, icon_name: str = "circle-check") -> None:
    """Renders a single quality metric cell with a clear status indicator."""
    st.markdown(
        f'<div class="ri-kpi">'
        f'<div class="ri-kpi-top">'
        f'<div class="ri-kpi-label">{label}</div>'
        f'<div class="ri-kpi-icon {"green" if tone=="passed" else ("amber" if tone=="warning" else "red")}">'
        f'{icon(STATUS_ICONS.get(tone, "info"), 16)}'
        f'</div>'
        f'</div>'
        f'<div class="ri-kpi-value">{value}</div>'
        f'<div class="ri-kpi-delta {"up" if tone=="passed" else ("down" if tone=="critical" else "flat")}">'
        f'{icon(STATUS_ICONS.get(tone, "info"), 13)}'
        f'<span>{detail or tone.capitalize()}</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_checklist_item(icon_tone: str, title: str, detail: str,
                          return_html: bool = False) -> str | None:
    """Renders one validation checklist row with icon + text labels.

    When *return_html* is ``True`` the HTML string is returned instead of
    being injected via ``st.markdown``.  This avoids the split-tag
    rendering bug where open/close ``<div>`` pairs must live in the same
    ``st.markdown`` call.
    """
    html = (
        f'<div class="ri-check-item">'
        f'<div class="ri-check-icon {icon_tone}">{icon(STATUS_ICONS.get(icon_tone, "info"), 16)}</div>'
        f'<div class="ri-check-text"><b>{title}</b><span>{detail}</span></div>'
        f'</div>'
    )
    if return_html:
        return html
    st.markdown(html, unsafe_allow_html=True)