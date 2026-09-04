"""Design system: tokens, global CSS and the centralized Plotly theme.

This module is the single source of truth for the visual language of the
Retail Intelligence platform.  Values are NEVER scattered across views --
every component and chart pulls tokens from here.
"""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

# ============================================================
#  COLOR TOKENS
# ============================================================
class C:
    # Surfaces
    BG_BASE       = "#070B14"   # app background (near-black navy)
    BG_SIDEBAR    = "#0A0F1A"   # sidebar surface
    BG_CARD       = "#0E1526"   # card / panel surface
    BG_ELEVATED   = "#141D33"   # elevated surface (hover / active)
    BG_INSET      = "#0A1120"   # inset wells / tooltips

    # Borders (very subtle)
    BORDER        = "rgba(148, 163, 184, 0.11)"
    BORDER_STRONG = "rgba(148, 163, 184, 0.22)"

    # Text
    TEXT_PRIMARY   = "#EEF2F8"
    TEXT_SECONDARY = "#C3CEDA"
    TEXT_MUTED     = "#8B99B5"
    TEXT_FAINT     = "#5D6B8A"

    # Brand accent (primary) + secondary accents
    ACCENT      = "#4C8DFF"   # primary brand blue
    ACCENT_DARK = "#2E66D6"
    ACCENT_SOFT = "rgba(76, 141, 255, 0.14)"
    ACCENT_2    = "#38BDF8"   # sky (secondary accent)
    VIOLET      = "#8B5CF6"
    TEAL        = "#2DD4BF"

    # Semantic
    SUCCESS = "#34D399"
    WARNING = "#FBBF24"
    DANGER  = "#F87171"

    # Semantic soft backgrounds
    SUCCESS_BG = "rgba(52, 211, 153, 0.12)"
    WARNING_BG = "rgba(251, 191, 36, 0.12)"
    DANGER_BG  = "rgba(248, 113, 113, 0.12)"

    # Anomaly
    ANOMALY_UP   = "#FBBF24"   # spike (high)
    ANOMALY_DOWN = "#F87171"   # dip (low)

    # Chart series palette (restrained)
    SERIES = ["#4C8DFF", "#38BDF8", "#2DD4BF", "#8B5CF6", "#FBBF24", "#FB7185"]

    # Plotly-specific
    GRID   = "rgba(148, 163, 184, 0.09)"
    TICK   = "#8B99B5"


# ============================================================
#  SPACING / RADIUS / SHADOW / TYPOGRAPHY TOKENS
# ============================================================
class SP:
    XS, SM, MD, LG, XL, XXL = 4, 8, 12, 16, 24, 32


class RADIUS:
    CONTROL = 8
    CARD    = 12
    PANEL   = 16


class SHADOW:
    CARD    = "0 1px 2px rgba(0,0,0,0.25), 0 8px 24px rgba(0,0,0,0.28)"
    HOVER   = "0 2px 4px rgba(0,0,0,0.3), 0 14px 34px rgba(0,0,0,0.4)"
    GLOW    = "0 0 0 1px rgba(76,141,255,0.25), 0 8px 28px rgba(76,141,255,0.15)"


class FONT:
    SANS = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    MONO = "'JetBrains Mono', 'SF Mono', 'Cascadia Code', Consolas, monospace"


class FS:  # font sizes
    HERO   = "1.6rem"
    TITLE  = "1.25rem"
    SECTION = "1.05rem"
    BODY   = "0.9rem"
    SMALL  = "0.82rem"
    TINY   = "0.72rem"
    KPI    = "1.7rem"


# ============================================================
#  CHART TOKENS
# ============================================================
class CH:
    PRIMARY   = 420   # hero revenue chart
    SECONDARY = 340   # paired charts
    TERTIARY  = 300   # small supporting charts
    TIMELINE  = 400
    TABLE     = 380


def premium_dark_theme() -> dict:
    """Returns a centralized Plotly layout config applied to every chart."""
    return dict(
        template="none",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT.SANS, size=12, color=C.TEXT_SECONDARY),
        colorway=C.SERIES,
        margin=dict(l=8, r=8, t=10, b=8),
        hoverlabel=dict(
            bgcolor=C.BG_ELEVATED,
            bordercolor=C.BORDER_STRONG,
            font=dict(family=FONT.SANS, size=12, color=C.TEXT_PRIMARY),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(family=FONT.SANS, size=11, color=C.TEXT_MUTED),
            itemclick=False,
            itemdoubleclick=False,
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            linecolor=C.BORDER_STRONG,
            linewidth=1,
            tickfont=dict(family=FONT.SANS, size=11, color=C.TICK),
            title_font=dict(family=FONT.SANS, size=11, color=C.TEXT_MUTED),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=C.GRID,
            gridwidth=1,
            zeroline=False,
            linecolor="rgba(0,0,0,0)",
            tickfont=dict(family=FONT.SANS, size=11, color=C.TICK),
            title_font=dict(family=FONT.SANS, size=11, color=C.TEXT_MUTED),
        ),
        hovermode="x unified",
        dragmode=False,
        autosize=True,
        bargap=0.35,
    )


