"""
EduPath AI - Database Data Models
Pydantic models representing internal database entities and records.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserRecord(BaseModel):
    id: str
    email: EmailStr
    username: str
    hashed_password: str
    role: str = "student"
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class StudentProfileRecord(BaseModel):
    id: str
    user_id: str
    full_name: str
    education_level: str
    field_of_study: str
    institution: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    bio: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class SkillRecord(BaseModel):
    id: str
    user_id: str
    skill_name: str
    category: str = "technical"  # technical, soft, domain
    proficiency: str = "intermediate"  # beginner, intermediate, advanced, expert
    verified: bool = False
    created_at: Optional[datetime] = None

class InterestRecord(BaseModel):
    id: str
    user_id: str
    interest_name: str
    category: Optional[str] = None
    priority: int = 1
    created_at: Optional[datetime] = None

class CareerGoalRecord(BaseModel):
    id: str
    user_id: str
    target_role: str
    target_industry: Optional[str] = None
    timeline_months: int = 12
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

class CareerRecommendationRecord(BaseModel):
    id: str
    user_id: str
    role_title: str
    match_percentage: float
    justification: str
    key_skills_required: List[str] = Field(default_factory=list)
    recommended_courses: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "active"
    created_at: Optional[datetime] = None

class SkillGapRecord(BaseModel):
    id: str
    user_id: str
    recommendation_id: Optional[str] = None
    missing_skill: str
    category: Optional[str] = "technical"
    importance: str = "critical"  # critical, moderate, optional
    recommendation_text: Optional[str] = None
    created_at: Optional[datetime] = None

class RoadmapRecord(BaseModel):
    id: str
    user_id: str
    role_title: str
    description: Optional[str] = None
    stages_json: Dict[str, Any] = Field(default_factory=dict)
    status: str = "active"  # active, completed, archived
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class MilestoneRecord(BaseModel):
    id: str
    roadmap_id: str
    user_id: str
    title: str
    stage: str  # beginner, intermediate, advanced
    description: Optional[str] = None
    order_index: int = 0
    project_prompt: Optional[str] = None
    resources_json: List[Dict[str, Any]] = Field(default_factory=list)
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

class ConversationMessageRecord(BaseModel):
    id: str
    user_id: str
    session_id: str
    role: str  # user, assistant, system
    content: str
    agent_name: Optional[str] = None
    citations_json: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: Optional[datetime] = None

class DocumentMetadataRecord(BaseModel):
    id: str
    user_id: Optional[str] = None
    filename: str
    file_path: str
    file_size: int
    file_hash: str
    mime_type: str
    chunk_count: int = 0
    is_global: bool = False
    description: Optional[str] = None
    uploaded_at: Optional[datetime] = None
