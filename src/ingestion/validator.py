import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from src.ingestion.schema import check_schema_coverage, CANONICAL_FIELDS, DERIVABLE_FIELDS

def validate_dataset(df: pd.DataFrame, column_mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    Evaluates dataset quality and returns comprehensive quality metrics & validation score (0-100).
    """
    total_rows = len(df)
    total_cols = len(df.columns)

    if total_rows == 0:
        return {
            "score": 0,
            "status": "🔴 Critical",
            "status_code": "CRITICAL",
            "total_rows": 0,
            "total_cols": total_cols,
            "missing_cells_pct": 100.0,
            "duplicate_rows": 0,
            "invalid_dates": 0,
            "negative_quantities": 0,
            "negative_prices": 0,
            "checklist": [("🔴 Empty Dataset", "The uploaded file contains 0 rows.")],
            "schema_mapped_count": 0
        }

    # Missing values
    missing_cells = df.isnull().sum().sum()
    total_cells = total_rows * total_cols
    missing_cells_pct = round((missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0.0

    # Duplicates
    duplicate_rows = int(df.duplicated().sum())

    # Invalid dates check
    date_col = column_mapping.get("date")
    invalid_dates = 0
    if date_col and date_col in df.columns:
        parsed_dates = pd.to_datetime(df[date_col], errors='coerce')
        invalid_dates = int(parsed_dates.isnull().sum() - df[date_col].isnull().sum())

    # Negative quantities
    qty_col = column_mapping.get("quantity")
    negative_quantities = 0
    if qty_col and qty_col in df.columns:
        numeric_qty = pd.to_numeric(df[qty_col], errors='coerce')
        negative_quantities = int((numeric_qty < 0).sum())

    # Negative prices
    price_col = column_mapping.get("unit_price")
    negative_prices = 0
    if price_col and price_col in df.columns:
        numeric_price = pd.to_numeric(df[price_col], errors='coerce')
        negative_prices = int((numeric_price < 0).sum())

    # Check schema coverage
    mapped_fields, missing_required, missing_optional = check_schema_coverage(column_mapping)

    # Compute Quality Score (0-100 formula)
    deductions = 0.0
    checklist: List[Tuple[str, str]] = []

    # Required schema check (35 pts deduction if missing required fields)
    if missing_required:
        deductions += 35.0
        checklist.append(("🔴 Missing Required Columns", f"Missing key fields: {', '.join(missing_required)}"))
    else:
        checklist.append(("✓ Required Schema Mapped", f"All essential fields ({', '.join(mapped_fields)}) detected."))

    # Auto-derived fields note (no deduction)
    derived_fields = [f for f in DERIVABLE_FIELDS if not column_mapping.get(f)]
    if derived_fields:
        checklist.append(("ℹ Auto-Derived Fields", f"{', '.join(derived_fields)} is automatically derived from other columns (no penalty)."))

    # Optional schema info (minor 2 pts deduction per missing optional field up to 8 pts max)
    if missing_optional:
        opt_deduction = min(8.0, len(missing_optional) * 2.0)
        deductions += opt_deduction
        checklist.append(("ℹ Optional Fields Unavailable", f"Fields omitted: {', '.join(missing_optional)}"))

    # Missing values (max 20 pts deduction)
    if missing_cells_pct > 15:
        deductions += 20
        checklist.append(("🔴 High Missing Values", f"{missing_cells_pct}% of data cells are empty."))
    elif missing_cells_pct > 2:
        deductions += 10
        checklist.append(("⚠ Missing Values Present", f"{missing_cells_pct}% of data cells are empty."))
    else:
        checklist.append(("✓ Clean Data Completeness", f"Only {missing_cells_pct}% missing cell values."))

    # Duplicates (max 15 pts deduction)
    dup_pct = (duplicate_rows / total_rows) * 100
    if dup_pct > 10:
        deductions += 15
        checklist.append(("🔴 High Duplicate Rows", f"{duplicate_rows} duplicate rows ({round(dup_pct, 1)}%)."))
    elif duplicate_rows > 0:
        deductions += 5
        checklist.append(("⚠ Duplicate Rows Found", f"{duplicate_rows} duplicate rows detected."))
    else:
        checklist.append(("✓ No Duplicate Rows", "Zero duplicate rows found."))

    # Invalid dates (max 15 pts deduction)
    if invalid_dates > 0:
        deductions += 15
        checklist.append(("⚠ Invalid Date Formats", f"{invalid_dates} rows have unparseable dates."))
    elif date_col:
        checklist.append(("✓ Date Column Validated", "All date entries parsed successfully."))

    # Negative quantities (treated as returns/refunds in retail data) / negative prices
    if negative_prices > 0:
        deductions += 15
        checklist.append(("⚠ Negative Prices Detected", f"{negative_prices} rows have negative unit prices."))
    elif negative_quantities > 0:
        checklist.append(("✓ Returns Detected", f"{negative_quantities:,} negative-quantity rows treated as returns / refunds."))
    else:
        checklist.append(("✓ Valid Quantities & Prices", "No negative values detected in price or quantity."))

    score = max(0, int(round(100 - deductions)))

    if score >= 85 and not missing_required:
        status = "🟢 Passed"
        status_code = "PASSED"
    elif score >= 60 and not missing_required:
        status = "🟡 Warning"
        status_code = "WARNING"
    else:
        status = "🔴 Critical"
        status_code = "CRITICAL"

    return {
        "score": score,
        "status": status,
        "status_code": status_code,
        "total_rows": total_rows,
        "total_cols": total_cols,
        "missing_cells_pct": missing_cells_pct,
        "duplicate_rows": duplicate_rows,
        "invalid_dates": invalid_dates,
        "negative_quantities": negative_quantities,
        "negative_prices": negative_prices,
        "checklist": checklist,
        "schema_mapped_count": len(mapped_fields),
        "missing_required": missing_required,
        "missing_optional": missing_optional
    }
