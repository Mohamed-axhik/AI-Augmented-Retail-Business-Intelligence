import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_data():
    np.random.seed(42)
    random.seed(42)

    categories_products = {
        "Electronics": [
            ("iPhone 15 Pro", 120000, 95000),
            ("Samsung Galaxy S24", 90000, 72000),
            ("MacBook Air M3", 115000, 90000),
            ("Sony WH-1000XM5 Headphones", 28000, 20000),
            ("Dell XPS 15", 140000, 110000),
            ("iPad Air 5th Gen", 55000, 42000)
        ],
        "Apparel": [
            ("Nike Air Max Sneakers", 9500, 5500),
            ("Levi's Denim Jacket", 4500, 2400),
            ("Adidas Ultraboost", 12000, 7000),
            ("Zara Cotton Shirt", 2500, 1200),
            ("Puma Track Pants", 2200, 1100)
        ],
        "Furniture": [
            ("Ergonomic Office Chair", 18000, 11000),
            ("Solid Wood Dining Table", 45000, 30000),
            ("Minimalist Sofa 3-Seater", 60000, 40000),
            ("Standing Desk Dual Motor", 32000, 21000)
        ],
        "Grocery": [
            ("Organic Extra Virgin Olive Oil 1L", 1400, 950),
            ("Premium Basmati Rice 5kg", 850, 580),
            ("Artisanal Dark Chocolate Pack", 650, 380),
            ("Imported Coffee Beans 500g", 1200, 750)
        ],
        "Home & Kitchen": [
            ("Dyson Airwrap Styler", 49000, 38000),
            ("Philips Air Fryer XL", 12500, 8500),
            ("Nespresso Coffee Machine", 18500, 12500),
            ("Robot Vacuum Cleaner", 29000, 19000)
        ]
    }

    stores_regions = [
        ("Chennai Central", "South"),
        ("Mumbai West", "West"),
        ("Delhi North", "North"),
        ("Bengaluru East", "South"),
        ("Kolkata South", "East")
    ]

    start_date = datetime(2025, 1, 1)
    num_days = 365
    records = []
    order_counter = 10001

    for day_offset in range(num_days):
        current_date = start_date + timedelta(days=day_offset)
        # Weekend sales boost
        num_orders = random.randint(4, 8) if current_date.weekday() < 5 else random.randint(7, 12)
        
        # Inject deliberate anomalies
        if current_date.strftime("%Y-%m-%d") == "2025-03-15":
            num_orders = 35 # High spike anomaly
        elif current_date.strftime("%Y-%m-%d") == "2025-07-22":
            num_orders = 1 # Low drop anomaly

        for _ in range(num_orders):
            category = random.choice(list(categories_products.keys()))
            product, price, cost = random.choice(categories_products[category])
            store, region = random.choice(stores_regions)
            qty = random.randint(1, 4)
            if category == "Grocery":
                qty = random.randint(1, 8)
            
            # Stock inventory level
            stock = random.randint(15, 150)
            if product == "Dyson Airwrap Styler" and random.random() < 0.2:
                stock = random.randint(0, 3) # Low stock alert simulation

            records.append({
                "Order Date": current_date.strftime("%Y-%m-%d"),
                "Order ID": f"ORD-{order_counter}",
                "Product Name": product,
                "Category Name": category,
                "Store Name": store,
                "Region": region,
                "Qty": qty,
                "Unit Price": price,
                "Cost Price": cost,
                "Stock Level": stock
            })
            order_counter += 1

    df = pd.DataFrame(records)
    # Introduce tiny missing data & duplicate rows to test data quality engine
    df.loc[15, "Qty"] = None
    df.loc[42, "Unit Price"] = -500 # Negative price anomaly for testing
    
    # Duplicate row addition
    duplicate_rows = df.iloc[[10, 25, 100]].copy()
    df = pd.concat([df, duplicate_rows], ignore_index=True)

    import os
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/sample_retail_data.csv", index=False)
    print(f"Generated dataset with {len(df)} rows.")

if __name__ == "__main__":
    generate_sample_data()
