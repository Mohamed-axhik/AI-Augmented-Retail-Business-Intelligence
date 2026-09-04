# AI-Augmented Retail Business Performance Intelligence Platform — Architecture Guide

## System Architecture

```text
                                  RETAIL USER
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │    Streamlit UI     │
                            └──────────┬──────────┘
                                       │
                                CSV / Excel Upload
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │  INGESTION LAYER    │
                            │                     │
                            │ Loader              │
                            │ Schema Detection    │
                            │ Validation          │
                            │ Cleaning            │
                            └──────────┬──────────┘
                                       │
                                       ▼
                            STANDARDIZED DATASET
                                       │
                           ┌───────────┴───────────┐
                           │                       │
                           ▼                       ▼
                   ┌───────────────┐       ┌────────────────┐
                   │ ANALYTICS     │       │ ANOMALY ENGINE │
                   │ ENGINE        │       │                │
                   │               │       │ Statistical    │
                   │ KPIs          │       │ Detection      │
                   │ Growth        │       └───────┬────────┘
                   │ Category      │               │
                   │ Product       │               │
                   │ Store         │               │
                   └───────┬───────┘               │
                           │                       │
                           └───────────┬───────────┘
                                       ▼
                               BUSINESS CONTEXT
                                       │
                                       ▼
                               ┌───────────────┐
                               │   AI LAYER    │
                               │               │
                               │ Query Engine  │
                               │ Context       │
                               │ LLM           │
                               │ Explanation   │
                               └───────┬───────┘
                                       │
                                       ▼
                            ┌─────────────────────┐
                            │   AI RETAIL ANALYST │
                            │                     │
                            │ "Why did sales     │
                            │  decline?"          │
                            └─────────────────────┘
```

## Layer Design Rationale

1. **Ingestion & Validation Engine**:
   - Auto-detects custom headers.
   - Calculates 0–100 Data Quality Score based on cell completeness, duplicates, unparseable dates, and negative price/quantity anomalies.

2. **Analytics Engine (Pandas & DuckDB)**:
   - Evaluates executive metrics deterministically (`Revenue = Quantity × Unit Price`).
   - DuckDB in-memory engine provides sub-millisecond analytical SQL queries.

3. **Statistical Anomaly Engine**:
   - Employs Z-score ($|Z| > 2.2$) & IQR outlier detection on daily revenue streams.
   - Computes primary root-cause contributors by evaluating product, category, and store variances on anomaly dates.

4. **AI Analyst Augmentation**:
   - Passes structured context payloads to Gemini/OpenAI API or the built-in offline smart analyst fallback engine.
   - Generates executive briefings and answers natural language questions with 100% numerical fidelity.
