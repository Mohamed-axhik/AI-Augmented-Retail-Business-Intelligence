from typing import Union, Optional

CURRENCY_SYMBOL = "£"  # Online Retail II dataset is denominated in GBP

def format_currency(amount: Optional[Union[int, float]], symbol: str = CURRENCY_SYMBOL) -> str:
    """Formats numeric amounts into currency representation."""
    if amount is None:
        return "N/A"
    
    val = float(amount)
    abs_val = abs(val)
    sign = "-" if val < 0 else ""

    if abs_val >= 10_000_000: # 1 Crore / 10M
        return f"{sign}{symbol}{abs_val / 1_000_000:.2f}M"
    elif abs_val >= 100_000: # 1 Lakh / 100K
        return f"{sign}{symbol}{abs_val / 1_000:.1f}K"
    else:
        return f"{sign}{symbol}{abs_val:,.2f}"

def format_pct(val: Optional[Union[int, float]], include_sign: bool = True) -> str:
    """Formats values as percentages."""
    if val is None:
        return "N/A"
    v = float(val)
    sign = "+" if (v > 0 and include_sign) else ""
    return f"{sign}{v:.1f}%"

def format_number(val: Optional[Union[int, float]]) -> str:
    """Formats plain numbers with comma separators or compact units."""
    if val is None:
        return "0"
    v = float(val)
    if abs(v) >= 1_000_000:
        return f"{v / 1_000_000:.2f}M"
    elif abs(v) >= 1_000:
        return f"{v:,.0f}"
    else:
        return f"{v:,.0f}"
