import os
import json
from typing import Dict, Any, Optional

class LLMAnalyst:
    """
    Unified LLM Interface with automatic provider resolution (Gemini, OpenAI, or Fallback).
    """

    def __init__(self, api_key: Optional[str] = None, provider: str = "auto"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.provider = provider

    def generate_explanation(self, prompt: str, context: Dict[str, Any], system_prompt: str) -> str:
        """
        Sends query payload to LLM or executes fallback NLG engine if no API key is set.
        """
        # Try OpenAI or Gemini if API Key is available
        if self.api_key:
            try:
                # Attempt Gemini API first if google-genai is installed
                if "gemini" in self.provider.lower() or os.getenv("GEMINI_API_KEY"):
                    from google import genai
                    client = genai.Client(api_key=self.api_key)
                    full_prompt = f"{system_prompt}\n\nDATA CONTEXT:\n{json.dumps(context, indent=2)}\n\nQUESTION:\n{prompt}"
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=full_prompt,
                    )
                    if response and response.text:
                        return response.text.strip()
            except Exception as e:
                print(f"Gemini API attempt failed: {e}. Falling back...")

            try:
                # Attempt OpenAI API
                import openai
                client = openai.OpenAI(api_key=self.api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"DATA CONTEXT:\n{json.dumps(context, indent=2)}\n\nQUESTION:\n{prompt}"}
                    ],
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"OpenAI API attempt failed: {e}. Falling back to deterministic offline analyst.")

        # Fallback Offline Smart Analyst (Deterministic Template NLG)
        return self._generate_fallback_insight(prompt, context)

    def _generate_fallback_insight(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        Deterministic Rule-based Natural Language Generation when no API key is present.
        """
        kpis = context.get("executive_kpis", {})
        rev = kpis.get("total_revenue", 0)
        profit = kpis.get("total_profit")
        margin = kpis.get("profit_margin_pct")
        mom = kpis.get("mom_growth_pct")
        orders = kpis.get("total_orders", 0)
        aov = kpis.get("aov", 0)
        cats = context.get("category_summary", [])
        anomalies = context.get("recent_anomalies", [])

        top_cat_name = cats[0]["category"] if cats else "N/A"
        top_cat_rev = cats[0]["revenue"] if cats else 0
        cust = context.get("customer_summary", {})
        customers = cust.get("total_customers", 0)
        repeat_rate = cust.get("repeat_rate_pct")

        prompt_lower = prompt.lower()

        if "executive" in prompt_lower or "summary" in prompt_lower or "brief" in prompt_lower:
            lines = [
                "### 📊 AI Executive Performance Summary",
                f"- **Revenue & Orders**: Total revenue stands at **£{rev:,.2f}** across **{orders:,} orders** (AOV: £{aov:,.2f}).",
                f"- **Profitability**: Generated total profit of **£{profit:,.2f}** with a profit margin of **{margin}%**." if profit else "- **Profitability**: Profit tracking is currently disabled (no cost column mapped).",
                f"- **Growth Trajectory**: Revenue changed **{mom}% MoM** compared to the previous month.",
                f"- **Category Driver**: **{top_cat_name}** is the top revenue generator, contributing **£{top_cat_rev:,.2f}**.",
                f"- **Customer Base**: **{customers:,}** unique customers" + (f" with a **{repeat_rate}%** repeat purchase rate." if repeat_rate is not None else "."),
                f"- **Anomalies**: Identified **{len(anomalies)} statistical anomalies** requiring management review."
            ]
            return "\n\n".join(lines)

        elif "revenue" in prompt_lower or "sales" in prompt_lower:
            return (
                f"Based on the deterministic analytics engine, total revenue is **£{rev:,.2f}** generated from **{orders:,} orders**.\n\n"
                f"• **Average Order Value (AOV)**: £{aov:,.2f}\n"
                f"• **MoM Growth**: {mom}%\n"
                f"• **Top Category**: {top_cat_name} (£{top_cat_rev:,.2f})"
            )

        elif "category" in prompt_lower or "products" in prompt_lower:
            top_prods = context.get("top_5_products", [])
            top_prod_str = ", ".join([f"{p['product_name']} (£{p['revenue']:,.0f})" for p in top_prods[:3]])
            return (
                f"Category and product performance analysis highlights:\n\n"
                f"• **Leading Category**: **{top_cat_name}** with £{top_cat_rev:,.2f} in sales.\n"
                f"• **Top Products**: {top_prod_str}.\n"
                f"• **Recommendation**: Reallocate marketing spend toward high-margin products in {top_cat_name}."
            )

        elif "anomaly" in prompt_lower or "spike" in prompt_lower or "drop" in prompt_lower:
            if not anomalies:
                return "No statistical revenue anomalies were detected in the dataset (all sales fall within standard Z-score bounds)."
            a = anomalies[0]
            drivers_str = " | ".join(a.get("possible_drivers", []))
            return (
                f"Anomalous business activity detected on **{a['date']}**:\n\n"
                f"• **Type**: {a['anomaly_type']}\n"
                f"• **Actual Revenue**: £{a['actual_revenue']:,.2f} (Expected: £{a['expected_revenue']:,.2f})\n"
                f"• **Deviation**: {a['deviation_pct']}%\n"
                f"• **Primary Drivers**: {drivers_str}"
            )

        else:
            return (
                f"**Analytics Query Answer**:\n\n"
                f"• **Total Revenue**: £{rev:,.2f}\n"
                f"• **Orders Processed**: {orders:,}\n"
                f"• **MoM Revenue Growth**: {mom}%\n"
                f"• **Top Category**: {top_cat_name}\n\n"
                f"*(Tip: You can add an OpenAI or Gemini API key in Streamlit secrets for deep custom natural-language reasoning.)*"
            )
