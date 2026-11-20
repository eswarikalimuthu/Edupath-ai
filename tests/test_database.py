"""
EduPath AI - Database CRUD & Data Isolation Unit Tests
"""

import pytest
import uuid
from database.connection import init_db
from database.crud import (
    create_user, get_user_by_id, get_user_by_email,
    upsert_student_profile, get_student_profile,
    add_skill, get_skills_by_user, delete_skill,
    add_interest, get_interests_by_user,
    set_career_goal, get_career_goal,
    save_career_recommendation, get_career_recommendations_by_user,
    save_roadmap, get_roadmaps_by_user, update_milestone_completion,
    get_milestones_by_roadmap
)
from security.password import hash_password

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_user_creation_and_retrieval():
    uid_str = str(uuid.uuid4())[:8]
    email = f"user_{uid_str}@edupath.ai"
    username = f"user_{uid_str}"
    pwd = hash_password("SecurePass123!")
    
    user = create_user(email=email, username=username, hashed_password=pwd)
    assert user.id is not None
    assert user.email == email
    assert user.username == username

    fetched = get_user_by_email(email)
    assert fetched.id == user.id

def test_student_profile_upsert():
    uid_str = str(uuid.uuid4())[:8]
    user = create_user(f"prof_{uid_str}@edupath.ai", f"prof_{uid_str}", hash_password("Pass123!"))

    p1 = upsert_student_profile(
        user_id=user.id,
        full_name="Samantha Ray",
        education_level="Undergraduate",
        field_of_study="Robotics & AI"
    )
    assert p1.full_name == "Samantha Ray"

    # Update profile
    p2 = upsert_student_profile(
        user_id=user.id,
        full_name="Samantha Ray-Updated",
        education_level="Postgraduate",
        field_of_study="Robotics & AI"
    )
    assert p2.full_name == "Samantha Ray-Updated"
    assert p2.education_level == "Postgraduate"

def test_user_skills_and_isolation():
    u1 = create_user(f"u1_{uuid.uuid4().hex[:6]}@edupath.ai", f"u1_{uuid.uuid4().hex[:6]}", hash_password("Pass123!"))
    u2 = create_user(f"u2_{uuid.uuid4().hex[:6]}@edupath.ai", f"u2_{uuid.uuid4().hex[:6]}", hash_password("Pass123!"))

    s1 = add_skill(u1.id, "Python", "technical", "advanced")
    s2 = add_skill(u2.id, "Go", "technical", "intermediate")

    u1_skills = get_skills_by_user(u1.id)
    u2_skills = get_skills_by_user(u2.id)

    assert any(s.skill_name == "Python" for s in u1_skills)
    assert not any(s.skill_name == "Go" for s in u1_skills), "Cross-user data leakage detected"
    assert any(s.skill_name == "Go" for s in u2_skills)

def test_roadmap_milestone_completion():
    u = create_user(f"rm_{uuid.uuid4().hex[:6]}@edupath.ai", f"rm_{uuid.uuid4().hex[:6]}", hash_password("Pass123!"))
    
    stages_data = {"beginner": {"duration": 4}}
    milestones = [{"title": "Milestone 1", "stage": "beginner", "description": "Intro"}]
    
    rm = save_roadmap(u.id, "Cloud Architect", "Cloud training", stages_data, milestones)
    ms = get_milestones_by_roadmap(u.id, rm.id)
    assert len(ms) == 1
    m = ms[0]
    assert not m.is_completed

    # Toggle completion
    updated_m = update_milestone_completion(u.id, m.id, True)
    assert updated_m.is_completed
    assert updated_m.completed_at is not None
