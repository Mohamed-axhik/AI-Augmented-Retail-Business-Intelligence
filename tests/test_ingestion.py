import pytest
import pandas as pd
import io
from src.ingestion.loader import load_file
from src.ingestion.schema import detect_column_mapping, check_schema_coverage
from src.ingestion.validator import validate_dataset

def test_load_file_csv():
    csv_content = "Order Date,Sales,Qty,Unit Price,Product Name,Category Name\n2025-01-01,100,2,50,Widget A,Electronics\n"
    df, err = load_file(io.StringIO(csv_content), "test.csv")
    assert err is None
    assert df is not None
    assert len(df) == 1

def test_schema_auto_detection():
    cols = ["Order Date", "Sales", "Qty", "Unit Price", "Product Name", "Category Name", "Cost Price", "Store Name"]
    mapping = detect_column_mapping(cols)
    assert mapping["date"] == "Order Date"
    assert mapping["revenue"] == "Sales"
    assert mapping["quantity"] == "Qty"
    assert mapping["unit_price"] == "Unit Price"
    assert mapping["product_name"] == "Product Name"
    assert mapping["category"] == "Category Name"
    assert mapping["cost"] == "Cost Price"
    assert mapping["store"] == "Store Name"

def test_validate_dataset_quality_score():
    data = {
        "Order Date": ["2025-01-01", "2025-01-02"],
        "Sales": [500, 1000],
        "Qty": [1, 2],
        "Unit Price": [500, 500],
        "Product Name": ["Item X", "Item Y"],
        "Category Name": ["Tech", "Tech"]
    }
    df = pd.DataFrame(data)
    mapping = detect_column_mapping(list(df.columns))
    report = validate_dataset(df, mapping)
    assert report["score"] >= 80
    assert report["status_code"] in ["PASSED", "WARNING"]
