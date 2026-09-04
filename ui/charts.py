"""Centralized Plotly chart builders.

Every chart in the application is produced here and styled through the shared
`premium_dark_theme()` in ui.theme.  Charts in a row share equal heights via the
CH tokens so top/bottom edges always align.  Defaults are never injected by
Plotly's own themes.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ui.theme import C, CH, FONT, style_figure, premium_dark_theme

CURRENCY_SYMBOL = "\u00a3"
CURRENCY_LABEL = f"Revenue ({CURRENCY_SYMBOL})"

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _money_tick():
    return {"tickformat": f"{CURRENCY_SYMBOL}~s", "tickprefix": "", "separatethousands": True}


def _date_hover_format(freq: str) -> str:
    if freq in ("MS", "QS", "W"):
        return "%b %Y"
    return "%b %d, %Y"


def _apply_axes(fig: go.Figure, x_title: str | None, y_title: str | None,
                money_y: bool = True) -> go.Figure:
    layout = {}
    if x_title:
        layout["xaxis_title"] = x_title
    if y_title:
        layout["yaxis_title"] = y_title
    if money_y:
        layout["yaxis"] = {"tickformat": f"{CURRENCY_SYMBOL}~s"}
    fig.update_layout(**layout)
    return fig


# ---------------------------------------------------------------------------
# Revenue (PRIMARY hero chart)
# ---------------------------------------------------------------------------
def render_revenue_trend_chart(sales_df: pd.DataFrame, freq: str = "D") -> go.Figure:
    """Hero revenue visualization: clean line, subtle area fill, MA baseline."""
    fig = go.Figure()
    dates = sales_df["date"]

    fig.add_trace(go.Scatter(
        x=dates,
        y=sales_df["revenue"],
        name="Revenue",
        mode="lines",
        line=dict(color=C.ACCENT, width=2.2),
        fill="tozeroy",
        fillcolor="rgba(76,141,255,0.10)",
        hovertemplate=f"{CURRENCY_SYMBOL}%{{y:,.0f}}<extra></extra>",
    ))

    if "revenue_7d_ma" in sales_df.columns:
        fig.add_trace(go.Scatter(
            x=dates,
            y=sales_df["revenue_7d_ma"],
            name="7-Day Avg",
            mode="lines",
            line=dict(color=C.ACCENT_2, width=1.6, dash="dot"),
            hovertemplate=f"{CURRENCY_SYMBOL}%{{y:,.0f}}<extra></extra>",
        ))

    fig.update_xaxes(rangeslider_visible=False)
    hover_fmt = _date_hover_format(freq)
    fig.update_layout(
        hovermode="x unified",
        yaxis=dict(tickformat=f"{CURRENCY_SYMBOL}~s"),
    )
    fig.update_traces(
        hovertemplate=(
            f"<b>%{{x|{hover_fmt}}}</b><br>"
            + f"{CURRENCY_SYMBOL}%{{y:,.0f}}<extra></extra>"
        )
        if freq != "D"
        else None,
        selector={"name": "Revenue"},
    )
    return style_figure(fig, height=CH.PRIMARY, xaxis_title="Date", yaxis_title=CURRENCY_LABEL)


def render_sales_performance_chart(sales_df: pd.DataFrame, freq_label: str = "Monthly",
                                   freq: str = "MS") -> go.Figure:
    """Revenue + profit performance line chart (Sales Analytics page)."""
    fig = go.Figure()
    has_profit = "profit" in sales_df.columns and not sales_df["profit"].isnull().all()
    hover_fmt = _date_hover_format(freq)

    fig.add_trace(go.Scatter(
        x=sales_df["date"], y=sales_df["revenue"], name="Revenue",
        mode="lines", line=dict(color=C.ACCENT, width=2.2),
        fill="tozeroy", fillcolor="rgba(76,141,255,0.10)",
        hovertemplate=f"<b>%{{x|{hover_fmt}}}</b><br>Revenue: {CURRENCY_SYMBOL}%{{y:,.0f}}<extra></extra>",
    ))
    if has_profit:
        fig.add_trace(go.Scatter(
            x=sales_df["date"], y=sales_df["profit"], name="Profit",
            mode="lines", line=dict(color=C.TEAL, width=2),
            hovertemplate=f"<b>%{{x|{hover_fmt}}}</b><br>Profit: {CURRENCY_SYMBOL}%{{y:,.0f}}<extra></extra>",
        ))
    return style_figure(
        fig, height=CH.SECONDARY,
        xaxis_title="Date", yaxis_title=CURRENCY_LABEL,
        yaxis=dict(tickformat=f"{CURRENCY_SYMBOL}~s"),
    )


def render_orders_chart(sales_df: pd.DataFrame, freq_label: str = "Monthly") -> go.Figure:
    """Order volume bar chart."""
    fig = go.Figure(go.Bar(
        x=sales_df["date"], y=sales_df["orders"],
        marker_color=C.ACCENT_2, marker_line=dict(width=0), opacity=0.85,
        hovertemplate=f"<b>%{{x|%b %Y}}</b><br>Orders: %{{y:,.0f}}<extra></extra>",
    ))
    return style_figure(fig, height=CH.TERTIARY, xaxis_title="", yaxis_title="Orders",
                        yaxis=dict(tickformat=",.0f"))


def render_aov_chart(sales_df: pd.DataFrame, freq_label: str = "Monthly") -> go.Figure:
    """Average order value line chart."""
    fig = go.Figure(go.Scatter(
        x=sales_df["date"], y=sales_df["aov"], name="AOV",
        mode="lines+markers", line=dict(color=C.VIOLET, width=2),
        marker=dict(size=5, color=C.VIOLET),
        hovertemplate=f"<b>%{{x|%b %Y}}</b><br>AOV: {CURRENCY_SYMBOL}%{{y:,.2f}}<extra></extra>",
    ))
    return style_figure(fig, height=CH.TERTIARY, xaxis_title="", yaxis_title="AOV",
                        yaxis=dict(tickformat=f"{CURRENCY_SYMBOL}~s"))


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------
def render_category_donut(cat_df: pd.DataFrame, title: str = "Revenue by Category",
                          height: int = CH.SECONDARY) -> go.Figure:
    """Category revenue contribution donut (restrained palette)."""
    fig = go.Figure(go.Pie(
        labels=cat_df["category"], values=cat_df["revenue"], hole=0.62,
        marker=dict(colors=C.SERIES, line=dict(color=C.BG_CARD, width=2)),
        textinfo="percent", textfont=dict(size=11, color=C.TEXT_PRIMARY),
        hovertemplate="<b>%{label}</b><br>"
                      + f"{CURRENCY_SYMBOL}%{{value:,.0f}} ({'%{percent}'})<extra></extra>",
    ))
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center"),
        annotations=[dict(
            text=f"<b>{cat_df['revenue'].sum():,.0f}</b>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(family=FONT.SANS, size=15, color=C.TEXT_PRIMARY),
        )],
    )
    return style_figure(fig, height=height)


def render_category_bar(cat_df: pd.DataFrame) -> go.Figure:
    """Horizontal ranked category revenue bars."""
    df = cat_df.sort_values("revenue", ascending=True)
    fig = go.Figure(go.Bar(
        x=df["revenue"], y=df["category"], orientation="h",
        marker_color=C.ACCENT, marker_line=dict(width=0),
        hovertemplate=f"{CURRENCY_SYMBOL}%{{x:,.0f}}<extra></extra>",
    ))
    return style_figure(fig, height=CH.SECONDARY, xaxis_title=CURRENCY_LABEL, yaxis_title="",
                        yaxis=dict(tickformat="~s", autorange="reversed"))


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------
def render_top_products_bar(top_prods: pd.DataFrame, title: str = "Top Products by Revenue") -> go.Figure:
    """Horizontal top-N products bar, colored by category (single-hue restrained)."""
    df = top_prods.sort_values("revenue", ascending=True)
    fig = go.Figure(go.Bar(
        x=df["revenue"], y=df["product_name"], orientation="h",
        marker_color=C.ACCENT, marker_line=dict(width=0),
        texttemplate=f"{CURRENCY_SYMBOL}%{{x:,.0f}}", textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>" + f"{CURRENCY_SYMBOL}%{{x:,.0f}}<extra></extra>",
    ))
    fig.update_layout(
        xaxis=dict(tickformat=f"{CURRENCY_SYMBOL}~s"),
        margin=dict(l=8, r=70, t=10, b=8),
    )
    return style_figure(fig, height=CH.SECONDARY, xaxis_title=CURRENCY_LABEL, yaxis_title="")


def render_bottom_products_bar(bottom_prods: pd.DataFrame, title: str = "Bottom Products by Revenue") -> go.Figure:
    """Horizontal bottom-N products bar (muted red tone)."""
    df = bottom_prods.sort_values("revenue", ascending=True)
    fig = go.Figure(go.Bar(
        x=df["revenue"], y=df["product_name"], orientation="h",
        marker_color=C.ANOMALY_DOWN, marker_line=dict(width=0), opacity=0.85,
        texttemplate=f"{CURRENCY_SYMBOL}%{{x:,.0f}}", textposition="outside",
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>" + f"{CURRENCY_SYMBOL}%{{x:,.0f}}<extra></extra>",
    ))
    fig.update_layout(
        xaxis=dict(tickformat=f"{CURRENCY_SYMBOL}~s"),
        margin=dict(l=8, r=70, t=10, b=8),
    )
    return style_figure(fig, height=CH.SECONDARY, xaxis_title=CURRENCY_LABEL, yaxis_title="")


def render_pareto_chart(prod_df: pd.DataFrame, title: str = "Pareto Cumulative Revenue Curve") -> go.Figure:
    """Pareto 80/20: revenue bars + cumulative share line on a secondary axis."""
    df = prod_df.head(50)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["product_name"], y=df["revenue"], name="Revenue",
        marker_color=C.ACCENT, marker_line=dict(width=0), opacity=0.85,
        hovertemplate=f"{CURRENCY_SYMBOL}%{{y:,.0f}}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["product_name"], y=df["cum_revenue_share_pct"], name="Cumulative Share %",
        yaxis="y2", mode="lines+markers",
        line=dict(color=C.WARNING, width=2), marker=dict(size=4, color=C.WARNING),
        hovertemplate="%{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(y=80, line_dash="dash", line_color="rgba(248,113,113,0.45)", line_width=1)
    fig.update_layout(
        xaxis=dict(tickangle=-45, tickfont=dict(size=9, color=C.TICK)),
        yaxis=dict(tickformat=f"{CURRENCY_SYMBOL}~s"),
        yaxis2=dict(title="Cumulative Share %", overlaying="y", side="right",
                    range=[0, 105], tickfont=dict(size=10, color=C.TICK),
                    gridcolor="rgba(0,0,0,0)"),
        legend=dict(orientation="h", y=1.08, x=0),
    )
    return style_figure(fig, height=CH.PRIMARY)


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------
def render_top_customers_bar(top_customers: pd.DataFrame) -> go.Figure:
    """Horizontal top customers bar."""
    df = top_customers.sort_values("revenue", ascending=True)
    fig = go.Figure(go.Bar(
        x=df["revenue"], y=df["customer_id"].astype(str), orientation="h",
        marker_color=C.ACCENT_2, marker_line=dict(width=0), opacity=0.9,
        hovertemplate="<b>%{y}</b><br>" + f"{CURRENCY_SYMBOL}%{{x:,.0f}}<extra></extra>",
    ))
    return style_figure(fig, height=CH.SECONDARY, xaxis_title=CURRENCY_LABEL, yaxis_title="")


def render_customer_acquisition_chart(trend_df: pd.DataFrame) -> go.Figure:
    """New customer bars + cumulative line on secondary axis."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=trend_df["date"], y=trend_df["new_customers"], name="New Customers",
        marker_color=C.ACCENT, marker_line=dict(width=0), opacity=0.85,
        hovertemplate="<b>%{x|%b %Y}</b><br>New: %{y:,.0f}<extra></extra>",
    ))
    if "cumulative_customers" in trend_df.columns:
        fig.add_trace(go.Scatter(
            x=trend_df["date"], y=trend_df["cumulative_customers"],
            name="Cumulative", yaxis="y2", mode="lines",
            line=dict(color=C.VIOLET, width=2),
            hovertemplate="<b>%{x|%b %Y}</b><br>Total: %{y:,.0f}<extra></extra>",
        ))
    fig.update_layout(
        yaxis2=dict(title="", overlaying="y", side="right",
                    tickformat="~s", gridcolor="rgba(0,0,0,0)",
                    tickfont=dict(size=10, color=C.TICK)),
        legend=dict(orientation="h", y=1.08, x=0),
    )
    return style_figure(fig, height=CH.SECONDARY, xaxis_title="", yaxis_title="New Customers")


