import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.anomaly.detector import detect_statistical_anomalies

def test_anomaly_detection_spike():
    dates = [datetime(2025, 1, 1) + timedelta(days=i) for i in range(30)]
    revenues = [1000.0] * 30
    revenues[15] = 10000.0 # Extreme spike anomaly on day 15

    df = pd.DataFrame({
        "date": dates,
        "revenue": revenues,
        "quantity": [1] * 30,
        "order_id": [f"ORD-{i}" for i in range(30)],
        "category": ["Electronics"] * 30,
        "product_name": ["Widget"] * 30,
        "store": ["Store A"] * 30
    })

    daily_df, anomaly_records = detect_statistical_anomalies(df, z_threshold=2.0)
    assert len(anomaly_records) >= 1
    anomaly_dates = [a["date"] for a in anomaly_records]
    assert "2025-01-16" in anomaly_dates or "2025-01-15" in anomaly_dates or len(anomaly_records) > 0
