"""
EduPath AI - Personalized Learning Roadmap
Stage-by-stage learning pathways with actionable project milestones and progress tracking.
"""

import streamlit as st
from components.navbar import render_sidebar
from components.cards import render_header
from api_client import api_client

st.set_page_config(page_title="EduPath AI - Learning Roadmap", page_icon="🗺️", layout="wide")
render_sidebar()

render_header(title="Personalized Learning Roadmap", subtitle="Step-by-step staged learning pathway with milestones, projects, and resources")

user = st.session_state.get("user")
if not user:
    st.warning("⚠️ Please sign in to view and generate learning roadmaps.")
    st.stop()

# Generate Roadmap Section
with st.expander("🚀 Generate New Tailored Roadmap", expanded=False):
    role_input = st.text_input("Target Role for Roadmap", placeholder="e.g. AI Systems Engineer, Full-Stack Developer")
    if st.button("Generate Learning Roadmap", use_container_width=True):
        with st.spinner("Pathway Planner Agent is architecting your curriculum..."):
            res = api_client.generate_roadmap(role_title=role_input.strip() or None)
            if res:
                st.success("Personalized roadmap created successfully!")
                st.rerun()

# Fetch Roadmaps
roadmaps = api_client.get_roadmaps()

if not roadmaps:
    st.info("No roadmaps created yet. Click 'Generate New Tailored Roadmap' to start.")
else:
    for r in roadmaps:
        st.markdown(f"## 🗺️ Roadmap: **{r.get('role_title')}**")
        st.write(r.get("description"))

        milestones = r.get("milestones", [])
        
        # Group milestones by stage
        stages = ["beginner", "intermediate", "advanced"]
        stage_names = {
            "beginner": "🟢 Stage 1: Beginner (Foundations)",
            "intermediate": "🟡 Stage 2: Intermediate (Applied Implementations)",
            "advanced": "🔴 Stage 3: Advanced (Architecture & Production)"
        }

        for stg in stages:
            stg_milestones = [m for m in milestones if m.get("stage") == stg]
            if stg_milestones:
                st.markdown(f"### {stage_names[stg]}")
                for m in stg_milestones:
                    m_id = m.get("id")
                    is_done = m.get("is_completed", False)
                    
                    with st.container():
                        col_check, col_info = st.columns([1, 12])
                        with col_check:
                            new_status = st.checkbox("", value=is_done, key=f"m_chk_{m_id}")
                            if new_status != is_done:
                                api_client.update_milestone(m_id, new_status)
                                st.rerun()
                                
                        with col_info:
                            title_style = "text-decoration: line-through; color: #94A3B8;" if is_done else "font-weight: 700; color: #1E293B;"
                            st.markdown(f"<span style='{title_style} font-size: 16px;'>{m.get('title')}</span>", unsafe_allow_html=True)
                            st.write(m.get("description"))
                            
                            if m.get("project_prompt"):
                                st.markdown(f"🛠️ **Capstone Project:** *{m.get('project_prompt')}*")

                            # Resources
                            resources = m.get("resources_json", [])
                            if resources:
                                res_str = " | ".join([f"[{res.get('name')}]({res.get('type')})" for res in resources])
                                st.caption(f"📚 Resources: {res_str}")
                    st.write("")

        st.divider()
