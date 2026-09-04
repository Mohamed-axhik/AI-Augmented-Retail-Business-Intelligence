"""Sidebar: brand, navigation, dataset status, filters and AI status.

Also owns the data pipeline.  The full load -> validate -> clean -> transform
chain is cached per data source so filter changes never re-process the dataset.
"""
from __future__ import annotations

import io
import os
from typing import Dict, Tuple

import pandas as pd
import streamlit as st

from src.ingestion.loader import load_file
from src.ingestion.schema import detect_column_mapping
from src.ingestion.validator import validate_dataset
from src.processing.cleaner import clean_dataset
from src.processing.transformer import transform_to_canonical
from src.utils.formatting import format_number
from ui.cards import render_status_badge
from ui.icons import icon, svg_data_uri

DEFAULT_DATASET = os.path.join("data", "online_retail_II.csv")
FALLBACK_DATASET = os.path.join("data", "sample_retail_data.csv")

NAV_PAGES = [
    ("executive", "dashboard", "Executive Overview"),
    ("sales", "chart-line", "Sales Analytics"),
    ("customers", "users", "Customer Analytics"),
    ("category", "tag", "Category & Product"),
    ("stores", "store", "Store Performance"),
    ("anomaly", "alert-triangle", "Anomaly Detection"),
    ("ai", "sparkles", "AI Business Analyst"),
    ("quality", "shield-check", "Data Quality"),
    ("about", "info", "About"),
]

NAV_GROUPS = [
    ("OVERVIEW", ["executive"]),
    ("ANALYTICS", ["sales", "customers", "category", "stores"]),
    ("INTELLIGENCE", ["anomaly", "ai"]),
    ("DATA", ["quality"]),
    ("SYSTEM", ["about"]),
]

_SOURCE_ICONS = {"sales": "chart-line", "customers": "users", "category": "tag",
                 "stores": "store", "anomaly": "alert-triangle", "ai": "sparkles",
                 "quality": "shield-check", "about": "info"}

SOURCE_BUILTIN = "Online Retail II (Built-in)"
SOURCE_SAMPLE = "Sample Dataset (Legacy)"
SOURCE_UPLOAD = "Upload CSV / Excel"


# ---------------------------------------------------------------------------
# Data pipeline (cached per source + mapping)
# ---------------------------------------------------------------------------
def _peek_columns_file(path: str, mtime: float) -> list:
    """Reads only the header row of a CSV to expose column names (cheap)."""
    try:
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                header = pd.read_csv(path, nrows=0, encoding=enc)
                return list(header.columns)
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
    except Exception:
        pass
    return []


def _peek_columns_bytes(raw_bytes: bytes, name: str) -> list:
    """Reads only the header of an uploaded buffer to expose column names."""
    import io
    try:
        if name.lower().endswith((".xlsx", ".xls")):
            header = pd.read_excel(io.BytesIO(raw_bytes), nrows=0)
            return list(header.columns)
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                header = pd.read_csv(io.BytesIO(raw_bytes), nrows=0, encoding=enc)
                return list(header.columns)
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
    except Exception:
        pass
    return []


def _mapping_for(filename: str, columns: list) -> Dict:
    """Returns the session mapping for the file, re-detecting when stale.

    The mapping is passed into the cached pipeline so that editing the
    schema mapping on the Data Quality page invalidates the cache and
    re-processes the dataset with the new mapping.
    """
    current = st.session_state.get("column_mapping", {})
    mapped_cols = {v for v in current.values() if v}
    stale = (
        not columns
        or st.session_state.get("current_file") != filename
        or not mapped_cols
        or not mapped_cols.issubset(set(columns))
    )
    if stale and columns:
        st.session_state["column_mapping"] = detect_column_mapping(columns)
        st.session_state["current_file"] = filename
    return st.session_state.get("column_mapping") or {}


