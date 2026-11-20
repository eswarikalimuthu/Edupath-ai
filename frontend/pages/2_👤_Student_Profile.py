"""
EduPath AI - Student Profile Management
Educational qualifications, skills inventory, interests, and target goals.
"""

import streamlit as st
from components.navbar import render_sidebar
from components.cards import render_header
from api_client import api_client

st.set_page_config(page_title="EduPath AI - Student Profile", page_icon="👤", layout="wide")
render_sidebar()

render_header(title="Student Profile & Skill Inventory", subtitle="Maintain your academic background, technical proficiencies, and career ambitions")

user = st.session_state.get("user")
if not user:
    st.warning("⚠️ Please sign in on the Auth page to view and update your profile.")
    st.stop()

# Fetch Profile Data
profile_data = api_client.get_profile()
prof = profile_data.get("profile") or {}
skills = profile_data.get("skills") or []
interests = profile_data.get("interests") or []
goal = profile_data.get("career_goal") or {}

col_left, col_right = st.columns([3, 2])

# Left Column: Academic Background & Qualifications
with col_left:
    st.subheader("🎓 Academic Background")
    with st.form("profile_form"):
        full_name = st.text_input("Full Name", value=prof.get("full_name", ""))
        c1, c2 = st.columns(2)
        with c1:
            edu_level = st.selectbox(
                "Education Level",
                ["High School", "Diploma", "Undergraduate (B.Tech / B.S.)", "Postgraduate (M.Tech / M.S.)", "Ph.D.", "Other"],
                index=2
            )
            institution = st.text_input("Institution / University", value=prof.get("institution", ""))
        with c2:
            field_of_study = st.text_input("Field of Study / Major", value=prof.get("field_of_study", "Computer Science"))
            grad_year = st.number_input("Graduation Year", min_value=2000, max_value=2035, value=prof.get("graduation_year") or 2026)
            
        gpa = st.number_input("GPA / Percentage", min_value=0.0, max_value=10.0, value=float(prof.get("gpa") or 8.5), step=0.1)
        bio = st.text_area("Personal Bio & Career Aspiration", value=prof.get("bio", ""))
        
        save_profile = st.form_submit_button("Save Academic Profile", use_container_width=True)
        if save_profile:
            with st.spinner("Saving..."):
                res = api_client.update_profile({
                    "full_name": full_name,
                    "education_level": edu_level,
                    "field_of_study": field_of_study,
                    "institution": institution,
                    "graduation_year": grad_year,
                    "gpa": gpa,
                    "bio": bio
                })
                st.success("Profile updated successfully!")
                st.rerun()

    st.divider()
    st.subheader("🎯 Target Career Goal")
    with st.form("goal_form"):
        target_role = st.text_input("Target Career Role", value=goal.get("target_role", "AI Application Engineer"))
        target_ind = st.text_input("Target Industry", value=goal.get("target_industry", "Information Technology & AI"))
        timeline = st.slider("Target Timeline (Months)", min_value=3, max_value=36, value=goal.get("timeline_months", 12))
        save_goal = st.form_submit_button("Set Career Goal", use_container_width=True)
        if save_goal:
            api_client.set_goal(target_role, target_ind, timeline)
            st.success("Career goal updated!")
            st.rerun()

# Right Column: Skills & Interests Inventory
with col_right:
    st.subheader("⚡ Skills Inventory")
    
    # Display Current Skills
    if skills:
        for s in skills:
            sc1, sc2, sc3 = st.columns([3, 2, 1])
            with sc1:
                st.markdown(f"**{s.get('skill_name')}**")
            with sc2:
                cat_color = "#2563EB" if s.get("category") == "technical" else "#10B981"
                st.markdown(f"<span style='color:{cat_color}; font-size:12px; font-weight:600;'>{s.get('category').upper()} ({s.get('proficiency')})</span>", unsafe_allow_html=True)
            with sc3:
                if st.button("🗑️", key=f"del_skill_{s.get('id')}"):
                    api_client.delete_skill(s.get("id"))
                    st.rerun()
    else:
        st.caption("No skills added yet. Add your technical and soft skills below.")

    # Add Skill Form
    with st.expander("➕ Add New Skill", expanded=False):
        new_skill = st.text_input("Skill Name (e.g. Python, Docker, Public Speaking)")
        c_cat, c_prof = st.columns(2)
        with c_cat:
            skill_cat = st.selectbox("Category", ["technical", "soft", "domain"])
        with c_prof:
            skill_prof = st.selectbox("Proficiency", ["beginner", "intermediate", "advanced", "expert"])
        if st.button("Add Skill", use_container_width=True):
            if new_skill.strip():
                api_client.add_skill(new_skill.strip(), skill_cat, skill_prof)
                st.success(f"Added {new_skill}!")
                st.rerun()

    st.divider()
    st.subheader("💡 Career Interests")
    if interests:
        for i in interests:
            ic1, ic2 = st.columns([4, 1])
            with ic1:
                st.markdown(f"• **{i.get('interest_name')}** ({i.get('category') or 'General'})")
            with ic2:
                if st.button("🗑️", key=f"del_int_{i.get('id')}"):
                    api_client.delete_interest(i.get("id"))
                    st.rerun()
    else:
        st.caption("No interests listed yet.")

    with st.expander("➕ Add New Interest", expanded=False):
        new_int = st.text_input("Interest Name (e.g. Robotics, Cloud Architecture)")
        int_cat = st.text_input("Interest Field", value="AI / Engineering")
        if st.button("Add Interest", use_container_width=True):
            if new_int.strip():
                api_client.add_interest(new_int.strip(), int_cat)
                st.success(f"Added {new_int}!")
                st.rerun()
