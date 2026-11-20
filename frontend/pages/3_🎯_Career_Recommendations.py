"""
EduPath AI - Career Recommendations
AI-driven career matching grounded in verified educational documents and industry standards.
"""

import streamlit as st
from components.navbar import render_sidebar
from components.cards import render_header
from components.charts import create_gauge_chart
from api_client import api_client

st.set_page_config(page_title="EduPath AI - Career Recommendations", page_icon="🎯", layout="wide")
render_sidebar()

render_header(title="Career Path Recommendations", subtitle="Personalized career trajectory recommendations grounded in verified market standards")

user = st.session_state.get("user")
if not user:
    st.warning("⚠️ Please sign in to view and generate career recommendations.")
    st.stop()

col_act1, col_act2 = st.columns([3, 1])
with col_act1:
    target_role_input = st.text_input("Custom Focus / Target Role (Optional)", placeholder="Leave blank to use profile goal")
with col_act2:
    st.write("")
    st.write("")
    generate_btn = st.button("🚀 Generate New Recommendations", use_container_width=True)

if generate_btn:
    with st.spinner("Analyzing profile & searching verified industry standards..."):
        res = api_client.generate_recommendations(target_role=target_role_input.strip() or None)
        if res:
            st.success("New career analysis generated successfully!")
            st.rerun()

# Display Existing Recommendations
recs = api_client.get_recommendations()

if not recs:
    st.info("No recommendations generated yet. Click 'Generate New Recommendations' to begin.")
else:
    for idx, r in enumerate(recs):
        with st.container():
            st.markdown(f"### 🎯 Option {idx+1}: **{r.get('role_title')}**")
            
            c_score, c_detail = st.columns([1, 2])
            with c_score:
                st.plotly_chart(create_gauge_chart(r.get("match_percentage", 0.0), "Role Compatibility"), use_container_width=True)
            with c_detail:
                st.markdown("#### 💡 AI Mentor Justification:")
                st.write(r.get("justification"))
                
                # Key Skills
                key_skills = r.get("key_skills_required") or []
                if key_skills:
                    st.markdown("**Key Required Skills:**")
                    st.markdown(" ".join([f"`{k}`" for k in key_skills]))
            
            # Recommended Courses
            courses = r.get("recommended_courses") or []
            if courses:
                st.markdown("#### 🎓 Recommended Verified Courses:")
                cols = st.columns(len(courses))
                for c_idx, course in enumerate(courses):
                    with cols[c_idx]:
                        st.info(f"**{course.get('title')}**\n\nProvider: {course.get('provider')}\nDuration: {course.get('duration')}")
            
            st.divider()