@st.cache_data(show_spinner="Loading dataset & building analytics pipeline...")
def _load_and_process_builtin(source_id: str, file_size: int, file_mtime: float,
                              mapping: Dict) -> Tuple:
    """Loads, validates, cleans and transforms a built-in dataset (cached)."""
    df, err = load_file(source_id)
    if err or df is None or df.empty:
        return pd.DataFrame(), {}, None, err or ""
    return _process_raw(df, source_id, mapping)


@st.cache_data(show_spinner="Processing uploaded dataset...")
def _load_and_process_upload(name: str, size: int, raw_bytes: bytes, mapping: Dict) -> Tuple:
    """Loads an uploaded file buffer and processes it (cached by content)."""
    import io
    df, err = load_file(io.BytesIO(raw_bytes), name)
    if err or df is None or df.empty:
        return pd.DataFrame(), {}, None, err or ""
    return _process_raw(df, name, mapping)


def _process_raw(raw_df: pd.DataFrame, filename: str, mapping: Dict) -> Tuple:
    """Runs validate -> clean -> transform and returns cached artifacts."""
    val_report = validate_dataset(raw_df, mapping)
    clean_df = clean_dataset(raw_df, mapping)
    canonical_df = transform_to_canonical(clean_df, mapping)

    # Pre-compute the day column once so date filtering stays cheap on every rerun.
    if not canonical_df.empty and "date" in canonical_df.columns:
        canonical_df["_day"] = canonical_df["date"].dt.date

    return canonical_df, val_report, mapping, ""


def _svg_data_uri(icon_name: str, color: str, size: int = 16) -> str:
    return svg_data_uri(icon_name, color, size)


