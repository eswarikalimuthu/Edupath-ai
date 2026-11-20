"""
EduPath AI - AI Career Assistant
Intelligent conversational guidance powered by LangGraph multi-agent orchestration and grounded RAG.
"""

import streamlit as st
from components.navbar import render_sidebar
from components.cards import render_header
from api_client import api_client

st.set_page_config(page_title="EduPath AI - Career Assistant", page_icon="💬", layout="wide")
render_sidebar()

render_header(title="AI Career Assistant", subtitle="Ask educational queries, discover career pathways, or explore verified certifications", badge="LangGraph Multi-Agent")

user = st.session_state.get("user")
if not user:
    st.warning("⚠️ Please sign in to chat with the AI Career Assistant and save your conversation.")
    st.stop()

session_id = f"session_{user.get('id')}"

# Initialize local chat history in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
    # Load past history from backend
    past_messages = api_client.get_chat_history(session_id=session_id)
    for m in past_messages:
        st.session_state["messages"].append({
            "role": m.get("role"),
            "content": m.get("content"),
            "agent": m.get("agent_name"),
            "citations": m.get("citations_json", [])
        })

# Render conversation messages
for msg in st.session_state["messages"]:
    role = msg.get("role")
    with st.chat_message(role):
        if role == "assistant" and msg.get("agent"):
            st.caption(f"🤖 Agent: **{msg.get('agent')}**")
        st.markdown(msg.get("content"))
        
        # Citations expander
        citations = msg.get("citations", [])
        if citations:
            with st.expander("📚 View Verified Source Citations"):
                for c in citations:
                    st.markdown(
                        f"- **[{c.get('citation_id')}] {c.get('source')}** (Page {c.get('page_number')})\n"
                        f"  *\"{c.get('excerpt')}\"* — Relevance: `{c.get('score')}`"
                    )

# User Chat Input
if prompt := st.chat_input("Ask a question about careers, qualifications, skill gaps, or learning roadmaps..."):
    # Render user query
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    # Call Backend Multi-Agent System
    with st.chat_message("assistant"):
        with st.spinner("EduPath AI agents are coordinating..."):
            res = api_client.send_chat_message(query=prompt, session_id=session_id)
            answer = res.get("answer", "No answer received.")
            agent_used = res.get("agent_used", "QAAgent")
            citations = res.get("citations", [])

            st.caption(f"🤖 Handled by: **{agent_used}**")
            st.markdown(answer)

            if citations:
                with st.expander("📚 View Verified Source Citations"):
                    for c in citations:
                        st.markdown(
                            f"- **[{c.get('citation_id')}] {c.get('source')}** (Page {c.get('page_number')})\n"
                            f"  *\"{c.get('excerpt')}\"* — Relevance: `{c.get('score')}`"
                        )

            st.session_state["messages"].append({
                "role": "assistant",
                "content": answer,
                "agent": agent_used,
                "citations": citations
            })
