import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional

CATEGORY_KEYWORDS = [
    ("Seasonal & Gifts", ["christmas", "halloween", "easter", "valentine", "birthday", "gift", "stocking", "santa", "snowman", "bauble", "christmas craft"]),
    ("Kitchen & Dining", ["mug", "cup", "plate", "bowl", "tray", "jar", "bottle", "canister", "dish", "glass", "spoon", "fork", "knife", "cutlery", "teapot", "coaster", "napkin", "apron", "lunchbox", "measuring", "kitchen", "egg"]),
    ("Home Decor", ["light", "lamp", "candle", "frame", "photo", "mirror", "clock", "vase", "basket", "rug", "mat", "doormat", "cushion", "cover", "curtain", "picture", "ornament", "sculpture", "sign", "decor", "towel", "candleholder", "trinket", "pot", "votive"]),
    ("Toys & Kids", ["toy", "game", "puzzle", "doll", "ball", "building block", "block", "craft", "kids", "children", "baby", "boy", "girl", "play", "duck"]),
    ("Stationery & Cards", ["note", "paper", "pen", "pencil", "book", "diary", "card", "envelope", "sticker", "stationery", "wrap", "letter", "calendar", "postcard"]),
    ("Fashion & Accessories", ["bag", "jewellery", "jewelry", "earring", "necklace", "bracelet", "scarf", "hat", "glove", "t-shirt", "shirt", "dress", "sock", "umbrella", "purse", "wallet", "ring", "brooch"]),
    ("Party Supplies", ["balloon", "party", "bunting", "confetti", "lantern", "crackers", "party popper"]),
    ("Food & Beverage", ["tea", "coffee", "chocolate", "sweet", "biscuit", "cookie", "cake", "food", "snack", "candy", "lollipop", "marshmallow"]),
    ("Shipping & Services", ["postage", "shipping", "carriage", "adjustment", "insurance"]),
]

def _derive_category(product_name: str) -> str:
    """Classifies a product name into a retail category using keyword taxonomy."""
    name = product_name.lower()
    for category, keywords in CATEGORY_KEYWORDS:
        if any(kw in name for kw in keywords):
            return category
    return "General"

def transform_to_canonical(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    """
    Transforms clean DataFrame into standard internal canonical DataFrame schema:
    [date, order_id, product_id, product_name, category, store, region, customer_id,
     quantity, unit_price, revenue, cost, profit, inventory]
    """
    df_std = pd.DataFrame(index=df.index)

    # Date
    date_col = mapping.get("date")
    if date_col and date_col in df.columns:
        df_std["date"] = pd.to_datetime(df[date_col])
    else:
        df_std["date"] = pd.Timestamp.now()

    # Categorical fields with smart defaults
    defaults = {
        "order_id": None, # Dynamic per row if missing
        "product_id": "SKU-GENERIC",
        "product_name": "Unspecified Product",
        "category": None, # Derived from product name if missing
        "store": "Main Store",
        "region": "National",
        "customer_id": "Unspecified"
    }

    for field, default_val in defaults.items():
        col = mapping.get(field)
        if col and col in df.columns:
            fallback = default_val if default_val else "ORD-UNKNOWN"
            raw = df[col]
            if field == "customer_id" and pd.api.types.is_numeric_dtype(raw):
                raw = raw.map(lambda v: f"{int(v)}" if pd.notna(v) else fallback).astype(str)
            else:
                raw = raw.fillna(fallback).astype(str)
            df_std[field] = raw
        else:
            if field == "order_id":
                df_std[field] = "ORD-" + (df.index + 1).astype(str)
            else:
                df_std[field] = default_val

    # Derive product category from product name when no category column exists
    category_col = mapping.get("category")
    if not (category_col and category_col in df.columns):
        df_std["category"] = df_std["product_name"].apply(_derive_category)

    # Numeric fields
    # Quantity
    qty_col = mapping.get("quantity")
    if qty_col and qty_col in df.columns:
        df_std["quantity"] = pd.to_numeric(df[qty_col], errors='coerce').fillna(1.0)
    else:
        df_std["quantity"] = 1.0

    # Unit price
    price_col = mapping.get("unit_price")
    if price_col and price_col in df.columns:
        df_std["unit_price"] = pd.to_numeric(df[price_col], errors='coerce').fillna(0.0)
    else:
        df_std["unit_price"] = 0.0

    # Revenue (Derive if missing)
    rev_col = mapping.get("revenue")
    if rev_col and rev_col in df.columns:
        derived_rev = pd.to_numeric(df[rev_col], errors='coerce')
        # Fill missing values in revenue with quantity * unit_price
        df_std["revenue"] = derived_rev.fillna(df_std["quantity"] * df_std["unit_price"])
    else:
        df_std["revenue"] = df_std["quantity"] * df_std["unit_price"]

    # Cost
    cost_col = mapping.get("cost")
    if cost_col and cost_col in df.columns:
        df_std["cost"] = pd.to_numeric(df[cost_col], errors='coerce')
    else:
        df_std["cost"] = np.nan

    # Profit (Derive if cost is available)
    if not df_std["cost"].isnull().all():
        df_std["profit"] = df_std["revenue"] - (df_std["quantity"] * df_std["cost"])
    else:
        df_std["profit"] = np.nan

    # Inventory
    inv_col = mapping.get("inventory")
    if inv_col and inv_col in df.columns:
        df_std["inventory"] = pd.to_numeric(df[inv_col], errors='coerce')
    else:
        df_std["inventory"] = np.nan

    # Sort chronologically
    df_std = df_std.sort_values("date").reset_index(drop=True)

    return df_std