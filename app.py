import streamlit as st
import anthropic
import os
from dotenv import load_dotenv

from agents.marcus import chat as marcus_chat
from agents.gemini_research import run_gemini_trend_report, save_report

load_dotenv()

st.set_page_config(
    page_title="Marcus | Home Decor Expert",
    page_icon="🏠",
    layout="wide",
)

# --- Sidebar: API key (only Anthropic needed now) ---
st.sidebar.subheader("API Keys")
anthropic_key = os.getenv("ANTHROPIC_API_KEY") or st.sidebar.text_input(
    "Anthropic API Key (Marcus)", type="password"
)

if not anthropic_key:
    st.info("Enter your Anthropic API key in the sidebar or set `ANTHROPIC_API_KEY` in a `.env` file.")
    st.stop()

claude_client = anthropic.Anthropic(api_key=anthropic_key)

# --- Sidebar: Trend Reports via Gemini CLI ---
st.sidebar.markdown("---")
st.sidebar.subheader("Research Agent (Gemini CLI)")
st.sidebar.caption("Runs `gemini -p` in headless mode for web research")
if st.sidebar.button("Generate Trend Report"):
    with st.sidebar:
        with st.spinner("Gemini CLI is researching trends..."):
            report = run_gemini_trend_report()
            path = save_report(report)
            st.session_state["latest_report"] = report
            st.success(f"Report saved to `{path}`")

if "latest_report" in st.session_state:
    with st.sidebar.expander("Latest Trend Report", expanded=False):
        st.markdown(st.session_state["latest_report"])

# --- Main Chat: Marcus Agent (Claude) ---
st.title("Marcus — Your Home Decor Expert")
st.caption(
    "Marcus (Claude) gives decor advice. "
    "When he needs trend data, he calls Gemini CLI in headless mode automatically."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask Marcus about your space..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Marcus is thinking..."):
            # Build messages for the agent (inject trend context if available)
            agent_messages = list(st.session_state.messages)
            if "latest_report" in st.session_state:
                trend_context = {
                    "role": "user",
                    "content": f"[CONTEXT — Latest trend research for your reference, "
                    f"use if relevant]\n\n{st.session_state['latest_report']}",
                }
                response_msg = {
                    "role": "assistant",
                    "content": "Got it, I have the latest trend data available. "
                    "I'll reference it when relevant.",
                }
                agent_messages = [trend_context, response_msg] + agent_messages

            reply = marcus_chat(claude_client, agent_messages)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
