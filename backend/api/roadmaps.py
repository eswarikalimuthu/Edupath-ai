"""
EduPath AI - Personalized Learning Roadmaps API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from security.authorization import get_current_user
from database.models import UserRecord
from database.crud import (
    get_roadmaps_by_user, get_roadmap_by_id,
    get_milestones_by_roadmap, update_milestone_completion
)
from agents.pathway_planner_agent import get_pathway_planner_agent
from backend.schemas import RoadmapGenerateRequest, MilestoneUpdateRequest

router = APIRouter(prefix="/roadmaps", tags=["Learning Roadmaps"])

@router.post("/generate")
def generate_roadmap(
    req: RoadmapGenerateRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    agent = get_pathway_planner_agent()
    result = agent.generate_roadmap(
        user_id=current_user.id,
        role_title=req.role_title or ""
    )
    return result

@router.get("")
def list_my_roadmaps(current_user: UserRecord = Depends(get_current_user)):
    roadmaps = get_roadmaps_by_user(current_user.id)
    results = []
    for r in roadmaps:
        milestones = get_milestones_by_roadmap(current_user.id, r.id)
        data = r.model_dump()
        data["milestones"] = [m.model_dump() for m in milestones]
        results.append(data)
    return results

@router.get("/{roadmap_id}")
def get_roadmap(roadmap_id: str, current_user: UserRecord = Depends(get_current_user)):
    roadmap = get_roadmap_by_id(current_user.id, roadmap_id)
    if not roadmap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    milestones = get_milestones_by_roadmap(current_user.id, roadmap.id)
    data = roadmap.model_dump()
    data["milestones"] = [m.model_dump() for m in milestones]
    return data

@router.put("/milestones/{milestone_id}")
def toggle_milestone(
    milestone_id: str,
    req: MilestoneUpdateRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    agent = get_pathway_planner_agent()
    result = agent.update_progress(
        user_id=current_user.id,
        milestone_id=milestone_id,
        completed=req.is_completed
    )
    if result["status"] == "not_found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")
    return result
