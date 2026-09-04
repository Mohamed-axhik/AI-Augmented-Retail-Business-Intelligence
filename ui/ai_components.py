"""Premium AI Analyst workspace components."""
from __future__ import annotations

import streamlit as st
from src.utils.formatting import format_currency, format_pct, format_number
from ui.icons import icon, svg_data_uri

SUGGESTED_QUESTIONS = [
    ("Revenue drivers", "chart-line",
     "What drove the revenue decline?"),
    ("Top products", "package",
     "Which products generate the most revenue?"),
    ("Growth trends", "trending-up",
     "Which countries are growing fastest?"),
    ("Anomalies", "alert-triangle",
     "What anomalies need attention?"),
    ("Customer health", "users",
     "How is customer retention performing?"),
    ("Strategic priorities", "star",
     "What strategic recommendations should management prioritize?"),
]


def render_suggestion_chips(on_select) -> None:
    """Renders suggested-question pills; calls on_select(question) on click."""
    # Icons cannot be HTML in st.button labels, so draw them via CSS ::before.
    css = "".join(
        f".st-key-sugg_{i} button::before{{"
        f"content:'';width:15px;height:15px;flex-shrink:0;display:inline-block;"
        f"background:url('{svg_data_uri(ic, '#8B99B5')}') no-repeat center/contain;"
        f"vertical-align:-3px;margin-right:8px;"
        f"}}"
        for i, (_label, ic, _q) in enumerate(SUGGESTED_QUESTIONS)
    )
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="ri-section-sub" style="margin:0 0 10px 2px;color:#5D6B8A;">'
        f'<b>Suggested questions</b></div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(3)
    for i, (label, _ic, question) in enumerate(SUGGESTED_QUESTIONS):
        col = cols[i % 3]
        with col:
            if st.button(label, key=f"sugg_{i}",
                         width="stretch", type="secondary",
                         help=question):
                on_select(question)


def _evidence_items(context: dict) -> list[tuple[str, str]]:
    """Extracts compact computed-evidence facts from the business context."""
    items: list[tuple[str, str]] = []
    kpis = context.get("executive_kpis") or {}
    if kpis.get("total_revenue") is not None:
        items.append(("Revenue", format_currency(kpis["total_revenue"])))
    if kpis.get("total_profit") is not None:
        items.append(("Profit", format_currency(kpis["total_profit"])))
    if kpis.get("profit_margin_pct") is not None:
        items.append(("Margin", format_pct(kpis["profit_margin_pct"], include_sign=False)))
    if kpis.get("mom_growth_pct") is not None:
        items.append(("MoM Growth", format_pct(kpis["mom_growth_pct"])))
    if kpis.get("total_orders") is not None:
        items.append(("Orders", format_number(kpis["total_orders"])))
    if kpis.get("total_customers") is not None:
        items.append(("Customers", format_number(kpis["total_customers"])))
    if kpis.get("aov") is not None:
        items.append(("AOV", format_currency(kpis["aov"])))
    if context.get("detected_anomalies_count") is not None:
        items.append(("Anomalies", str(context["detected_anomalies_count"])))
    cats = context.get("category_summary") or []
    if cats:
        items.append(("Top Category", str(cats[0].get("category", "—"))))
    return items


def render_evidence_panel(context: dict) -> None:
    """Renders the computed-evidence strip below an AI answer."""
    items = _evidence_items(context)
    if not items:
        return
    chips = "".join(
        f'<div class="ri-evidence-item"><span class="ri-evidence-k">{k}</span>'
        f'<span class="ri-evidence-v">{v}</span></div>'
        for k, v in items
    )
    st.markdown(
        f'<div class="ri-evidence">'
        f'<div class="ri-evidence-label">{icon("layers", 12)} &nbsp;Computed Evidence</div>'
        f'<div class="ri-evidence-grid">{chips}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )