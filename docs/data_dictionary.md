# Data Dictionary — Canonical Internal Schema

The internal analytical engine transforms arbitrary uploaded datasets into the following canonical schema:

| Canonical Field Name | Field Description | Data Type | Required | Derivation / Default Rules |
| :--- | :--- | :--- | :--- | :--- |
| `date` | Transaction or order timestamp | Datetime | **Yes** | Coerced to YYYY-MM-DD. Invalid dates dropped. |
| `order_id` | Unique invoice or order ID | String | No | Defaults to `ORD-{row_index}` |
| `product_id` | Unique SKU / Item Code | String | No | Defaults to `SKU-GENERIC` |
| `product_name` | Name of item sold | String | **Yes** | Defaults to `Unspecified Product` |
| `category` | Product department / category | String | **Yes** | Defaults to `General` |
| `store` | Store branch or location name | String | No | Defaults to `Main Store` |
| `region` | Geographical region / territory | String | No | Defaults to `National` |
| `quantity` | Count of units purchased | Numeric | **Yes** | Numeric cast. Negative values set to NaN. |
| `unit_price` | Selling price per single unit | Numeric | **Yes** | Numeric cast. Negative values set to NaN. |
| `revenue` | Total sales revenue | Numeric | Derived | `quantity * unit_price` if unmapped or missing. |
| `cost` | Unit cost price | Numeric | No | `NaN` if unmapped. Disables profit metrics gracefully. |
| `profit` | Gross profit amount | Numeric | Derived | `revenue - (quantity * cost)` if cost exists. |
| `inventory` | Available stock count | Numeric | No | `NaN` if unmapped. Disables turnover KPIs gracefully. |
