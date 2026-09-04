from typing import Dict, List, Tuple, Optional
import pandas as pd

# Canonical Schema Definitions
CANONICAL_FIELDS = {
    "date": {"description": "Transaction / Order Date", "required": True, "type": "datetime"},
    "order_id": {"description": "Unique Order ID", "required": False, "type": "string"},
    "product_id": {"description": "Product ID / SKU", "required": False, "type": "string"},
    "product_name": {"description": "Product Name", "required": True, "type": "string"},
    "category": {"description": "Product Category", "required": True, "type": "string"},
    "store": {"description": "Store Name / ID", "required": False, "type": "string"},
    "region": {"description": "Region / Territory / Country", "required": False, "type": "string"},
    "customer_id": {"description": "Customer Identifier", "required": False, "type": "string"},
    "quantity": {"description": "Units Sold / Quantity", "required": True, "type": "numeric"},
    "unit_price": {"description": "Unit Selling Price", "required": True, "type": "numeric"},
    "revenue": {"description": "Total Sales / Revenue", "required": False, "type": "numeric"},
    "cost": {"description": "Unit Cost Price", "required": False, "type": "numeric"},
    "inventory": {"description": "Stock / Inventory Level", "required": False, "type": "numeric"}
}

# Alias rules for smart auto-detection
FIELD_ALIASES = {
    "date": ["date", "order date", "order_date", "transaction date", "dt", "time", "day", "created_at", "orderdate", "invoice date", "invoicedate", "invoice datetime", "transaction date", "order datetime"],
    "order_id": ["order id", "order_id", "invoice id", "invoice_id", "transaction id", "trans_id", "order_no", "ordernumber", "invoice", "invoice no", "invoice number", "orderno"],
    "product_id": ["product id", "product_id", "sku", "item id", "item_code", "product code", "stockcode", "stock code", "item no"],
    "product_name": ["product", "product name", "product_name", "item", "item_name", "title", "product_title", "description", "product description"],
    "category": ["category", "category name", "category_name", "department", "group", "product_category", "dept"],
    "store": ["store", "store name", "store_name", "store_id", "location", "branch", "outlet", "shop"],
    "region": ["region", "territory", "zone", "state", "area", "market", "geography", "country", "country name"],
    "customer_id": ["customer id", "customer_id", "customer", "client", "client id", "client_id", "cust id", "customer number", "customer no"],
    "quantity": ["quantity", "qty", "units", "units sold", "quantity sold", "count", "items_sold"],
    "unit_price": ["unit price", "unit_price", "price", "selling price", "rate", "price per unit", "mrp"],
    "revenue": ["revenue", "sales", "total sales", "amount", "total amount", "sales_amount", "turnover", "total_price"],
    "cost": ["cost", "unit cost", "cost price", "cogs", "buy price", "cost_price", "purchase price"],
    "inventory": ["inventory", "stock", "stock level", "qty in stock", "available stock", "inventory_level", "stock_count"]
}

def detect_column_mapping(df_columns: List[str]) -> Dict[str, Optional[str]]:
    """
    Automatically maps dataset column names to internal canonical schema fields.
    Returns dict: {canonical_field: detected_uploaded_column_name_or_None}
    """
    mapping = {field: None for field in CANONICAL_FIELDS.keys()}
    cleaned_columns = {col: col.strip().lower().replace("_", " ") for col in df_columns}
    used_columns = set()

    for field, aliases in FIELD_ALIASES.items():
        for original_col, clean_col in cleaned_columns.items():
            if original_col in used_columns:
                continue
            if clean_col in aliases:
                mapping[field] = original_col
                used_columns.add(original_col)
                break

    return mapping

# Fields automatically derived by the transformer when unmapped (never penalized)
DERIVABLE_FIELDS = {"category"}

def check_schema_coverage(mapping: Dict[str, Optional[str]]) -> Tuple[List[str], List[str], List[str]]:
    """
    Checks which required & optional canonical fields are mapped.
    Auto-derived fields (e.g. category) count as satisfied.
    Returns (mapped_fields, missing_required_fields, missing_optional_fields).
    """
    mapped = []
    missing_required = []
    missing_optional = []

    for field, info in CANONICAL_FIELDS.items():
        if mapping.get(field):
            mapped.append(field)
        elif field in DERIVABLE_FIELDS:
            mapped.append(f"{field} (derived)")
        else:
            if info["required"]:
                missing_required.append(field)
            else:
                missing_optional.append(field)

    return mapped, missing_required, missing_optional
