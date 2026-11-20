"""
EduPath AI - Main Dashboard / Home
Smart Educational & Career Guidance Platform (SIH25094)
"""

import streamlit as st
from components.navbar import render_sidebar
from components.cards import render_metric_card, render_header
from components.charts import create_gauge_chart, create_skills_radar_chart, create_recommendation_bar_chart
from api_client import api_client

st.set_page_config(
    page_title="EduPath AI - Career Guidance Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_sidebar()

render_header(
    title="EduPath AI Dashboard",
    subtitle="Intelligent Career Guidance, Skill Gap Analysis & Personalized Learning Roadmaps",
    badge="SIH25094"
)

user = st.session_state.get("user")

if not user:
    st.warning("⚠️ You are browsing in guest mode. Please sign in or register to access personalized roadmaps and recommendations.")
    col_a, col_b = st.columns(2)
    with col_a:
        st.info("💡 **New Student?** Head to the **Auth** page in the sidebar to create your secure account.")
    with col_b:
        st.info("📚 **Want to explore?** Check out **AI Career Assistant** or **Document Management** to explore verified career data.")

# Fetch Summary Metrics
progress = api_client.get_progress_summary() if user else {}
recs = api_client.get_recommendations() if user else []

# Metric Row
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_metric_card("Roadmap Progress", f"{progress.get('completion_percentage', 0.0)}%", "Milestones Completed", "📈", "#2563EB")
with c2:
    render_metric_card("Verified Skills", progress.get("total_skills", 0), "Technical & Domain", "⚡", "#10B981")
with c3:
    render_metric_card("Active Roadmaps", progress.get("total_roadmaps", 0), "Staged Milestones", "🗺️", "#F59E0B")
with c4:
    render_metric_card("Career Recommendations", progress.get("total_recommendations", 0), "Grounded Matches", "🎯", "#8B5CF6")

st.divider()

# Charts & Analysis Row
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📊 Learning Progress")
    gauge_val = progress.get("completion_percentage", 0.0)
    st.plotly_chart(create_gauge_chart(gauge_val, "Roadmap Completion"), use_container_width=True)

    st.subheader("🎯 Career Matches Overview")
    if recs:
        st.plotly_chart(create_recommendation_bar_chart(recs), use_container_width=True)
    else:
        st.caption("No recommendations generated yet. Visit Career Recommendations to analyze your profile.")

with col_right:
    st.subheader("⚡ Skill Competency Breakdown")
    skill_breakdown = {
        "Technical": progress.get("technical_skills_count", 0),
        "Soft Skills": progress.get("soft_skills_count", 0),
        "Domain": progress.get("domain_skills_count", 0)
    }
    st.plotly_chart(create_skills_radar_chart(skill_breakdown), use_container_width=True)

    st.subheader("🚀 Quick Actions")
    qa_col1, qa_col2 = st.columns(2)
    with qa_col1:
        if st.button("🔍 Run Skill Gap Analysis", use_container_width=True):
            st.switch_page("pages/4_🔍_Skill_Gap_Analysis.py")
        if st.button("💬 Ask AI Career Assistant", use_container_width=True):
            st.switch_page("pages/6_💬_AI_Career_Assistant.py")
    with qa_col2:
        if st.button("🗺️ View Active Roadmaps", use_container_width=True):
            st.switch_page("pages/5_🗺️_Personalized_Roadmap.py")
        if st.button("👤 Update My Profile", use_container_width=True):
            st.switch_page("pages/2_👤_Student_Profile.py")
