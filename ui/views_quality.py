"""Data Quality & Schema Health page — data observability interface."""
from __future__ import annotations

import streamlit as st
from src.ingestion.schema import CANONICAL_FIELDS
from ui.cards import render_kpi_card, render_score_gauge, render_status_badge
from ui.layout import render_empty_state, render_hero, render_section_header
from ui.quality_components import quality_tone, render_checklist_item, render_quality_metric


def render_data_quality(df, val_report):
    """Renders the Data Quality observability page."""
    render_hero(
        "DATA OBSERVABILITY",
        "Data Quality & Schema Health",
        "Validation metrics, column mapping layer and dataset health score.",
    )

    if not val_report:
        render_empty_state("No validation report", "Load a dataset to inspect its quality.",
                           icon_name="shield-check")
        return

    c_score, c_status, c_rows, c_cols, c_clean = st.columns([3, 4, 2, 2, 2])
    with c_score:
        render_score_gauge(val_report["score"], label="Data Quality Score",
                           status_text=val_report["status"])
    with c_status:
        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="ri-panel-title">Validation Status</div>', unsafe_allow_html=True)
        render_status_badge(val_report["status"])

        score = val_report["score"]
        if score >= 80:
            explanation = ("The dataset passes all critical quality checks. Schema coverage is "
                           "high, missing data is minimal, and date/price fields are clean.")
        elif score >= 60:
            explanation = ("The dataset is usable but has quality issues. Check missing values, "
                           "date parsing and price anomalies below.")
        else:
            explanation = ("Significant data quality issues detected. Review the checklist below "
                           "to identify specific problems affecting analysis accuracy.")
        st.markdown(
            f'<div style="margin-top:14px;font-size:0.8rem;color:#8B99B5;line-height:1.6;">'
            f'{explanation}'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c_rows:
        render_kpi_card("Source Rows", f"{val_report['total_rows']:,}",
                        icon_name="layers", icon_tone="blue",
                        sub="raw rows scanned")
    with c_clean:
        render_kpi_card("Cleaned Rows", f"{len(df):,}",
                        icon_name="filter", icon_tone="teal",
                        sub="rows after cleaning")
    with c_cols:
        render_kpi_card("Total Columns", f"{val_report['total_cols']}",
                        icon_name="grid", icon_tone="violet")

    render_section_header("scale", "Quality Metrics Breakdown",
                          "Issue counts detected during validation — status uses icon + text, not color alone")

    missing_tone = quality_tone(val_report["missing_cells_pct"], warn_above=2, crit_above=15)
    dup_tone = "passed" if val_report["duplicate_rows"] == 0 else (
        "critical" if val_report["duplicate_rows"] / max(val_report["total_rows"], 1) > 0.10 else "warning")
    dates_tone = "passed" if val_report["invalid_dates"] == 0 else "warning"
    neg_qty_tone = "passed" if val_report["negative_quantities"] == 0 else "info"
    neg_price_tone = "passed" if val_report["negative_prices"] == 0 else "warning"

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        render_quality_metric("Missing Values", f"{val_report['missing_cells_pct']}%",
                              missing_tone, detail=_tone_label(missing_tone), icon_name="circle-alert")
    with m2:
        render_quality_metric("Duplicate Rows", f"{val_report['duplicate_rows']:,}",
                              dup_tone, detail=_tone_label(dup_tone), icon_name="refresh-cw")
    with m3:
        render_quality_metric("Invalid Dates", f"{val_report['invalid_dates']:,}",
                              dates_tone, detail=_tone_label(dates_tone), icon_name="calendar")
    with m4:
        render_quality_metric("Negative Quantities", f"{val_report['negative_quantities']:,}",
                              neg_qty_tone, detail="Treated as returns", icon_name="gift")
    with m5:
        render_quality_metric("Negative Prices", f"{val_report['negative_prices']:,}",
                              neg_price_tone, detail=_tone_label(neg_price_tone), icon_name="alert-triangle")

    col_left, col_right = st.columns([6, 6])
    with col_left:
        render_section_header("circle-check", "Validation Checklist",
                              "Step-by-step quality checks and their outcomes")
        checklist_html = ""
        for icon_title, detail in val_report["checklist"]:
            tone = _checklist_tone(icon_title)
            title = _clean_checklist_title(icon_title)
            checklist_html += render_checklist_item(tone, title, detail, return_html=True)
        st.markdown(f'<div class="ri-panel">{checklist_html}</div>', unsafe_allow_html=True)

    with col_right:
        render_section_header("settings", "Schema Column Mapping",
                              "Customize how uploaded columns map to the canonical schema")

        current_mapping = st.session_state.get("column_mapping", {})
        raw_columns = st.session_state.get("raw_columns")
        if not raw_columns and not df.empty:
            raw_columns = list(df.columns)
        df_cols = ["(Unmapped)"] + list(raw_columns or [])

        new_mapping = {}
        with st.form("schema_mapping_form"):
            for c_field, info in CANONICAL_FIELDS.items():
                field_label = f"{c_field} ({'Required' if info['required'] else 'Optional'})"
                curr_val = current_mapping.get(c_field)
                default_idx = df_cols.index(curr_val) if curr_val in df_cols else 0
                selected_col = st.selectbox(field_label, options=df_cols, index=default_idx,
                                            key=f"map_select_{c_field}")
                new_mapping[c_field] = None if selected_col == "(Unmapped)" else selected_col

            if st.form_submit_button("Save Schema Mapping & Re-process", type="primary",
                                     width="stretch"):
                st.session_state["column_mapping"] = new_mapping
                st.success("Schema mapping updated — reloading pipeline…")
                st.rerun()

    if not df.empty:
        render_section_header("download", "Download Cleaned Dataset",
                              "Export the standardized canonical dataset for further analysis")
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Standardized CSV",
            data=csv_data,
            file_name="standardized_retail_dataset.csv",
            mime="text/csv",
        )


def _tone_label(tone: str) -> str:
    return {"passed": "Passed", "warning": "Warning",
            "critical": "Critical", "info": "Note"}[tone]


def _checklist_tone(title: str) -> str:
    if title.startswith("✓"):
        return "passed"
    if title.startswith("⚠") or title.startswith("ℹ"):
        return "warning" if title.startswith("⚠") else "info"
    if title.startswith("🔴"):
        return "critical"
    return "info"


def _clean_checklist_title(title: str) -> str:
    return title.lstrip("✓⚠🔴ℹ").strip() or title