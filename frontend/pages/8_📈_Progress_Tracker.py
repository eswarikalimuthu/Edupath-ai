"""
EduPath AI - Learning Progress Tracker
Monitors student skill acquisition, roadmap milestone completion, and learning momentum.
"""

import streamlit as st
from components.navbar import render_sidebar
from components.cards import render_header, render_metric_card
from components.charts import create_gauge_chart, create_skills_radar_chart
from api_client import api_client

st.set_page_config(page_title="EduPath AI - Progress Tracker", page_icon="📈", layout="wide")
render_sidebar()

render_header(title="Learning Progress Tracker", subtitle="Track milestone completions, skill masteries, and target career readiness")

user = st.session_state.get("user")
if not user:
    st.warning("⚠️ Please sign in to view your learning progress.")
    st.stop()

# Fetch Progress Summary
prog = api_client.get_progress_summary()
roadmaps = api_client.get_roadmaps()

# Summary Metrics Row
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card("Overall Progress", f"{prog.get('completion_percentage', 0.0)}%", "Across All Roadmaps", "📊", "#2563EB")
with c2:
    render_metric_card("Completed Milestones", f"{prog.get('completed_milestones', 0)} / {prog.get('total_milestones', 0)}", "Tasks Finished", "✅", "#10B981")
with c3:
    render_metric_card("Technical Skills", prog.get("technical_skills_count", 0), "Verified Stack", "💻", "#6366F1")
with c4:
    render_metric_card("Active Roadmaps", prog.get("total_roadmaps", 0), "Curricula in Progress", "🗺️", "#F59E0B")

st.divider()

col_gauge, col_radar = st.columns(2)
with col_gauge:
    st.subheader("🎯 Overall Goal Readiness")
    st.plotly_chart(create_gauge_chart(prog.get("completion_percentage", 0.0), "Curriculum Completion"), use_container_width=True)

with col_radar:
    st.subheader("⚡ Competency Distribution")
    skill_breakdown = {
        "Technical": prog.get("technical_skills_count", 0),
        "Soft Skills": prog.get("soft_skills_count", 0),
        "Domain": prog.get("domain_skills_count", 0)
    }
    st.plotly_chart(create_skills_radar_chart(skill_breakdown), use_container_width=True)

st.divider()

# Detailed Roadmap Progress Breakdown
st.subheader("📋 Active Roadmap Milestone Status")

if not roadmaps:
    st.info("No active roadmaps found. Generate a personalized roadmap to track progress.")
else:
    for r in roadmaps:
        milestones = r.get("milestones", [])
        completed_count = sum(1 for m in milestones if m.get("is_completed"))
        total_count = len(milestones)
        pct = round((completed_count / total_count) * 100, 1) if total_count > 0 else 0.0

        with st.expander(f"🗺️ **{r.get('role_title')}** — {completed_count}/{total_count} Milestones Completed ({pct}%)", expanded=True):
            st.progress(pct / 100.0)
            for m in milestones:
                status_icon = "✅" if m.get("is_completed") else "⏳"
                st.markdown(f"{status_icon} **{m.get('title')}** ({m.get('stage').title()} Stage)")
                if m.get("description"):
                    st.caption(m.get("description"))
