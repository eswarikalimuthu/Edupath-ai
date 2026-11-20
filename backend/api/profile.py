"""
EduPath AI - Student Profile API Endpoints
Manages profile qualifications, technical & soft skills, interests, and target career goals.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from security.authorization import get_current_user
from database.models import UserRecord
from database.crud import (
    upsert_student_profile, get_student_profile,
    add_skill, get_skills_by_user, delete_skill,
    add_interest, get_interests_by_user, delete_interest,
    set_career_goal, get_career_goal
)
from backend.schemas import (
    ProfileUpdateRequest, SkillAddRequest, InterestAddRequest, GoalSetRequest
)

router = APIRouter(prefix="/profile", tags=["Student Profile"])

@router.get("")
def get_my_profile(current_user: UserRecord = Depends(get_current_user)):
    profile = get_student_profile(current_user.id)
    skills = get_skills_by_user(current_user.id)
    interests = get_interests_by_user(current_user.id)
    goal = get_career_goal(current_user.id)

    return {
        "profile": profile.model_dump() if profile else None,
        "skills": [s.model_dump() for s in skills],
        "interests": [i.model_dump() for i in interests],
        "career_goal": goal.model_dump() if goal else None
    }

@router.put("")
def update_profile(req: ProfileUpdateRequest, current_user: UserRecord = Depends(get_current_user)):
    profile = upsert_student_profile(
        user_id=current_user.id,
        full_name=req.full_name,
        education_level=req.education_level,
        field_of_study=req.field_of_study,
        institution=req.institution,
        graduation_year=req.graduation_year,
        gpa=req.gpa,
        bio=req.bio
    )
    return {"status": "success", "profile": profile.model_dump()}

@router.post("/skills", status_code=status.HTTP_201_CREATED)
def add_new_skill(req: SkillAddRequest, current_user: UserRecord = Depends(get_current_user)):
    skill = add_skill(
        user_id=current_user.id,
        skill_name=req.skill_name,
        category=req.category,
        proficiency=req.proficiency
    )
    return {"status": "success", "skill": skill.model_dump()}

@router.delete("/skills/{skill_id}")
def remove_skill(skill_id: str, current_user: UserRecord = Depends(get_current_user)):
    success = delete_skill(current_user.id, skill_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found or unauthorized")
    return {"status": "success", "message": "Skill deleted"}

@router.post("/interests", status_code=status.HTTP_201_CREATED)
def add_new_interest(req: InterestAddRequest, current_user: UserRecord = Depends(get_current_user)):
    interest = add_interest(
        user_id=current_user.id,
        interest_name=req.interest_name,
        category=req.category,
        priority=req.priority
    )
    return {"status": "success", "interest": interest.model_dump()}

@router.delete("/interests/{interest_id}")
def remove_interest(interest_id: str, current_user: UserRecord = Depends(get_current_user)):
    success = delete_interest(current_user.id, interest_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interest not found or unauthorized")
    return {"status": "success", "message": "Interest deleted"}

@router.post("/goal")
def set_target_goal(req: GoalSetRequest, current_user: UserRecord = Depends(get_current_user)):
    goal = set_career_goal(
        user_id=current_user.id,
        target_role=req.target_role,
        target_industry=req.target_industry,
        timeline_months=req.timeline_months,
        notes=req.notes
    )
    return {"status": "success", "career_goal": goal.model_dump()}
