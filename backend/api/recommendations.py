"""
EduPath AI - Career Recommendations & Skill Gap Analysis API
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from security.authorization import get_current_user
from database.models import UserRecord
from database.crud import (
    get_career_recommendations_by_user,
    get_career_recommendation_by_id,
    get_skill_gaps_by_user
)
from agents.recommendation_agent import get_recommendation_agent
from backend.schemas import RecommendationRequest

router = APIRouter(prefix="/recommendations", tags=["Career Recommendations"])

@router.post("/generate")
def generate_recommendations(
    req: RecommendationRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    agent = get_recommendation_agent()
    result = agent.generate_recommendations(
        user_id=current_user.id,
        custom_focus=req.target_role or ""
    )
    return result

@router.get("")
def list_recommendations(current_user: UserRecord = Depends(get_current_user)):
    recs = get_career_recommendations_by_user(current_user.id)
    return [r.model_dump() for r in recs]

@router.get("/gaps")
def list_skill_gaps(
    recommendation_id: Optional[str] = None,
    current_user: UserRecord = Depends(get_current_user)
):
    gaps = get_skill_gaps_by_user(current_user.id, recommendation_id=recommendation_id)
    return [g.model_dump() for g in gaps]
