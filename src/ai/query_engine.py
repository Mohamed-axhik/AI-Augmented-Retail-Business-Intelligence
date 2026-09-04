import pandas as pd
from typing import Dict, Any, Tuple
from src.ai.context import build_business_context
from src.ai.prompts import SYSTEM_ANALYST_PROMPT, EXECUTIVE_SUMMARY_PROMPT
from src.ai.llm import LLMAnalyst
from src.utils.db import query_duckdb

class AIQueryEngine:
    """
    Orchestrates user questions:
    User Question -> Analytics Engine -> Structured Context -> LLM -> Natural Language Explanation
    """

    def __init__(self, api_key: str = None):
        self.llm = LLMAnalyst(api_key=api_key)

    def answer_question(self, question: str, df: pd.DataFrame) -> Tuple[str, Dict[str, Any]]:
        """
        Executes question answer workflow.
        Returns (natural_language_answer, structured_context_payload).
        """
        if df.empty:
            return "No dataset is currently loaded. Please upload a CSV/Excel file or load the sample dataset.", {}

        # Build full business context
        context = build_business_context(df)

        # Dynamic DuckDB SQL query execution for targeted numerical queries
        q_lower = question.lower()
        if "top 10" in q_lower or "top 5" in q_lower:
            sql = "SELECT product_name, category, SUM(revenue) as total_revenue, SUM(quantity) as units_sold FROM retail_data GROUP BY product_name, category ORDER BY total_revenue DESC LIMIT 10"
            sql_res = query_duckdb(df, sql)
            if sql_res is not None:
                context["targeted_sql_result"] = sql_res.to_dict("records")
        elif "monthly" in q_lower or "march" in q_lower or "trend" in q_lower:
            sql = "SELECT strftime(date, '%Y-%m') as month, SUM(revenue) as monthly_revenue, COUNT(DISTINCT order_id) as orders FROM retail_data GROUP BY month ORDER BY month"
            sql_res = query_duckdb(df, sql)
            if sql_res is not None:
                context["monthly_trend_sql"] = sql_res.to_dict("records")

        # Call LLM / Fallback analyst
        answer = self.llm.generate_explanation(
            prompt=question,
            context=context,
            system_prompt=SYSTEM_ANALYST_PROMPT
        )

        return answer, context

    def generate_executive_briefing(self, df: pd.DataFrame) -> str:
        """
        Generates automated executive summary briefing.
        """
        if df.empty:
            return "No dataset loaded for executive briefing."

        context = build_business_context(df)
        return self.llm.generate_explanation(
            prompt="Generate Executive Briefing Summary",
            context=context,
            system_prompt=EXECUTIVE_SUMMARY_PROMPT
        )
