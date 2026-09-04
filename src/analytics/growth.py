import pandas as pd
from typing import Dict, Any, Optional

def calculate_growth_rates(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes Month-over-Month (MoM) and Year-over-Year (YoY) revenue growth rates.
    """
    if df.empty or "date" not in df.columns or "revenue" not in df.columns:
        return {
            "mom_growth_pct": None,
            "mom_revenue_delta": None,
            "yoy_growth_pct": None,
            "yoy_revenue_delta": None,
            "latest_month": None,
            "prev_month": None
        }

    # Resample to monthly revenue
    monthly_rev = df.set_index("date").resample("MS")["revenue"].sum().reset_index()
    monthly_rev = monthly_rev[monthly_rev["revenue"] > 0]

    if len(monthly_rev) < 2:
        return {
            "mom_growth_pct": None,
            "mom_revenue_delta": None,
            "yoy_growth_pct": None,
            "yoy_revenue_delta": None,
            "latest_month": None,
            "prev_month": None
        }

    latest = monthly_rev.iloc[-1]
    prev = monthly_rev.iloc[-2]

    latest_rev = latest["revenue"]
    prev_rev = prev["revenue"]

    mom_pct = ((latest_rev - prev_rev) / prev_rev) * 100.0 if prev_rev > 0 else 0.0
    mom_delta = latest_rev - prev_rev

    # YoY calculation if data spans >= 13 months
    yoy_pct = None
    yoy_delta = None
    if len(monthly_rev) >= 13:
        year_ago = monthly_rev.iloc[-13]
        year_ago_rev = year_ago["revenue"]
        yoy_pct = ((latest_rev - year_ago_rev) / year_ago_rev) * 100.0 if year_ago_rev > 0 else 0.0
        yoy_delta = latest_rev - year_ago_rev

    return {
        "mom_growth_pct": round(mom_pct, 2),
        "mom_revenue_delta": round(mom_delta, 2),
        "yoy_growth_pct": round(yoy_pct, 2) if yoy_pct is not None else None,
        "yoy_revenue_delta": round(yoy_delta, 2) if yoy_delta is not None else None,
        "latest_month": latest["date"].strftime("%B %Y"),
        "prev_month": prev["date"].strftime("%B %Y")
    }
