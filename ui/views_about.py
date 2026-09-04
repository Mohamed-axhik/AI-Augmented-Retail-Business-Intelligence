"""About & System Architecture page."""
from __future__ import annotations

import streamlit as st
from ui.icons import icon
from ui.layout import render_hero, render_section_header

_LAYERS = [
    ("database", "1 · Data Intelligence Layer", "Can I trust this dataset?",
     ["Upload CSV / XLSX", "Schema auto-detection", "Quality validation (0–100)", "Cleaning & canonical transform"]),
    ("chart-line", "2 · Business Intelligence Layer", "What is happening?",
     ["Executive KPIs", "DuckDB aggregations", "Statistical anomaly detector (Z-Score)"]),
    ("sparkles", "3 · AI Intelligence Layer", "Why is it happening?",
     ["Natural-language question", "Analytics engine evidence", "LLM explanation (OpenAI / Gemini)"]),
]

_PRINCIPLES = [
    ("scale", "Deterministic Financial Math",
     "KPIs (Revenue = Qty × Price, Profit = Revenue − COGS) are computed with 100% precision by "
     "Pandas & DuckDB. The LLM never calculates raw numbers."),
    ("refresh-cw", "Graceful Schema Degradation",
     "Accepts custom CSV/Excel uploads. Missing fields (e.g. no cost or inventory column) safely "
     "disable dependent KPIs without breaking dashboard views."),
    ("zap", "Offline Resilience",
     "Runs seamlessly on a built-in deterministic NLG engine when no API key is provided, while "
     "supporting OpenAI and Gemini for advanced natural-language reasoning."),
]


def render_about_page():
    """Renders the About & System Architecture page."""
    render_hero(
        "PLATFORM",
        "About the Retail Intelligence Platform",
        "Architecture principles, technology stack and the canonical schema reference.",
    )

    render_section_header("layers", "Three Intelligence Layers", "End-to-end pipeline design")
    cols = st.columns(3)
    for col, (ic, title, question, steps) in zip(cols, _LAYERS):
        with col:
            items = "".join(
                f'<div style="display:flex;align-items:center;gap:8px;padding:5px 0;">'
                f'<span style="color:#4C8DFF;font-size:0.8rem;">•</span>'
                f'<span style="color:#C3CEDA;font-size:0.84rem;">{s}</span></div>'
                for s in steps
            )
            st.markdown(
                f'<div class="ri-panel" style="height:100%;">'
                f'<div class="ri-panel-title">{icon(ic, 15)}<span>{title}</span></div>'
                f'<div style="font-size:0.8rem;color:#8B99B5;font-style:italic;margin-bottom:8px;">{question}</div>'
                f'{items}'
                f'</div>',
                unsafe_allow_html=True,
            )

    render_section_header("target", "Key Engineering Principles")
    cols = st.columns(3)
    for col, (ic, title, desc) in zip(cols, _PRINCIPLES):
        with col:
            st.markdown(
                f'<div class="ri-panel" style="height:100%;">'
                f'<div class="ri-panel-title">{icon(ic, 15)}<span>{title}</span></div>'
                f'<div style="font-size:0.84rem;color:#C3CEDA;line-height:1.65;">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    render_section_header("grid", "Canonical Internal Schema Reference")
    rows = "".join(
        f"<tr><td><code>{field}</code></td><td>{info['description']}</td><td>{info['type']}</td>"
        f"<td>{'<b style=color:#34D399>Yes</b>' if info['required'] else 'No'}</td></tr>"
        for field, info in _SCHEMA_ROWS()
    )
    st.markdown(
        f'<div class="ri-panel" style="padding:0;overflow:hidden;">'
        f'<table style="width:100%;border-collapse:collapse;font-size:0.82rem;">'
        f'<thead>'
        f'<tr style="background:rgba(10,17,32,0.6);text-align:left;">'
        f'<th style="padding:10px 14px;color:#8B99B5;font-weight:600;">Canonical Field</th>'
        f'<th style="padding:10px 14px;color:#8B99B5;font-weight:600;">Description</th>'
        f'<th style="padding:10px 14px;color:#8B99B5;font-weight:600;">Type</th>'
        f'<th style="padding:10px 14px;color:#8B99B5;font-weight:600;">Required</th>'
        f'</tr>'
        f'</thead>'
        f'<tbody>{rows}</tbody>'
        f'</table>'
        f'</div>',
        unsafe_allow_html=True,
    )

    render_section_header("box", "Technology Stack")
    st.markdown(
        f'<div class="ri-panel">'
        f'<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;font-size:0.84rem;">'
        f'<div><b style="color:#EEF2F8;">UI & Dashboard</b> · Streamlit (Python)</div>'
        f'<div><b style="color:#EEF2F8;">Data Engine</b> · Pandas & NumPy</div>'
        f'<div><b style="color:#EEF2F8;">Analytical Database</b> · DuckDB (in-memory SQL)</div>'
        f'<div><b style="color:#EEF2F8;">Visualizations</b> · Plotly Express & Graph Objects</div>'
        f'<div><b style="color:#EEF2F8;">Anomaly Engine</b> · Z-Score & IQR statistical detection</div>'
        f'<div><b style="color:#EEF2F8;">AI Layer</b> · OpenAI GPT & Google Gemini</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _SCHEMA_ROWS():
    from src.ingestion.schema import CANONICAL_FIELDS
    return CANONICAL_FIELDS.items()