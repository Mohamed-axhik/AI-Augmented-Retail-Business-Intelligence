"""AI Business Analyst — premium analyst workspace."""
from __future__ import annotations

import streamlit as st
from src.ai.query_engine import AIQueryEngine
from ui.ai_components import render_evidence_panel, render_suggestion_chips
from ui.icons import icon
from ui.layout import render_empty_state, render_hero, render_section_header


def render_ai_analyst(df):
    """Renders the AI Business Analyst workspace."""
    render_hero(
        "AI BUSINESS ANALYST",
        "Ask questions. Get evidence-backed business answers.",
        "Natural-language Q&A over revenue, categories, stores, customers and anomalies. "
        "Every answer is grounded in deterministic analytics — the analyst never invents numbers.",
    )

    if df.empty:
        render_empty_state("No dataset loaded", "Load a dataset to start analysing with the AI analyst.",
                           icon_name="bot")
        return

    with st.expander("LLM API Key Configuration (Optional)", icon=":material/key:"):
        user_key = st.text_input(
            "Enter OpenAI or Gemini API Key", type="password",
            placeholder="sk-... or AIza...",
            help="Leave blank to use the built-in smart offline analyst engine.",
            key="llm_key_input",
        )
        if user_key:
            st.session_state["llm_api_key"] = user_key
            st.success("API key saved for this session.")
        elif st.button("Clear API key", width="content", type="secondary",
                       key="clear_llm_key"):
            st.session_state.pop("llm_api_key", None)
            st.session_state.pop("llm_key_input", None)
            st.rerun()

    api_key = st.session_state.get("llm_api_key")
    engine_mode = "LLM reasoning (OpenAI / Gemini)" if api_key else "Smart offline analyst engine"
    engine_color = "#8B5CF6" if api_key else "#34D399"
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:16px;">'
        f'<span style="width:7px;height:7px;border-radius:50%;'
        f'background:{engine_color};display:inline-block;"></span>'
        f'<span style="color:#8B99B5;font-size:0.8rem;font-weight:600;">Engine: {engine_mode}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    query_engine = AIQueryEngine(api_key=api_key)

    render_section_header("file", "Executive Briefing",
                          "One-click AI summary of overall business health")
    col_b1, col_b2 = st.columns([3, 9])
    with col_b1:
        briefing = st.button("Generate AI Executive Briefing",
                             type="primary", width="stretch", key="exec_brief")
    with col_b2:
        st.caption("Produces a structured summary of revenue, profitability, growth, "
                   "customer health and risk signals.")

    if briefing:
        with st.status("Analysing dataset & generating executive briefing…", expanded=False) as status:
            text = query_engine.generate_executive_briefing(df)
            status.update(label="Executive briefing ready", state="complete")
        st.markdown('<div class="ri-ai-answer">' + text + '</div>', unsafe_allow_html=True)

    st.markdown("---")

    render_section_header("bot", "Ask the AI Business Analyst",
                          "Ask anything about your retail data, or start from a suggested question")

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [
            {"role": "assistant",
             "content": "Hello! I am your AI Retail Analyst. Ask me anything about revenue, "
                        "category performance, store trends, customer behaviour or anomalies.",
             "context": None}
        ]

    # Suggested questions
    selected = {"q": None}
    render_suggestion_chips(on_select=lambda q: selected.update(q=q))

    for msg in st.session_state["chat_messages"]:
        with st.chat_message(msg["role"], avatar=_avatar(msg["role"])):
            st.markdown(msg["content"])
            if msg.get("context"):
                render_evidence_panel(msg["context"])

    user_input = st.chat_input("Ask a question about your retail data…") or selected["q"]

    if user_input:
        st.session_state["chat_messages"].append({"role": "user", "content": user_input,
                                                   "context": None})
        with st.chat_message("user", avatar=_avatar("user")):
            st.markdown(user_input)

        with st.status("Consulting analytics engine & LLM layer…", expanded=False) as status:
            answer, context = query_engine.answer_question(user_input, df)
            status.update(label="Analysis complete", state="complete")

        st.session_state["chat_messages"].append({"role": "assistant", "content": answer,
                                                   "context": context or None})
        with st.chat_message("assistant", avatar=_avatar("assistant")):
            st.markdown(answer)
            if context:
                render_evidence_panel(context)


def _avatar(role: str) -> str:
    if role == "user":
        return "user"
    return "assistant"