def style_figure(fig: go.Figure, height: int = CH.SECONDARY, **layout_overrides) -> go.Figure:
    """Applies the shared premium theme plus per-chart overrides."""
    theme = premium_dark_theme()
    theme["height"] = height
    theme.update(layout_overrides)
    fig.update_layout(**theme)

    for ax in list(fig.select_xaxes()) + list(fig.select_yaxes()):
        ax.color = C.BORDER_STRONG
        if ax.title and ax.title.text:
            ax.title.font = dict(family=FONT.SANS, size=11, color=C.TEXT_MUTED)
    return fig


def build_title(title: str, subtitle: str | None = None) -> dict:
    """Builds a compact in-chart title dict used sparingly (HTML headers preferred)."""
    return dict(
        text=title,
        x=0,
        xanchor="left",
        y=1.0,
        yanchor="bottom",
        font=dict(family=FONT.SANS, size=13, color=C.TEXT_PRIMARY, weight=600),
    )


# ============================================================
#  GLOBAL CSS
# ============================================================
_GLOBAL_CSS = """
<style>
/* ============================================================
   RETAIL INTELLIGENCE — GLOBAL DESIGN SYSTEM
   ============================================================ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --ri-bg:        #070B14;
  --ri-card:      #0E1526;
  --ri-elevated:  #141D33;
  --ri-border:    rgba(148,163,184,0.11);
  --ri-accent:    #4C8DFF;
  --ri-text:      #EEF2F8;
  --ri-muted:     #8B99B5;
}

html, body, [class*="css"], .stApp {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color: #EEF2F8;
}

.stApp { background: #070B14; }

/* ---------- App background depth ---------- */
[data-testid="stAppViewContainer"] > .main {
  background:
    radial-gradient(1100px 480px at 8% -8%, rgba(76,141,255,0.10), transparent 60%),
    radial-gradient(820px 420px at 98% -6%, rgba(139,92,246,0.07), transparent 55%),
    radial-gradient(700px 500px at 50% 110%, rgba(56,189,248,0.05), transparent 60%),
    #070B14;
}
[data-testid="stAppViewContainer"] > .main .block-container {
  padding-top: 1.1rem;
  padding-bottom: 4rem;
  max-width: 1480px;
}

/* Hide Streamlit default chrome */
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none; }

#MainMenu, footer { visibility: hidden; height: 0; }

/* ---------- Selection & scrollbar ---------- */
::selection { background: rgba(76,141,255,0.32); }
::-webkit-scrollbar { width: 9px; height: 9px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(148,163,184,0.18); border-radius: 8px; }
::-webkit-scrollbar-thumb:hover { background: rgba(148,163,184,0.32); }

/* ---------- Typography ---------- */
h1, h2, h3, h4 { font-family: 'Inter', sans-serif; color: #EEF2F8; letter-spacing: -0.015em; }
p { color: #C3CEDA; }
.stMarkdown a { color: #4C8DFF; }

/* ============================================================
   TOP APP HEADER
   ============================================================ */
.ri-app-header {
  position: sticky; top: 0; z-index: 900;
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px;
  padding: 10px 22px;
  margin-bottom: 20px;
  border: 1px solid rgba(148,163,184,0.10);
  border-radius: 14px;
  background: rgba(10,15,26,0.82);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow: 0 6px 24px rgba(0,0,0,0.25);
}
.ri-app-header-left { display: flex; align-items: center; gap: 12px; min-width: 0; }
.ri-brand-mark {
  width: 36px; height: 36px; border-radius: 10px; flex-shrink: 0;
  background: linear-gradient(135deg, #4C8DFF 0%, #7C5CFF 100%);
  display: flex; align-items: center; justify-content: center;
  color: #fff; box-shadow: 0 4px 14px rgba(76,141,255,0.35);
}
.ri-brand-mark svg { width: 20px; height: 20px; }
.ri-header-brand { font-weight: 700; font-size: 0.98rem; color: #EEF2F8; line-height: 1.2; }
.ri-header-tag  { font-size: 0.68rem; color: #5D6B8A; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; }
.ri-header-right { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }

.ri-pill {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 5px 12px; border-radius: 999px;
  font-size: 0.75rem; font-weight: 600; color: #C3CEDA;
  background: rgba(20,29,51,0.85);
  border: 1px solid rgba(148,163,184,0.14);
  white-space: nowrap;
}
.ri-pill .ri-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.ri-pill.live .ri-dot { background: #34D399; box-shadow: 0 0 0 0 rgba(52,211,153,0.7); animation: ri-pulse 2.4s ease-out infinite; }
@keyframes ri-pulse {
  0%   { box-shadow: 0 0 0 0 rgba(52,211,153,0.45); }
  70%  { box-shadow: 0 0 0 7px rgba(52,211,153,0); }
  100% { box-shadow: 0 0 0 0 rgba(52,211,153,0); }
}
.ri-pill.accent .ri-dot { background: #4C8DFF; }

/* ============================================================
   HERO SECTION
   ============================================================ */
.ri-hero {
  position: relative; overflow: hidden;
  padding: 26px 28px; margin-bottom: 22px;
  border: 1px solid rgba(148,163,184,0.12);
  border-radius: 16px;
  background:
    linear-gradient(180deg, rgba(20,29,51,0.55) 0%, rgba(10,15,26,0.85) 100%);
  box-shadow: 0 8px 30px rgba(0,0,0,0.25);
}
.ri-hero::before {
  content: "";
  position: absolute; inset: 0;
  background:
    radial-gradient(600px 200px at 12% 0%, rgba(76,141,255,0.16), transparent 60%),
    radial-gradient(480px 200px at 88% 0%, rgba(139,92,246,0.12), transparent 60%);
  pointer-events: none;
}
.ri-hero-grid {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(148,163,184,0.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148,163,184,0.045) 1px, transparent 1px);
  background-size: 34px 34px;
  -webkit-mask-image: radial-gradient(640px 240px at 50% 0%, rgba(0,0,0,0.8), transparent 75%);
          mask-image: radial-gradient(640px 240px at 50% 0%, rgba(0,0,0,0.8), transparent 75%);
  pointer-events: none;
}
.ri-hero-grid::after {
  content: "";
  position: absolute; inset: 0;
  background:
    radial-gradient(2px 2px at 18% 35%, rgba(56,189,248,0.85), transparent 2px),
    radial-gradient(2px 2px at 68% 18%, rgba(139,92,246,0.75), transparent 2px),
    radial-gradient(3px 3px at 84% 55%, rgba(76,141,255,0.75), transparent 3px),
    radial-gradient(2px 2px at 42% 78%, rgba(45,212,191,0.6), transparent 2px),
    radial-gradient(2px 2px at 55% 45%, rgba(251,191,36,0.5), transparent 2px);
  animation: ri-drift 9s ease-in-out infinite;
  pointer-events: none;
}
@keyframes ri-drift {
  0%, 100% { transform: translate3d(0,0,0); opacity: 0.5; }
  25% { transform: translate3d(6px,-10px,0); opacity: 0.9; }
  50% { transform: translate3d(-4px,-18px,0); opacity: 0.6; }
  75% { transform: translate3d(8px,-6px,0); opacity: 0.85; }
}
.ri-hero-inner { position: relative; z-index: 1; }
.ri-hero-eyebrow {
  display: inline-flex; align-items: center; gap: 8px;
  font-size: 0.68rem; font-weight: 700; color: #4C8DFF;
  text-transform: uppercase; letter-spacing: 0.16em;
  margin-bottom: 10px;
}
.ri-hero-eyebrow svg { width: 14px; height: 14px; }
.ri-hero-title { font-size: 1.75rem; font-weight: 800; color: #EEF2F8; letter-spacing: -0.02em; line-height: 1.15; }
.ri-hero-sub   { font-size: 0.92rem; color: #8B99B5; margin-top: 6px; max-width: 720px; }
.ri-hero-meta {
  display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px;
}
.ri-chip {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 4px 11px; border-radius: 8px;
  background: rgba(20,29,51,0.75);
  border: 1px solid rgba(148,163,184,0.12);
  font-size: 0.74rem; font-weight: 500; color: #C3CEDA;
}
.ri-chip svg { width: 13px; height: 13px; color: #4C8DFF; flex-shrink: 0; }
.ri-chip b { font-weight: 600; color: #EEF2F8; font-variant-numeric: tabular-nums; }

/* ============================================================
   SECTION HEADER
   ============================================================ */
.ri-section {
  display: flex; align-items: center; gap: 10px;
  margin: 26px 0 12px 0;
}
.ri-section-icon {
  width: 30px; height: 30px; border-radius: 9px; flex-shrink: 0;
  background: rgba(76,141,255,0.13);
  border: 1px solid rgba(76,141,255,0.22);
  display: flex; align-items: center; justify-content: center;
  color: #4C8DFF;
}
.ri-section-icon svg { width: 15px; height: 15px; }
.ri-section-title { font-size: 1.02rem; font-weight: 700; color: #E6EDF7; letter-spacing: -0.01em; }
.ri-section-sub  { font-size: 0.8rem; color: #8B99B5; margin: -4px 0 0 40px; }

/* ============================================================
   KPI CARDS
   ============================================================ */
.ri-kpi {
  position: relative;
  background: linear-gradient(180deg, rgba(20,29,51,0.75) 0%, rgba(14,21,38,0.9) 100%);
  border: 1px solid rgba(148,163,184,0.11);
  border-radius: 14px;
  padding: 16px 18px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.25), 0 8px 24px rgba(0,0,0,0.22);
  transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
  height: 100%;
  min-width: 0;
  display: flex; flex-direction: column;
}
.ri-kpi:hover {
  transform: translateY(-2px);
  border-color: rgba(76,141,255,0.35);
  box-shadow: 0 2px 4px rgba(0,0,0,0.3), 0 14px 34px rgba(0,0,0,0.38);
}
.ri-kpi-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
.ri-kpi-label {
  font-size: 0.7rem; font-weight: 600; color: #8B99B5;
  text-transform: uppercase; letter-spacing: 0.07em; line-height: 1.5;
  overflow: hidden;
}
.ri-kpi-icon {
  width: 32px; height: 32px; border-radius: 9px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  border: 1px solid rgba(76,141,255,0.18);
  background: rgba(76,141,255,0.10);
  color: #4C8DFF;
}
.ri-kpi-icon svg { width: 16px; height: 16px; }
.ri-kpi-icon.green  { background: rgba(52,211,153,0.10); border-color: rgba(52,211,153,0.22); color: #34D399; }
.ri-kpi-icon.teal   { background: rgba(45,212,191,0.10); border-color: rgba(45,212,191,0.22); color: #2DD4BF; }
.ri-kpi-icon.sky    { background: rgba(56,189,248,0.10); border-color: rgba(56,189,248,0.22); color: #38BDF8; }
.ri-kpi-icon.violet { background: rgba(139,92,246,0.10); border-color: rgba(139,92,246,0.22); color: #8B5CF6; }
.ri-kpi-icon.amber  { background: rgba(251,191,36,0.10); border-color: rgba(251,191,36,0.22); color: #FBBF24; }
.ri-kpi-icon.red    { background: rgba(248,113,113,0.10); border-color: rgba(248,113,113,0.22); color: #F87171; }

.ri-kpi-value {
  font-size: 1.7rem; font-weight: 700; color: #EEF2F8;
  letter-spacing: -0.02em; line-height: 1.35; margin-top: 10px;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.ri-kpi-value .ri-kpi-unit { font-size: 1rem; font-weight: 600; color: #8B99B5; margin-left: 2px; }
.ri-kpi-delta {
  display: flex; align-items: center; gap: 5px;
  font-size: 0.78rem; font-weight: 600; margin-top: 8px;
  font-variant-numeric: tabular-nums;
}
.ri-kpi-delta svg { width: 13px; height: 13px; flex-shrink: 0; }
.ri-kpi-delta.up   { color: #34D399; }
.ri-kpi-delta.down { color: #F87171; }
.ri-kpi-delta.flat { color: #8B99B5; }
.ri-kpi-sub { font-size: 0.72rem; color: #5D6B8A; margin-top: 4px; }

/* ============================================================
   EQUAL HEIGHT CARDS IN COLUMN ROWS
   ============================================================ */
[data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
  display: flex; flex-direction: column;
}
[data-testid="stColumn"] [data-testid="stElementContainer"] {
  flex: 1 1 auto;
  display: flex; flex-direction: column;
}
[data-testid="stColumn"] [data-testid="stElementContainer"] > [data-testid="stMarkdown"] {
  flex: 1 1 auto;
}
[data-testid="stColumn"] [data-testid="stMarkdown"] > div { height: 100%; }
[data-testid="stColumn"] [data-testid="stMarkdownContainer"] { height: 100%; }
[data-testid="stColumn"] .ri-kpi,
[data-testid="stColumn"] .ri-panel { height: 100%; }

/* ============================================================
   PANEL / CARD WRAPPER
   ============================================================ */
.ri-panel {
  background: linear-gradient(180deg, rgba(20,29,51,0.6) 0%, rgba(14,21,38,0.88) 100%);
  border: 1px solid rgba(148,163,184,0.11);
  border-radius: 14px;
  padding: 16px 18px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.22), 0 8px 24px rgba(0,0,0,0.2);
}
.ri-panel-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 0.82rem; font-weight: 700; color: #D7E0EE;
  letter-spacing: 0.02em; margin-bottom: 12px;
}
.ri-panel-title svg { width: 15px; height: 15px; color: #4C8DFF; }

/* ============================================================
   BADGES
   ============================================================ */
.ri-badge {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 4px 12px; border-radius: 999px;
  font-weight: 600; font-size: 0.78rem; line-height: 1.5;
  border: 1px solid;
}
.ri-badge svg { width: 12px; height: 12px; flex-shrink: 0; }
.ri-badge.passed   { background: rgba(52,211,153,0.10);  color: #4ade80; border-color: rgba(52,211,153,0.28); }
.ri-badge.warning  { background: rgba(251,191,36,0.10);  color: #FBBF24; border-color: rgba(251,191,36,0.28); }
.ri-badge.critical { background: rgba(248,113,113,0.10); color: #F87171; border-color: rgba(248,113,113,0.28); }
.ri-badge.info     { background: rgba(76,141,255,0.10);  color: #8FB8FF; border-color: rgba(76,141,255,0.28); }
.ri-badge.neutral  { background: rgba(148,163,184,0.10); color: #C3CEDA; border-color: rgba(148,163,184,0.22); }

/* ============================================================
   SCORE GAUGE
   ============================================================ */
.ri-score-card {
  text-align: center;
  background: linear-gradient(180deg, rgba(20,29,51,0.75) 0%, rgba(14,21,38,0.9) 100%);
  border: 1px solid rgba(148,163,184,0.11);
  border-radius: 14px;
  padding: 20px 16px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.22), 0 8px 24px rgba(0,0,0,0.2);
  height: 100%;
}
.ri-score-ring {
  width: 104px; height: 104px; border-radius: 50%;
  margin: 0 auto 12px auto;
  display: flex; align-items: center; justify-content: center;
  position: relative;
}
.ri-score-ring::before {
  content: ""; position: absolute; inset: -4px; border-radius: 50%;
  background: radial-gradient(120px 120px at 30% 20%, rgba(76,141,255,0.18), transparent 60%);
  filter: blur(6px); z-index: -1;
}
.ri-score-inner {
  width: 82px; height: 82px; border-radius: 50%;
  background: #0A1120;
  border: 1px solid rgba(148,163,184,0.12);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.ri-score-value { font-size: 1.55rem; font-weight: 800; color: #EEF2F8; line-height: 1.5; font-variant-numeric: tabular-nums; }
.ri-score-max { font-size: 0.66rem; color: #5D6B8A; font-weight: 600; margin-top: 3px; }
.ri-score-label { font-size: 0.68rem; font-weight: 600; color: #8B99B5; text-transform: uppercase; letter-spacing: 0.07em; }
.ri-score-status { font-size: 0.82rem; font-weight: 700; margin-top: 8px; }

/* ============================================================
   PLOTLY CHART SHELL
   ============================================================ */
[data-testid="stPlotlyChart"] {
  background: linear-gradient(180deg, rgba(20,29,51,0.5) 0%, rgba(14,21,38,0.75) 100%);
  border: 1px solid rgba(148,163,184,0.11);
  border-radius: 14px;
  padding: 8px 6px 2px 6px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.22), 0 8px 24px rgba(0,0,0,0.18);
  transition: border-color 0.18s ease;
}
[data-testid="stPlotlyChart"]:hover { border-color: rgba(76,141,255,0.3); }
.js-plotly-plot .plotly .modebar { right: 4px; top: 4px; }

/* ============================================================
   BUTTONS
   ============================================================ */
.stButton > button, [data-testid="stBaseButton-primary"], [data-testid="stDownloadButton"],
[data-testid="stFormSubmitButton"] button {
  border-radius: 9px;
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease, border-color 0.15s ease;
}
.stButton > button:hover, [data-testid="stBaseButton-primary"]:hover,
[data-testid="stDownloadButton"]:hover {
  transform: translateY(-1px);
}
[data-testid="stBaseButton-primary"], [data-testid="stDownloadButton"] {
  background: linear-gradient(135deg, #4C8DFF 0%, #6A6CF0 100%);
  border: none;
  box-shadow: 0 4px 16px rgba(76,141,255,0.28);
}
[data-testid="stBaseButton-primary"]:hover, [data-testid="stDownloadButton"]:hover {
  background: linear-gradient(135deg, #5b9aff 0%, #7b7cf4 100%);
  box-shadow: 0 6px 20px rgba(76,141,255,0.38);
}
.stButton > button[kind="secondary"] { background: rgba(20,29,51,0.85); border-color: rgba(148,163,184,0.18); }
.stButton > button[kind="secondary"]:hover { border-color: rgba(76,141,255,0.4); color: #EEF2F8; }

/* ============================================================
   FORM CONTROLS
   ============================================================ */
[data-baseweb="select"] > div,
[data-baseweb="input"],
[data-testid="stDateInput"] [data-baseweb="input"],
[data-testid="stTextInput"] input {
  background-color: rgba(10,17,32,0.9) !important;
  border-color: rgba(148,163,184,0.18) !important;
  border-radius: 8px !important;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
[data-baseweb="select"] > div:focus-within,
[data-baseweb="input"]:focus-within,
[data-testid="stTextInput"] input:focus-within {
  border-color: rgba(76,141,255,0.6) !important;
  box-shadow: 0 0 0 3px rgba(76,141,255,0.15) !important;
}
[data-baseweb="select"] span, [data-baseweb="select"] input,
[data-baseweb="input"] input, [data-baseweb="input"] textarea,
[data-testid="stTextInput"] input { color: #EEF2F8 !important; }

[data-testid="stSelectbox"] label, [data-testid="stDateInput"] label,
[data-testid="stTextInput"] label, [data-testid="stMultiselect"] label,
[data-testid="stSlider"] label, [data-testid="stRadio"] label > div,
[data-testid="stCheckbox"] label > div {
  color: #8B99B5 !important;
  font-size: 0.8rem !important;
  font-weight: 600 !important;
}

[data-testid="stSlider"] [data-testid="stSliderThumbValue"] { color: #EEF2F8; font-weight: 600; }
[data-testid="stSlider"] [role="slider"] { box-shadow: 0 2px 8px rgba(0,0,0,0.3); }

[data-testid="stCheckbox"] span[role="checkbox"] { border-radius: 5px; }

[data-testid="stFileUploaderDropzone"] {
  background: rgba(20,29,51,0.45) !important;
  border: 1px dashed rgba(148,163,184,0.25) !important;
  border-radius: 12px !important;
  transition: border-color 0.15s ease;
}
[data-testid="stFileUploaderDropzone"]:hover { border-color: rgba(76,141,255,0.5) !important; }

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: 6px; }
[data-testid="stTabs"] [data-baseweb="tab"] {
  border-radius: 8px; padding: 6px 14px;
  color: #8B99B5; font-weight: 600; font-size: 0.84rem;
  transition: color 0.15s ease, background 0.15s ease;
}
[data-testid="stTabs"] [aria-selected="true"] {
  background: rgba(76,141,255,0.12);
  color: #EEF2F8;
}

/* Expanders */
[data-testid="stExpander"] {
  background: rgba(14,21,38,0.7);
  border: 1px solid rgba(148,163,184,0.11);
  border-radius: 12px;
  overflow: hidden;
}
[data-testid="stExpander"] summary { font-weight: 600; color: #D7E0EE; }

/* Alerts */
[data-testid="stAlert"] { border-radius: 12px; border-width: 1px; }

/* Captions / helpers */
[data-testid="stCaptionContainer"] p { color: #8B99B5; }
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li, [data-testid="stMarkdownContainer"] td { color: #C3CEDA; }
[data-testid="stMarkdownContainer"] strong { color: #EEF2F8; }

hr { border-color: rgba(148,163,184,0.09) !important; }

/* ============================================================
   DATAFRAME
   ============================================================ */
[data-testid="stDataFrame"] {
  border: 1px solid rgba(148,163,184,0.11);
  border-radius: 12px;
  overflow: hidden;
  background: rgba(14,21,38,0.6);
  box-shadow: 0 1px 2px rgba(0,0,0,0.2), 0 8px 24px rgba(0,0,0,0.16);
}
[data-testid="stDataFrame"] [data-testid="stElementContainer"] { max-height: 460px; }
[data-testid="stDataFrame"] canvas { border-radius: 12px; }

/* ============================================================
   CHAT (AI ANALYST)
   ============================================================ */
[data-testid="stChatMessage"] {
  border-radius: 14px;
  padding: 12px 16px;
  margin-bottom: 10px;
  border: 1px solid rgba(148,163,184,0.10);
  background: rgba(20,29,51,0.6);
  animation: ri-fade-up 0.3s ease both;
}
@keyframes ri-fade-up {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  background: rgba(76,141,255,0.10);
  border-color: rgba(76,141,255,0.22);
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p { color: #D7E0EE; line-height: 1.6; }
[data-testid="stChatInput"] {
  border: 1px solid rgba(148,163,184,0.16);
  border-radius: 14px;
  background: rgba(10,17,32,0.9);
}
[data-testid="stChatInput"]:focus-within {
  border-color: rgba(76,141,255,0.6);
  box-shadow: 0 0 0 3px rgba(76,141,255,0.15);
}

/* ---------- AI suggestion chips ---------- */
.ri-chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 6px 0 16px 0; }
.ri-sugg {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 7px 14px; border-radius: 999px;
  background: rgba(20,29,51,0.8);
  border: 1px solid rgba(148,163,184,0.16);
  color: #C3CEDA; font-size: 0.8rem; font-weight: 600;
  cursor: pointer; user-select: none;
  transition: transform 0.15s ease, border-color 0.15s ease, background 0.15s ease;
}
.ri-sugg:hover {
  transform: translateY(-1px);
  border-color: rgba(76,141,255,0.45);
  background: rgba(76,141,255,0.10);
  color: #EEF2F8;
}
.ri-sugg svg { width: 14px; height: 14px; color: #4C8DFF; }

/* ---------- AI evidence panel ---------- */
.ri-evidence {
  margin-top: 12px;
  border-top: 1px solid rgba(148,163,184,0.12);
  padding-top: 10px;
}
.ri-evidence-label {
  font-size: 0.66rem; font-weight: 700; color: #5D6B8A;
  text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px;
}
.ri-evidence-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.ri-evidence-item {
  display: flex; align-items: baseline; gap: 8px;
  padding: 5px 10px; border-radius: 8px;
  background: rgba(10,17,32,0.75);
  border: 1px solid rgba(148,163,184,0.12);
}
.ri-evidence-k { font-size: 0.7rem; font-weight: 600; color: #8B99B5; text-transform: uppercase; letter-spacing: 0.05em; }
.ri-evidence-v { font-size: 0.82rem; font-weight: 700; color: #EEF2F8; font-variant-numeric: tabular-nums; }

/* ---------- AI answer card ---------- */
.ri-ai-answer { line-height: 1.65; }

/* ============================================================
   ANOMALY CARDS
   ============================================================ */
.ri-anomaly {
  border-radius: 12px;
  border: 1px solid rgba(148,163,184,0.13);
  background: linear-gradient(180deg, rgba(20,29,51,0.75), rgba(14,21,38,0.9));
  padding: 16px 18px;
  margin-bottom: 12px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.22), 0 8px 24px rgba(0,0,0,0.18);
  transition: transform 0.15s ease, border-color 0.15s ease;
}
.ri-anomaly:hover { transform: translateY(-1px); border-color: rgba(76,141,255,0.3); }
.ri-anomaly-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 10px; }
.ri-anomaly-title { font-size: 0.95rem; font-weight: 700; color: #EEF2F8; display: flex; align-items: center; gap: 9px; }
.ri-anomaly-title svg { width: 16px; height: 16px; }
.ri-anomaly-title.up svg { color: #FBBF24; }
.ri-anomaly-title.down svg { color: #F87171; }
.ri-anomaly-date { font-size: 0.78rem; color: #8B99B5; font-weight: 600; font-variant-numeric: tabular-nums; }
.ri-anomaly-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 10px; }
.ri-anomaly-stat { background: rgba(10,17,32,0.7); border: 1px solid rgba(148,163,184,0.10); border-radius: 9px; padding: 8px 10px; }
.ri-anomaly-k { font-size: 0.64rem; font-weight: 600; color: #5D6B8A; text-transform: uppercase; letter-spacing: 0.06em; }
.ri-anomaly-v { font-size: 0.9rem; font-weight: 700; color: #EEF2F8; margin-top: 2px; font-variant-numeric: tabular-nums; }
.ri-anomaly-drivers { margin-top: 4px; }
.ri-anomaly-driver {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 0.76rem; color: #C3CEDA; font-weight: 500;
  background: rgba(76,141,255,0.08); border: 1px solid rgba(76,141,255,0.14);
  border-radius: 7px; padding: 3px 9px; margin: 0 6px 6px 0;
}
.ri-anomaly-driver svg { width: 11px; height: 11px; color: #4C8DFF; }

/* ============================================================
   STATUS LIST ITEM (quality checklist)
   ============================================================ */
.ri-check-item {
  display: flex; align-items: flex-start; gap: 11px;
  padding: 9px 4px;
  border-bottom: 1px solid rgba(148,163,184,0.07);
}
.ri-check-item:last-child { border-bottom: none; }
.ri-check-icon { width: 22px; height: 22px; flex-shrink: 0; margin-top: 1px; display: flex; align-items: center; justify-content: center; }
.ri-check-icon svg { width: 16px; height: 16px; }
.ri-check-icon.passed   { color: #34D399; }
.ri-check-icon.warning  { color: #FBBF24; }
.ri-check-icon.critical { color: #F87171; }
.ri-check-icon.info     { color: #4C8DFF; }
.ri-check-text b { font-size: 0.84rem; color: #E6EDF7; font-weight: 600; display: block; }
.ri-check-text span { font-size: 0.78rem; color: #8B99B5; }

/* ============================================================
   INSIGHT CARDS
   ============================================================ */
.ri-insight {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 16px; border-radius: 12px;
  background: linear-gradient(180deg, rgba(20,29,51,0.65) 0%, rgba(14,21,38,0.88) 100%);
  border: 1px solid rgba(148,163,184,0.11);
  margin-bottom: 8px;
  transition: transform 0.15s ease, border-color 0.15s ease;
}
.ri-insight:hover { transform: translateY(-1px); border-color: rgba(76,141,255,0.28); }
.ri-insight-icon {
  width: 36px; height: 36px; border-radius: 10px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.ri-insight-icon svg { width: 17px; height: 17px; }
.ri-insight-icon.green  { background: rgba(52,211,153,0.12); border: 1px solid rgba(52,211,153,0.22); color: #34D399; }
.ri-insight-icon.amber  { background: rgba(251,191,36,0.12); border: 1px solid rgba(251,191,36,0.22); color: #FBBF24; }
.ri-insight-icon.red    { background: rgba(248,113,113,0.12); border: 1px solid rgba(248,113,113,0.22); color: #F87171; }
.ri-insight-icon.blue   { background: rgba(76,141,255,0.12); border: 1px solid rgba(76,141,255,0.22); color: #4C8DFF; }
.ri-insight-icon.violet { background: rgba(139,92,246,0.12); border: 1px solid rgba(139,92,246,0.22); color: #8B5CF6; }
.ri-insight-body { flex: 1; min-width: 0; }
.ri-insight-label { font-size: 0.66rem; font-weight: 700; color: #5D6B8A; text-transform: uppercase; letter-spacing: 0.09em; }
.ri-insight-value { font-size: 0.95rem; font-weight: 700; color: #EEF2F8; margin-top: 2px; }
.ri-insight-note { font-size: 0.74rem; color: #8B99B5; margin-top: 1px; }

/* ============================================================
   EMPTY STATE
   ============================================================ */
.ri-empty {
  text-align: center;
  padding: 44px 24px;
  border: 1px dashed rgba(148,163,184,0.18);
  border-radius: 14px;
  background: rgba(14,21,38,0.5);
  margin: 8px 0;
}
.ri-empty-icon {
  width: 54px; height: 54px; border-radius: 16px; margin: 0 auto 14px auto;
  background: rgba(76,141,255,0.10); border: 1px solid rgba(76,141,255,0.2);
  display: flex; align-items: center; justify-content: center; color: #4C8DFF;
}
.ri-empty-icon svg { width: 26px; height: 26px; }
.ri-empty-title { font-size: 1.05rem; font-weight: 700; color: #E6EDF7; }
.ri-empty-msg { font-size: 0.85rem; color: #8B99B5; margin-top: 6px; max-width: 480px; margin-left: auto; margin-right: auto; }

/* ============================================================
   SIDEBAR
   ============================================================ */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0A0F1A 0%, #080C14 100%);
  border-right: 1px solid rgba(148,163,184,0.09);
  width: 264px !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0.9rem; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #C3CEDA; }
[data-testid="stSidebar"] .stCaption p { color: #5D6B8A; }

.ri-sb-brand { display: flex; align-items: center; gap: 11px; padding: 4px 6px 16px 6px; }
.ri-sb-logo {
  width: 38px; height: 38px; border-radius: 11px; flex-shrink: 0;
  background: linear-gradient(135deg, #4C8DFF 0%, #7C5CFF 100%);
  display: flex; align-items: center; justify-content: center; color: #fff;
  box-shadow: 0 4px 16px rgba(76,141,255,0.35);
}
.ri-sb-logo svg { width: 20px; height: 20px; }
.ri-sb-title { font-weight: 700; font-size: 0.98rem; color: #EEF2F8; letter-spacing: -0.01em; line-height: 1.2; }
.ri-sb-tagline { font-size: 0.68rem; color: #5D6B8A; font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase; }

.ri-sb-label {
  font-size: 0.66rem; font-weight: 700; color: #5D6B8A;
  text-transform: uppercase; letter-spacing: 0.11em;
  margin: 14px 6px 8px 6px;
}

.ri-nav { display: flex; flex-direction: column; gap: 2px; }
.ri-nav-item {
  display: flex; align-items: center; gap: 11px;
  width: 100%;
  padding: 8px 12px;
  border: 1px solid transparent;
  border-radius: 9px;
  background: transparent;
  color: #8B99B5;
  font-family: 'Inter', sans-serif;
  font-size: 0.86rem; font-weight: 500;
  text-align: left;
  cursor: pointer;
  transition: background 0.14s ease, color 0.14s ease, border-color 0.14s ease;
}
.ri-nav-item svg { width: 16px; height: 16px; flex-shrink: 0; }
.ri-nav-item:hover { background: rgba(76,141,255,0.08); color: #C3CEDA; }
.ri-nav-item.active {
  background: linear-gradient(90deg, rgba(76,141,255,0.16), rgba(76,141,255,0.05));
  border-color: rgba(76,141,255,0.32);
  color: #EEF2F8; font-weight: 600;
  box-shadow: 0 0 16px rgba(76,141,255,0.18), inset 3px 0 0 #4C8DFF;
}
.ri-nav-item.active svg { color: #4C8DFF; }

.ri-sb-dataset {
  background: rgba(20,29,51,0.6);
  border: 1px solid rgba(148,163,184,0.12);
  border-radius: 12px;
  padding: 13px 14px;
  margin-bottom: 8px;
}
.ri-sb-ds-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 8px; }
.ri-sb-ds-name { font-size: 0.84rem; font-weight: 700; color: #E6EDF7; }
.ri-sb-ds-meta { font-size: 0.72rem; color: #8B99B5; font-weight: 500; margin-top: 3px; }
.ri-sb-bar { height: 5px; border-radius: 5px; background: rgba(148,163,184,0.10); overflow: hidden; margin: 8px 0 6px 0; }
.ri-sb-fill { height: 100%; border-radius: 5px; transition: width 0.4s ease; }
.ri-sb-score-line { display: flex; justify-content: space-between; align-items: baseline; font-size: 0.72rem; }
.ri-sb-score-label { color: #8B99B5; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
.ri-sb-score-num { color: #EEF2F8; font-weight: 700; font-variant-numeric: tabular-nums; }

.ri-sb-ai {
  display: flex; align-items: center; gap: 9px;
  padding: 10px 12px; border-radius: 11px;
  background: rgba(139,92,246,0.08);
  border: 1px solid rgba(139,92,246,0.2);
  margin-bottom: 6px;
}
.ri-sb-ai svg { width: 15px; height: 15px; color: #8B5CF6; flex-shrink: 0; }
.ri-sb-ai b { font-size: 0.78rem; color: #E6EDF7; font-weight: 600; display: block; }
.ri-sb-ai span { font-size: 0.68rem; color: #8B99B5; }

/* hide default radio/label chrome inside styled custom controls */
.ri-sidebar-divider { border-top: 1px solid rgba(148,163,184,0.08); margin: 12px 0; }

/* ============================================================
   FOOTER
   ============================================================ */
.ri-footer {
  margin-top: 52px;
  padding: 14px 18px;
  border-top: 1px solid rgba(148,163,184,0.08);
  display: flex; align-items: center; justify-content: center; gap: 10px;
  color: #5D6B8A; font-size: 0.76rem; font-weight: 500; flex-wrap: wrap;
}
.ri-footer svg { width: 13px; height: 13px; color: #4C8DFF; }

/* ============================================================
   RESPONSIVE
   ============================================================ */
@media (max-width: 1100px) {
  .ri-kpi-value { font-size: 1.45rem; }
  .ri-hero-title { font-size: 1.45rem; }
  [data-testid="stSidebar"] { width: 236px !important; }
}
@media (max-width: 700px) {
  .ri-hero { padding: 20px; }
  .ri-hero-title { font-size: 1.25rem; }
  .ri-app-header { flex-direction: column; align-items: flex-start; }
  .ri-header-right { width: 100%; justify-content: flex-start; }
  .ri-anomaly-grid { grid-template-columns: 1fr 1fr; }
}

/* ============================================================
   MICRO-INTERACTIONS
   ============================================================ */
.ri-panel:hover {
  border-color: rgba(76,141,255,0.22);
  box-shadow: 0 2px 4px rgba(0,0,0,0.3), 0 10px 28px rgba(0,0,0,0.32);
}
.ri-insight:hover {
  border-color: rgba(76,141,255,0.28);
}
@keyframes ri-fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.ri-kpi, .ri-panel, .ri-anomaly, .ri-insight {
  animation: ri-fade-in 0.35s ease both;
}
.ri-anomaly:nth-child(2) { animation-delay: 0.05s; }
.ri-anomaly:nth-child(3) { animation-delay: 0.10s; }

/* Status pulse for the live data indicator */
@keyframes ri-glow-pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}
.ri-pill.live .ri-dot {
  animation: ri-pulse 2.4s ease-out infinite, ri-glow-pulse 1.8s ease-in-out infinite;
}

/* Smooth chart container transitions */
[data-testid="stPlotlyChart"] {
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stPlotlyChart"]:hover {
  box-shadow: 0 2px 4px rgba(0,0,0,0.3), 0 12px 30px rgba(0,0,0,0.32);
}

/* ============================================================
   ACCESSIBILITY
   ============================================================ */
:focus-visible { outline: 2px solid rgba(76,141,255,0.7); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
"""


def apply_global_css() -> None:
    """Injects the global design system CSS once per session."""
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)