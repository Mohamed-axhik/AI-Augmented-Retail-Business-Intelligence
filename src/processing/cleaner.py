import pandas as pd
import numpy as np
from typing import Dict

def clean_dataset(df: pd.DataFrame, mapping: Dict[str, str], drop_duplicates: bool = True) -> pd.DataFrame:
    """
    Cleans raw DataFrame based on schema mapping.
    Performs string trimming, date parsing, and e-commerce transaction corrections:
    - Rows with non-positive unit prices are dropped (adjustment / bad data).
    - Zero-quantity rows are dropped.
    - Negative quantities are preserved and treated as returns / refunds.
    - Blank or placeholder ('?') product names are dropped.
    """
    df_clean = df.copy()

    # Trim whitespace from all string columns
    for col in df_clean.select_dtypes(include=['object', 'string']).columns:
        df_clean[col] = df_clean[col].astype(str).str.strip()

    # Drop duplicate rows if requested
    if drop_duplicates:
        df_clean = df_clean.drop_duplicates()

    # Date parsing
    date_col = mapping.get("date")
    if date_col and date_col in df_clean.columns:
        df_clean[date_col] = pd.to_datetime(df_clean[date_col], errors='coerce')
        # Drop rows where date could not be parsed
        df_clean = df_clean.dropna(subset=[date_col])

    # Clean numeric columns
    numeric_fields = ["quantity", "unit_price", "revenue", "cost", "inventory"]
    for field in numeric_fields:
        col = mapping.get(field)
        if col and col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

    # Drop adjustment / corrupted rows: unit price must be positive
    price_col = mapping.get("unit_price")
    if price_col and price_col in df_clean.columns:
        df_clean = df_clean[df_clean[price_col] > 0]

    # Drop zero-quantity rows (meaningless transactions)
    qty_col = mapping.get("quantity")
    if qty_col and qty_col in df_clean.columns:
        df_clean = df_clean[df_clean[qty_col] != 0]

    # Drop blank or placeholder product names
    name_col = mapping.get("product_name")
    if name_col and name_col in df_clean.columns:
        names = df_clean[name_col].astype(str).str.strip()
        df_clean = df_clean[~names.isin(["", "nan", "None", "?"])]

    return df_clean