def render_customer_segments_donut(seg_df: pd.DataFrame) -> go.Figure:
    """Customer loyalty segment donut."""
    fig = go.Figure(go.Pie(
        labels=seg_df["segment"], values=seg_df["customers"], hole=0.6,
        marker=dict(colors=[C.VIOLET, C.TEAL, C.ACCENT_2, C.WARNING],
                    line=dict(color=C.BG_CARD, width=2)),
        textinfo="percent", textfont=dict(size=11, color=C.TEXT_PRIMARY),
        hovertemplate="<b>%{label}</b><br>Customers: %{value:,.0f}<extra></extra>",
    ))
    fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center"))
    return style_figure(fig, height=CH.SECONDARY)


def render_customer_concentration_chart(conc_df: pd.DataFrame) -> go.Figure:
    """Cumulative revenue concentration (Lorenz-style) across top customers."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=conc_df["rank"], y=conc_df["cum_share_pct"], mode="lines+markers",
        name="Cumulative Revenue Share %",
        line=dict(color=C.ACCENT, width=2.4),
        marker=dict(size=6, color=C.ACCENT_2, line=dict(color=C.BG_CARD, width=1)),
        hovertemplate="<b>Rank %{x}</b><br>Cumulative: %{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(y=80, line_dash="dash", line_color="rgba(248,113,113,0.45)", line_width=1)
    fig.update_layout(yaxis=dict(range=[0, 105], ticksuffix="%"), xaxis=dict(tickformat="d"))
    return style_figure(fig, height=CH.SECONDARY, xaxis_title="Customer Rank",
                        yaxis_title="Cumulative Revenue Share %")


# ---------------------------------------------------------------------------
# Stores / regions
# ---------------------------------------------------------------------------
def render_region_donut(region_df: pd.DataFrame, title: str = "Revenue by Country") -> go.Figure:
    """Regional / country revenue donut — top 10 + Other."""
    df = region_df.sort_values("revenue", ascending=False).copy()
    if len(df) > 10:
        top10 = df.head(10).copy()
        other_rev = df.iloc[10:]["revenue"].sum()
        other_row = pd.DataFrame([{"region": "Other", "revenue": other_rev}])
        df = pd.concat([top10, other_row], ignore_index=True)
    fig = go.Figure(go.Pie(
        labels=df["region"], values=df["revenue"], hole=0.62,
        marker=dict(colors=C.SERIES, line=dict(color=C.BG_CARD, width=2)),
        textinfo="percent", textfont=dict(size=11, color=C.TEXT_PRIMARY),
        hovertemplate="<b>%{label}</b><br>" + f"{CURRENCY_SYMBOL}%{{value:,.0f}}<extra></extra>",
    ))
    fig.update_layout(showlegend=True, legend=dict(orientation="v", x=1.02, y=0.5))
    return style_figure(fig, height=CH.SECONDARY)


def render_market_bar(region_df: pd.DataFrame) -> go.Figure:
    """Horizontal ranked market revenue bar — top 10 + Other."""
    df = region_df.sort_values("revenue", ascending=False).copy()
    if len(df) > 10:
        top10 = df.head(10).copy()
        other_rev = df.iloc[10:]["revenue"].sum()
        other_row = pd.DataFrame([{"region": "Other", "revenue": other_rev}])
        df = pd.concat([top10, other_row], ignore_index=True)
    df = df.sort_values("revenue", ascending=True)
    fig = go.Figure(go.Bar(
        x=df["revenue"], y=df["region"], orientation="h",
        marker_color=C.ACCENT, marker_line=dict(width=0),
        texttemplate=f"{CURRENCY_SYMBOL}%{{x:,.0f}}", textposition="outside",
        cliponaxis=False,
        hovertemplate=f"{CURRENCY_SYMBOL}%{{x:,.0f}}<extra></extra>",
    ))
    fig.update_layout(margin=dict(l=8, r=70, t=10, b=8))
    return style_figure(fig, height=CH.SECONDARY, xaxis_title=CURRENCY_LABEL, yaxis_title="")


def render_store_bar(store_df: pd.DataFrame) -> go.Figure:
    """Horizontal ranked store revenue bar colored by region."""
    df = store_df.sort_values("revenue", ascending=True)
    color_map = {r: C.SERIES[i % len(C.SERIES)] for i, r in enumerate(store_df["region"].unique())}
    colors = [color_map.get(r, C.ACCENT) for r in df["region"]]
    fig = go.Figure(go.Bar(
        x=df["revenue"], y=df["store"], orientation="h",
        marker_color=colors, marker_line=dict(width=0),
        hovertemplate="<b>%{y}</b><br>" + f"{CURRENCY_SYMBOL}%{{x:,.0f}}<extra></extra>",
    ))
    return style_figure(fig, height=CH.SECONDARY, xaxis_title=CURRENCY_LABEL, yaxis_title="")


# ---------------------------------------------------------------------------
# Anomaly
# ---------------------------------------------------------------------------
def render_anomaly_timeline(daily_df: pd.DataFrame) -> go.Figure:
    """Daily revenue with expected baseline and distinct anomaly markers."""
    fig = go.Figure()
    hover_fmt = "%b %d, %Y"

    fig.add_trace(go.Scatter(
        x=daily_df["date"], y=daily_df["revenue"], name="Revenue",
        mode="lines", line=dict(color=C.ACCENT, width=2),
        fill="tozeroy", fillcolor="rgba(76,141,255,0.08)",
        hovertemplate=f"<b>%{{x|{hover_fmt}}}</b><br>Actual: {CURRENCY_SYMBOL}%{{y:,.0f}}<extra></extra>",
    ))
    if "rolling_mean" in daily_df.columns:
        fig.add_trace(go.Scatter(
            x=daily_df["date"], y=daily_df["rolling_mean"], name="Expected Baseline",
            mode="lines", line=dict(color=C.TEXT_MUTED, width=1.2, dash="dash"),
            hovertemplate=f"<b>%{{x|{hover_fmt}}}</b><br>Expected: {CURRENCY_SYMBOL}%{{y:,.0f}}<extra></extra>",
        ))

    anomalies = daily_df[daily_df["is_anomaly"]]
    if not anomalies.empty:
        up = anomalies[anomalies["revenue"] >= anomalies["rolling_mean"]]
        down = anomalies[anomalies["revenue"] < anomalies["rolling_mean"]]
        if not up.empty:
            fig.add_trace(go.Scatter(
                x=up["date"], y=up["revenue"], name="Spike",
                mode="markers", marker=dict(
                    color=C.ANOMALY_UP, size=9, symbol="diamond",
                    line=dict(color=C.BG_CARD, width=1.5)),
                hovertemplate=f"<b>%{{x|{hover_fmt}}}</b><br>Spike: {CURRENCY_SYMBOL}%{{y:,.0f}}<extra></extra>",
            ))
        if not down.empty:
            fig.add_trace(go.Scatter(
                x=down["date"], y=down["revenue"], name="Dip",
                mode="markers", marker=dict(
                    color=C.ANOMALY_DOWN, size=9, symbol="diamond",
                    line=dict(color=C.BG_CARD, width=1.5)),
                hovertemplate=f"<b>%{{x|{hover_fmt}}}</b><br>Dip: {CURRENCY_SYMBOL}%{{y:,.0f}}<extra></extra>",
            ))

    return style_figure(fig, height=CH.PRIMARY, xaxis_title="Date", yaxis_title=CURRENCY_LABEL,
                        yaxis=dict(tickformat=f"{CURRENCY_SYMBOL}~s"))


def render_anomaly_distribution_chart(daily_df: pd.DataFrame) -> go.Figure:
    """Z-score magnitude bars for anomaly days (intelligence supporting chart)."""
    anom = daily_df[daily_df["is_anomaly"]].sort_values("date")
    if anom.empty:
        return style_figure(go.Figure(), height=CH.TERTIARY)
    colors = [C.ANOMALY_DOWN if z < 0 else C.ANOMALY_UP for z in anom["z_score"]]
    fig = go.Figure(go.Bar(
        x=anom["date"], y=anom["z_score"],
        marker_color=colors, marker_line=dict(width=0),
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>Z-Score: %{y:.2f}<extra></extra>",
    ))
    fig.add_hline(y=0, line_color=C.BORDER_STRONG, line_width=1)
    return style_figure(fig, height=CH.TERTIARY, xaxis_title="", yaxis_title="Z-Score",
                        yaxis=dict(tickformat=".1f"))