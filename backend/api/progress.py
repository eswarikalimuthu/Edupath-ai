"""
EduPath AI - Student Learning Progress API
"""

from fastapi import APIRouter, Depends
from security.authorization import get_current_user
from database.models import UserRecord
from database.crud import (
    get_skills_by_user, get_roadmaps_by_user,
    get_milestones_by_roadmap, get_career_recommendations_by_user
)

router = APIRouter(prefix="/progress", tags=["Learning Progress"])

@router.get("/summary")
def get_progress_summary(current_user: UserRecord = Depends(get_current_user)):
    skills = get_skills_by_user(current_user.id)
    roadmaps = get_roadmaps_by_user(current_user.id)
    recommendations = get_career_recommendations_by_user(current_user.id)

    total_milestones = 0
    completed_milestones = 0

    for r in roadmaps:
        milestones = get_milestones_by_roadmap(current_user.id, r.id)
        total_milestones += len(milestones)
        completed_milestones += sum(1 for m in milestones if m.is_completed)

    completion_percentage = (
        round((completed_milestones / total_milestones) * 100, 1)
        if total_milestones > 0 else 0.0
    )

    # Category breakdown
    tech_skills = sum(1 for s in skills if s.category == "technical")
    soft_skills = sum(1 for s in skills if s.category == "soft")
    domain_skills = sum(1 for s in skills if s.category == "domain")

    return {
        "user_id": current_user.id,
        "total_skills": len(skills),
        "technical_skills_count": tech_skills,
        "soft_skills_count": soft_skills,
        "domain_skills_count": domain_skills,
        "total_roadmaps": len(roadmaps),
        "total_recommendations": len(recommendations),
        "total_milestones": total_milestones,
        "completed_milestones": completed_milestones,
        "completion_percentage": completion_percentage
    }
