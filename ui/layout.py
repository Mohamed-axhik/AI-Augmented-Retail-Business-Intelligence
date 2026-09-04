"""Page-level layout primitives: app header, hero, section headers, empty states."""
from __future__ import annotations

import streamlit as st
from ui.icons import icon


def render_app_header(dataset_name: str = "Online Retail II", records: int = 0,
                      quality_score: int = 0) -> None:
    """Renders the sticky premium application header with live status badges."""
    meta = st.session_state.get("dataset_meta", {})
    total_rows = meta.get("total_rows", records)
    filtered_rows = meta.get("filtered_rows", records)
    q_score = meta.get("quality_score", quality_score)
    q_status = meta.get("quality_status", "Unknown")
    date_min = meta.get("date_min")
    date_max = meta.get("date_max")

    # Period text
    period = ""
    if date_min is not None and date_max is not None:
        try:
            period = f"{date_min.strftime('%d %b %Y')} – {date_max.strftime('%d %b %Y')}"
        except Exception:
            period = ""

    # Quality pill color
    if q_score >= 80:
        q_color = "#34D399"
        q_status_text = "Healthy"
    elif q_score >= 60:
        q_color = "#FBBF24"
        q_status_text = "Fair"
    else:
        q_color = "#F87171"
        q_status_text = "Degraded"

    st.markdown(
        f'<div class="ri-app-header">'
        f'<div class="ri-app-header-left">'
        f'<div class="ri-brand-mark">{icon("zap", 20)}</div>'
        f'<div>'
        f'<div class="ri-header-brand">Retail Intelligence</div>'
        f'<div class="ri-header-tag">AI-Augmented Business Performance</div>'
        f'</div>'
        f'</div>'
        f'<div class="ri-header-right">'
        f'<span class="ri-pill live"><span class="ri-dot"></span>Data Connected</span>'
        f'<span class="ri-pill"><span class="ri-dot" style="background:#4C8DFF"></span>{total_rows:,} records</span>'
        f'<span class="ri-pill"><span class="ri-dot" style="background:{q_color}"></span>Quality {q_score}/100 · {q_status_text}</span>'
        + (f'<span class="ri-pill"><span class="ri-dot" style="background:#8B5CF6"></span>{period}</span>' if period else '')
        + '</div></div>',
        unsafe_allow_html=True,
    )


def render_hero(eyebrow: str, title: str, subtitle: str,
                metadata: list[tuple[str, str]] | None = None) -> None:
    """Renders the hero / page masthead with subtle depth and grid."""
    meta_html = ""
    if metadata:
        chips = "".join(
            f'<span class="ri-chip">{icon(ic, 13)}<span>{label}: <b>{value}</b></span></span>'
            for ic, label, value in metadata
        )
        meta_html = f'<div class="ri-hero-meta">{chips}</div>'
    st.markdown(
        f'<div class="ri-hero">'
        f'<div class="ri-hero-grid"></div>'
        f'<div class="ri-hero-inner">'
        f'<div class="ri-hero-eyebrow">{icon("sparkles", 14)}<span>{eyebrow}</span></div>'
        f'<div class="ri-hero-title">{title}</div>'
        f'<div class="ri-hero-sub">{subtitle}</div>'
        f'{meta_html}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_section_header(icon_name: str, title: str, subtitle: str | None = None) -> None:
    """Renders a compact section heading with icon and optional subtitle."""
    sub_html = f'<div class="ri-section-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="ri-section">'
        f'<div class="ri-section-icon">{icon(icon_name, 15)}</div>'
        f'<div class="ri-section-title">{title}</div>'
        f'</div>'
        f'{sub_html}',
        unsafe_allow_html=True,
    )


def render_panel_title(icon_name: str, title: str) -> None:
    """Renders the title row inside a card/panel."""
    st.markdown(
        f'<div class="ri-panel-title">{icon(icon_name, 15)}<span>{title}</span></div>',
        unsafe_allow_html=True,
    )


def render_empty_state(title: str, message: str, icon_name: str = "search") -> None:
    """Renders a friendly empty state instead of a blank chart / error box."""
    st.markdown(
        f'<div class="ri-empty">'
        f'<div class="ri-empty-icon">{icon(icon_name, 26)}</div>'
        f'<div class="ri-empty-title">{title}</div>'
        f'<div class="ri-empty-msg">{message}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_metric_spacer() -> None:
    """Adds a small vertical spacer for metric alignment rows."""
    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)


def render_footer() -> None:
    """Renders the subtle application footer."""
    st.markdown(
        f'<div class="ri-footer">'
        f'<span>Retail Intelligence Platform</span>'
        f'<span style="opacity:0.5">•</span>'
        f'{icon("box", 13)}'
        f'<span>Deterministic Analytics · Statistical Anomaly Engine · LLM Analyst</span>'
        f'<span style="opacity:0.5">•</span>'
        f'<span>Streamlit · Pandas · DuckDB · Plotly</span>'
        f'</div>',
        unsafe_allow_html=True,
    )