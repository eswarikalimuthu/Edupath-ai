"""
EduPath AI - Pydantic Request & Response Schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field

# -------------------------------------------------------------
# AUTH SCHEMAS
# -------------------------------------------------------------
class UserRegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=72)
    role: str = "student"

class UserLoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    role: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    role: str
    is_active: bool

# -------------------------------------------------------------
# PROFILE SCHEMAS
# -------------------------------------------------------------
class ProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    education_level: str
    field_of_study: str
    institution: Optional[str] = None
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None
    bio: Optional[str] = None

class SkillAddRequest(BaseModel):
    skill_name: str = Field(min_length=1, max_length=50)
    category: str = "technical"
    proficiency: str = "intermediate"

class InterestAddRequest(BaseModel):
    interest_name: str = Field(min_length=1, max_length=50)
    category: Optional[str] = None
    priority: int = 1

class GoalSetRequest(BaseModel):
    target_role: str = Field(min_length=2, max_length=100)
    target_industry: Optional[str] = None
    timeline_months: int = 12
    notes: Optional[str] = None

# -------------------------------------------------------------
# RECOMMENDATION SCHEMAS
# -------------------------------------------------------------
class RecommendationRequest(BaseModel):
    target_role: Optional[str] = None

# -------------------------------------------------------------
# ROADMAP SCHEMAS
# -------------------------------------------------------------
class RoadmapGenerateRequest(BaseModel):
    role_title: Optional[str] = None

class MilestoneUpdateRequest(BaseModel):
    is_completed: bool

# -------------------------------------------------------------
# CHAT / QA SCHEMAS
# -------------------------------------------------------------
class ChatQueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=3000)
    session_id: str = "default_session"

class CitationResponse(BaseModel):
    citation_id: int
    source: str
    page_number: int
    chunk_id: str
    excerpt: str
    score: float

class ChatQueryResponse(BaseModel):
    answer: str
    citations: List[CitationResponse] = []
    agent_used: str
    is_grounded: bool
    security_alert: bool = False
