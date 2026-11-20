"""
EduPath AI - Skill Gap Analysis
Detailed breakdown of critical, moderate, and optional skill gaps for target careers.
"""

import streamlit as st
from components.navbar import render_sidebar
from components.cards import render_header
from api_client import api_client

st.set_page_config(page_title="EduPath AI - Skill Gap Analysis", page_icon="🔍", layout="wide")
render_sidebar()

render_header(title="Skill Gap Analysis", subtitle="Identify missing competencies and target areas for rapid career readiness")

user = st.session_state.get("user")
if not user:
    st.warning("⚠️ Please sign in to view skill gap analysis.")
    st.stop()

# Fetch Skill Gaps
gaps = api_client.get_skill_gaps()

if not gaps:
    st.info("No skill gaps recorded yet. Please run Career Recommendations to discover skill gaps.")
    if st.button("Go to Career Recommendations"):
        st.switch_page("pages/3_🎯_Career_Recommendations.py")
else:
    # Filter Tabs
    tab_all, tab_crit, tab_mod = st.tabs(["All Gaps", "🚨 Critical Gaps", "⚠️ Moderate Gaps"])

    def render_gap_list(items):
        if not items:
            st.success("No gaps found in this category! Outstanding job.")
            return

        for g in items:
            imp = g.get("importance", "moderate").lower()
            badge_color = "#EF4444" if imp == "critical" else "#F59E0B"
            
            st.markdown(
                f"""
                <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px; padding: 18px; margin-bottom: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #1E293B;">{g.get('missing_skill')}</h4>
                        <span style="background: {badge_color}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase;">
                            {imp}
                        </span>
                    </div>
                    <p style="margin: 8px 0 0 0; color: #64748B; font-size: 14px;">
                        <strong>Action Plan:</strong> {g.get('recommendation_text') or 'Practice hands-on exercises and review curriculum resources.'}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    with tab_all:
        render_gap_list(gaps)

    with tab_crit:
        crit_gaps = [g for g in gaps if g.get("importance") == "critical"]
        render_gap_list(crit_gaps)

    with tab_mod:
        mod_gaps = [g for g in gaps if g.get("importance") == "moderate"]
        render_gap_list(mod_gaps)