# ---------------------------------------------------------------------------
# Sidebar renderers
# ---------------------------------------------------------------------------
def _render_brand() -> None:
    st.markdown(
        f'<div class="ri-sb-brand">'
        f'<div class="ri-sb-logo">{icon("zap", 20)}</div>'
        f'<div>'
        f'<div class="ri-sb-title">Retail Intelligence</div>'
        f'<div class="ri-sb-tagline">AI-Augmented Analytics</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_nav(active_slug: str) -> None:
    nav_map = {slug: (ic, label) for slug, ic, label in NAV_PAGES}

    # Per-button styling incl. inline SVG icons and the active state.
    css = []
    for slug, ic, _label in NAV_PAGES:
        inactive = "#8B99B5"
        active = "#4C8DFF"
        is_active = slug == active_slug
        color = active if is_active else inactive
        bg = "linear-gradient(90deg, rgba(76,141,255,0.16), rgba(76,141,255,0.05))" if is_active else "transparent"
        border = "1px solid rgba(76,141,255,0.32)" if is_active else "1px solid transparent"
        text = "#EEF2F8" if is_active else "#8B99B5"
        weight = 600 if is_active else 500
        shadow = ("box-shadow:0 0 16px rgba(76,141,255,0.18), inset 3px 0 0 #4C8DFF;" if is_active
                  else "box-shadow:none;")
        css.append(
            f".st-key-nav_{slug} button{{"
            f"display:flex;align-items:center;gap:9px;justify-content:flex-start;"
            f"background:{bg};border:{border};color:{text};font-weight:{weight};"
            f"border-radius:9px;padding:8px 12px;font-size:0.86rem;"
            f"{shadow}"
            f"transition:background .14s ease,color .14s ease,border-color .14s ease,box-shadow .14s ease;"
            f"}}"
            f".st-key-nav_{slug} button:hover{{background:rgba(76,141,255,0.10);color:#C3CEDA;}}"
            f".st-key-nav_{slug} button::before{{"
            f"content:'';width:16px;height:16px;flex-shrink:0;"
            f"background:url('{_svg_data_uri(ic, color)}') no-repeat center/contain;"
            f"}}"
        )
    st.markdown(f"<style>{''.join(css)}</style>", unsafe_allow_html=True)

    for group_label, slugs in NAV_GROUPS:
        st.markdown(f'<div class="ri-sb-label">{group_label}</div>', unsafe_allow_html=True)
        for slug in slugs:
            if slug not in nav_map:
                continue
            _ic, label = nav_map[slug]
            if st.sidebar.button(label, key=f"nav_{slug}", width="stretch",
                                 type="secondary"):
                st.session_state["page"] = slug
        st.markdown('<div style="height:4px;"></div>', unsafe_allow_html=True)


def _display_filename(filename: str) -> str:
    """Returns a clean display name for any OS path separator."""
    if not filename:
        return "No dataset"
    return filename.replace("\\", "/").split("/")[-1]


def _render_dataset_card(filename: str, records: int, score: int) -> None:
    fill_color = "#34D399" if score >= 80 else ("#FBBF24" if score >= 60 else "#F87171")
    name = _display_filename(filename)
    if len(name) > 26:
        name = name[:23] + "…"
    st.markdown(
        f'<div class="ri-sb-dataset">'
        f'<div class="ri-sb-ds-row">'
        f'<div>'
        f'<div class="ri-sb-ds-name">{name}</div>'
        f'<div class="ri-sb-ds-meta">{records:,} records</div>'
        f'</div>'
        f'</div>'
        f'<div class="ri-sb-bar"><div class="ri-sb-fill" style="width:{min(max(score,0),100)}%;background:{fill_color};"></div></div>'
        f'<div class="ri-sb-score-line">'
        f'<span class="ri-sb-score-label">Data Quality</span>'
        f'<span class="ri-sb-score-num">{score}/100</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_ai_status() -> None:
    api_key = st.session_state.get("llm_api_key")
    if api_key:
        provider = "Gemini/OpenAI" if api_key.startswith(("AIza", "sk-")) else "Custom LLM"
        st.markdown(
            f'<div class="ri-sb-ai">{icon("bot", 15)}<div>'
            f'<b>AI Analyst · Connected</b>'
            f'<span>{provider} reasoning enabled</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="ri-sb-ai">{icon("sparkles", 15)}<div>'
            f'<b>AI Analyst · Ready</b>'
            f'<span>Smart offline engine active</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def render_sidebar() -> Tuple[str, pd.DataFrame, Dict]:
    """Renders the sidebar and returns (page_slug, filtered_df, validation_report)."""
    _render_brand()

    active_page = st.session_state.get("page", "executive")
    _render_nav(active_page)

    st.markdown('<div class="ri-sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="ri-sb-label">Dataset</div>', unsafe_allow_html=True)

    source = st.sidebar.selectbox(
        "Data source",
        [SOURCE_BUILTIN, SOURCE_SAMPLE, SOURCE_UPLOAD],
        label_visibility="collapsed",
    )

    canonical_df: pd.DataFrame = pd.DataFrame()
    val_report: Dict = {}
    filename = ""

    try:
        if source == SOURCE_UPLOAD:
            uploaded = st.sidebar.file_uploader(
                "Upload Retail Dataset",
                type=["csv", "xlsx", "xls"],
                help="Recommended dataset size < 200MB",
                label_visibility="collapsed",
            )
            if uploaded is not None:
                raw_bytes = uploaded.getvalue()
                filename = uploaded.name
                raw_cols = _peek_columns_bytes(raw_bytes, filename)
                if not raw_cols:
                    full, ferr = load_file(io.BytesIO(raw_bytes), filename)
                    if ferr is None and full is not None and not full.empty:
                        raw_cols = list(full.columns)
                if raw_cols:
                    st.session_state["raw_columns"] = raw_cols
                mapping = _mapping_for(filename, raw_cols)
                canonical_df, val_report, _, err = _load_and_process_upload(
                    filename, len(raw_bytes), raw_bytes, mapping
                )
                if err:
                    st.sidebar.error(err)
            else:
                st.sidebar.info("Upload a CSV or Excel file to get started.")
        else:
            path = DEFAULT_DATASET if source == SOURCE_BUILTIN else FALLBACK_DATASET
            if os.path.exists(path):
                filename = path
                size = os.path.getsize(path)
                mtime = os.path.getmtime(path)
                raw_cols = _peek_columns_file(path, mtime)
                if not raw_cols:
                    full, ferr = load_file(path)
                    if ferr is None and full is not None and not full.empty:
                        raw_cols = list(full.columns)
                if raw_cols:
                    st.session_state["raw_columns"] = raw_cols
                mapping = _mapping_for(filename, raw_cols)
                canonical_df, val_report, _, err = _load_and_process_builtin(path, size, mtime, mapping)
                if err:
                    st.sidebar.error(err)
            else:
                st.sidebar.warning("Dataset file not found in data folder.")
    except Exception as e:  # pragma: no cover - defensive
        st.sidebar.error(f"Failed to process dataset: {str(e)}")
        return active_page, pd.DataFrame(), {}

    if canonical_df.empty or not val_report:
        st.sidebar.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
        st.sidebar.info("Load a dataset to explore the platform.")
        return active_page, pd.DataFrame(), {}

    st.session_state["full_dataset"] = canonical_df
    st.session_state["dataset_label"] = _display_filename(filename)

    _render_dataset_card(filename, len(canonical_df), val_report.get("score", 0))
    render_status_badge(val_report.get("status", ""))

    st.markdown('<div class="ri-sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="ri-sb-label">Filters</div>', unsafe_allow_html=True)

    filtered_df = _render_filters(canonical_df)

    # Build canonical metadata object after filtering so filtered_rows is accurate.
    date_min = canonical_df["date"].min() if "date" in canonical_df.columns else None
    date_max = canonical_df["date"].max() if "date" in canonical_df.columns else None
    st.session_state["dataset_meta"] = {
        "source_rows": val_report.get("total_rows", len(canonical_df)),
        "total_rows": len(canonical_df),
        "cleaned_rows": len(canonical_df),
        "total_cols": len(canonical_df.columns),
        "filtered_rows": len(filtered_df) if not filtered_df.empty else 0,
        "date_min": date_min,
        "date_max": date_max,
        "quality_score": val_report.get("score", 0),
        "quality_status": val_report.get("status", "Unknown"),
        "filename": _display_filename(filename),
    }

    st.markdown('<div class="ri-sidebar-divider"></div>', unsafe_allow_html=True)
    _render_ai_status()

    if st.sidebar.button("Reset filters", key="reset_filters", width="stretch",
                         type="secondary"):
        for _filter_key in ("filt_date_range", "filt_categories", "filt_stores"):
            st.session_state.pop(_filter_key, None)
        st.rerun()

    # Re-read the page AFTER nav buttons ran so the current run routes immediately.
    return st.session_state.get("page", "executive"), filtered_df, val_report


def _render_filters(canonical_df: pd.DataFrame) -> pd.DataFrame:
    """Renders date / category / store filters over the canonical dataset."""
    day = canonical_df["_day"]
    min_date = day.min()
    max_date = day.max()

    selected_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="filt_date_range",
    )
    if isinstance(selected_range, (list, tuple)) and len(selected_range) == 2:
        start_d, end_d = selected_range
    else:
        start_d, end_d = min_date, max_date

    mask = (day >= start_d) & (day <= end_d)
    filtered_df = canonical_df[mask]

    if filtered_df.empty:
        st.sidebar.caption("No rows in the selected date range.")
        return filtered_df

    all_categories = sorted(filtered_df["category"].dropna().unique())
    if len(all_categories) > 1:
        selected_categories = st.sidebar.multiselect(
            "Category",
            options=all_categories,
            default=all_categories,
            key="filt_categories",
        )
        if selected_categories:
            filtered_df = filtered_df[filtered_df["category"].isin(selected_categories)]

    if filtered_df.empty:
        st.sidebar.caption("No rows after category filtering.")
        return filtered_df

    all_stores = sorted(filtered_df["store"].dropna().unique())
    if len(all_stores) > 1:
        selected_stores = st.sidebar.multiselect(
            "Store",
            options=all_stores,
            default=all_stores,
            key="filt_stores",
        )
        if selected_stores:
            filtered_df = filtered_df[filtered_df["store"].isin(selected_stores)]

    return filtered_df