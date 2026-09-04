# AI-Augmented Retail Business Performance Intelligence Platform 🛒📊

An enterprise-grade, portfolio-ready Retail Business Intelligence (BI) and AI Analyst platform. Built in Python, Streamlit, Pandas, DuckDB, Plotly, and LLM APIs.

---

## 🌟 Key Features & Distinction

1. **Deterministic Analytics Core**: Financial totals, profit margins, AOV, MoM growth rates, and statistical anomalies are computed with 100% mathematical precision by Python and DuckDB—**the LLM never calculates raw numbers or hallucinates KPIs**.
2. **Schema Auto-Detection Layer**: Intelligent fuzzy alias mapping layer maps arbitrary CSV/Excel headers (e.g. `Order Date`, `Sales`, `Qty`, `Item Name`) to standard internal canonical fields.
3. **Data Quality Health Report (0–100 Score)**: Evaluates dataset health, missing values %, duplicate rows, unparseable dates, and negative price/quantity anomalies with color-coded status badges (🟢 Passed, 🟡 Warning, 🔴 Critical).
4. **Graceful Degradation**: Datasets lacking cost or inventory columns disable dependent metrics without crashing the dashboard.
5. **Statistical Anomaly Detector**: Z-Score ($|Z| > 2.2$) & IQR baseline deviation detection with root-cause driver breakdown (Category, Product, Store).
6. **Natural Language AI Analyst**: Supports natural-language business Q&A and one-click C-suite Executive Briefings using OpenAI, Google Gemini, or a built-in smart offline analyst fallback engine.

---

## 🏗 System Architecture

```text
UPLOAD DATASET (.csv / .xlsx) ──► SCHEMA AUTO-DETECTION ──► QUALITY VALIDATION (0-100)
                                                                 │
                                                                 ▼
                                                        CANONICAL DATASET
                                                                 │
                                            ┌────────────────────┴────────────────────┐
                                            ▼                                         ▼
                                  DETERMINISTIC ANALYTICS                     STATISTICAL ANOMALY
                                     (Pandas & DuckDB)                            (Z-Score)
                                            │                                         │
                                            └────────────────────┬────────────────────┘
                                                                 ▼
                                                      STRUCTURED CONTEXT PAYLOAD
                                                                 │
                                                                 ▼
                                                        AI ANALYST (LLM)
                                                                 │
                                                                 ▼
                                                    EXECUTIVE INSIGHTS & Q&A
```

---

## 🚀 Quick Start & Installation

### 1. Clone & Navigate
```bash
git clone https://github.com/your-username/AI-Augmented-Retail-Intelligence.git
cd AI-Augmented-Retail-Intelligence
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run Streamlit Dashboard
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 🧪 Running Unit Tests

Run the Pytest suite to verify dataset loader, schema mapper, quality scoring, KPI math, and anomaly engine:

```bash
pytest tests/
```

---

## 🔑 LLM API Key Configuration (Optional)

The application includes a built-in **Smart Offline Analyst** that generates structured natural-language insights out of the box without requiring any API key.

To activate custom LLM reasoning using OpenAI or Gemini:
1. Create a `.streamlit/secrets.toml` file:
   ```toml
   OPENAI_API_KEY = "your-openai-api-key"
   # or
   GEMINI_API_KEY = "your-gemini-api-key"
   ```
2. Or input your API key directly inside the **🤖 AI Analyst** tab in the application.

---

## 📁 Project Directory Structure

```text
AI-Augmented-Retail-Intelligence/
├── app.py                         # Application entry point & router
├── requirements.txt               # Dependencies
├── README.md                      # Documentation
├── .gitignore
├── .streamlit/
│   └── config.toml                # Dark theme & 50MB upload limit settings
├── data/
│   └── sample_retail_data.csv     # Built-in 2,500+ row realistic sample dataset
├── src/
│   ├── ingestion/                 # File loader, schema detection & quality validator
│   ├── processing/                # Cleaner & canonical transformer
│   ├── analytics/                 # KPI, Sales, Category, Product, Store & Inventory engines
│   ├── anomaly/                   # Statistical Z-Score anomaly detector & driver analysis
│   ├── ai/                        # Unified LLM interface, context builder & query engine
│   └── utils/                     # Formatting helpers & DuckDB SQL interface
├── ui/                            # Custom CSS components, sidebar & tab views
├── tests/                         # Pytest test suite
└── docs/                          # Architecture guide & data dictionary
```

---

## 📜 License
MIT License. Built for portfolio demonstration.
