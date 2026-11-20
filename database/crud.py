"""
EduPath AI - Database CRUD Operations
Enforces transactional integrity and user-level data isolation.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from database.connection import get_db
from database.models import (
    UserRecord, StudentProfileRecord, SkillRecord,
    InterestRecord, CareerGoalRecord, CareerRecommendationRecord,
    SkillGapRecord, RoadmapRecord, MilestoneRecord,
    ConversationMessageRecord, DocumentMetadataRecord
)

# -------------------------------------------------------------
# USER CRUD
# -------------------------------------------------------------

def create_user(email: str, username: str, hashed_password: str, role: str = "student") -> UserRecord:
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO users (id, email, username, hashed_password, role, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """,
            (user_id, email.lower().strip(), username.strip(), hashed_password, role, now, now)
        )
    return get_user_by_id(user_id)

def get_user_by_id(user_id: str) -> Optional[UserRecord]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            return None
        return UserRecord(**dict(row))

def get_user_by_email(email: str) -> Optional[UserRecord]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),)).fetchone()
        if not row:
            return None
        return UserRecord(**dict(row))

def get_user_by_username(username: str) -> Optional[UserRecord]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE username = ?", (username.strip(),)).fetchone()
        if not row:
            return None
        return UserRecord(**dict(row))

# -------------------------------------------------------------
# STUDENT PROFILE CRUD
# -------------------------------------------------------------

def upsert_student_profile(
    user_id: str,
    full_name: str,
    education_level: str,
    field_of_study: str,
    institution: Optional[str] = None,
    graduation_year: Optional[int] = None,
    gpa: Optional[float] = None,
    bio: Optional[str] = None
) -> StudentProfileRecord:
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM student_profiles WHERE user_id = ?", (user_id,)).fetchone()
        if existing:
            profile_id = existing["id"]
            conn.execute(
                """
                UPDATE student_profiles
                SET full_name = ?, education_level = ?, field_of_study = ?,
                    institution = ?, graduation_year = ?, gpa = ?, bio = ?, updated_at = ?
                WHERE id = ? AND user_id = ?
                """,
                (full_name, education_level, field_of_study, institution, graduation_year, gpa, bio, now, profile_id, user_id)
            )
        else:
            profile_id = str(uuid.uuid4())
            conn.execute(
                """
                INSERT INTO student_profiles (id, user_id, full_name, education_level, field_of_study,
                                             institution, graduation_year, gpa, bio, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (profile_id, user_id, full_name, education_level, field_of_study, institution, graduation_year, gpa, bio, now, now)
            )
    return get_student_profile(user_id)

def get_student_profile(user_id: str) -> Optional[StudentProfileRecord]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM student_profiles WHERE user_id = ?", (user_id,)).fetchone()
        if not row:
            return None
        return StudentProfileRecord(**dict(row))

# -------------------------------------------------------------
# SKILLS CRUD
# -------------------------------------------------------------

def add_skill(user_id: str, skill_name: str, category: str = "technical", proficiency: str = "intermediate") -> SkillRecord:
    skill_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO skills (id, user_id, skill_name, category, proficiency, verified, created_at)
            VALUES (?, ?, ?, ?, ?, 0, ?)
            """,
            (skill_id, user_id, skill_name.strip(), category.lower(), proficiency.lower(), now)
        )
    return SkillRecord(id=skill_id, user_id=user_id, skill_name=skill_name, category=category, proficiency=proficiency)

def get_skills_by_user(user_id: str) -> List[SkillRecord]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM skills WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
        return [SkillRecord(**dict(r)) for r in rows]

def delete_skill(user_id: str, skill_id: str) -> bool:
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM skills WHERE id = ? AND user_id = ?", (skill_id, user_id))
        return cursor.rowcount > 0

# -------------------------------------------------------------
# INTERESTS CRUD
# -------------------------------------------------------------

def add_interest(user_id: str, interest_name: str, category: Optional[str] = None, priority: int = 1) -> InterestRecord:
    interest_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO interests (id, user_id, interest_name, category, priority, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (interest_id, user_id, interest_name.strip(), category, priority, now)
        )
    return InterestRecord(id=interest_id, user_id=user_id, interest_name=interest_name, category=category, priority=priority)

def get_interests_by_user(user_id: str) -> List[InterestRecord]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM interests WHERE user_id = ? ORDER BY priority DESC", (user_id,)).fetchall()
        return [InterestRecord(**dict(r)) for r in rows]

def delete_interest(user_id: str, interest_id: str) -> bool:
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM interests WHERE id = ? AND user_id = ?", (interest_id, user_id))
        return cursor.rowcount > 0

# -------------------------------------------------------------
# CAREER GOALS CRUD
# -------------------------------------------------------------

def set_career_goal(user_id: str, target_role: str, target_industry: Optional[str] = None, timeline_months: int = 12, notes: Optional[str] = None) -> CareerGoalRecord:
    with get_db() as conn:
        conn.execute("DELETE FROM career_goals WHERE user_id = ?", (user_id,))
        goal_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """
            INSERT INTO career_goals (id, user_id, target_role, target_industry, timeline_months, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (goal_id, user_id, target_role.strip(), target_industry, timeline_months, notes, now)
        )
        return CareerGoalRecord(
            id=goal_id, user_id=user_id, target_role=target_role,
            target_industry=target_industry, timeline_months=timeline_months, notes=notes
        )

def get_career_goal(user_id: str) -> Optional[CareerGoalRecord]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM career_goals WHERE user_id = ?", (user_id,)).fetchone()
        if not row:
            return None
        return CareerGoalRecord(**dict(row))

# -------------------------------------------------------------
# CAREER RECOMMENDATIONS & SKILL GAPS CRUD
# -------------------------------------------------------------

def save_career_recommendation(
    user_id: str,
    role_title: str,
    match_percentage: float,
    justification: str,
    key_skills_required: List[str],
    recommended_courses: List[Dict[str, Any]],
    skill_gaps: Optional[List[Dict[str, Any]]] = None
) -> CareerRecommendationRecord:
    rec_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    skills_json = json.dumps(key_skills_required)
    courses_json = json.dumps(recommended_courses)

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO career_recommendations (id, user_id, role_title, match_percentage, justification,
                                               key_skills_required, recommended_courses, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?)
            """,
            (rec_id, user_id, role_title, match_percentage, justification, skills_json, courses_json, now)
        )

        if skill_gaps:
            for gap in skill_gaps:
                gap_id = str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO skill_gaps (id, user_id, recommendation_id, missing_skill, category, importance, recommendation_text, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        gap_id, user_id, rec_id,
                        gap.get("missing_skill", ""),
                        gap.get("category", "technical"),
                        gap.get("importance", "critical"),
                        gap.get("recommendation_text", ""),
                        now
                    )
                )

    return get_career_recommendation_by_id(user_id, rec_id)

def get_career_recommendation_by_id(user_id: str, rec_id: str) -> Optional[CareerRecommendationRecord]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM career_recommendations WHERE id = ? AND user_id = ?", (rec_id, user_id)).fetchone()
        if not row:
            return None
        data = dict(row)
        data["key_skills_required"] = json.loads(data["key_skills_required"]) if data["key_skills_required"] else []
        data["recommended_courses"] = json.loads(data["recommended_courses"]) if data["recommended_courses"] else []
        return CareerRecommendationRecord(**data)

def get_career_recommendations_by_user(user_id: str) -> List[CareerRecommendationRecord]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM career_recommendations WHERE user_id = ? ORDER BY match_percentage DESC", (user_id,)).fetchall()
        results = []
        for r in rows:
            data = dict(r)
            data["key_skills_required"] = json.loads(data["key_skills_required"]) if data["key_skills_required"] else []
            data["recommended_courses"] = json.loads(data["recommended_courses"]) if data["recommended_courses"] else []
            results.append(CareerRecommendationRecord(**data))
        return results

def get_skill_gaps_by_user(user_id: str, recommendation_id: Optional[str] = None) -> List[SkillGapRecord]:
    with get_db() as conn:
        if recommendation_id:
            rows = conn.execute(
                "SELECT * FROM skill_gaps WHERE user_id = ? AND recommendation_id = ? ORDER BY created_at DESC",
                (user_id, recommendation_id)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM skill_gaps WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
        return [SkillGapRecord(**dict(r)) for r in rows]

# -------------------------------------------------------------
# ROADMAPS & MILESTONES CRUD
# -------------------------------------------------------------

def save_roadmap(
    user_id: str,
    role_title: str,
    description: str,
    stages_data: Dict[str, Any],
    milestones_list: List[Dict[str, Any]]
) -> RoadmapRecord:
    roadmap_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    stages_json = json.dumps(stages_data)

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO roadmaps (id, user_id, role_title, description, stages_json, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 'active', ?, ?)
            """,
            (roadmap_id, user_id, role_title, description, stages_json, now, now)
        )

        for idx, m in enumerate(milestones_list):
            m_id = str(uuid.uuid4())
            res_json = json.dumps(m.get("resources", []))
            conn.execute(
                """
                INSERT INTO milestones (id, roadmap_id, user_id, title, stage, description, order_index,
                                        project_prompt, resources_json, is_completed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                """,
                (
                    m_id, roadmap_id, user_id,
                    m.get("title", ""),
                    m.get("stage", "beginner"),
                    m.get("description", ""),
                    idx,
                    m.get("project_prompt", ""),
                    res_json,
                    now
                )
            )

    return get_roadmap_by_id(user_id, roadmap_id)

def get_roadmap_by_id(user_id: str, roadmap_id: str) -> Optional[RoadmapRecord]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM roadmaps WHERE id = ? AND user_id = ?", (roadmap_id, user_id)).fetchone()
        if not row:
            return None
        data = dict(row)
        data["stages_json"] = json.loads(data["stages_json"]) if data["stages_json"] else {}
        return RoadmapRecord(**data)

def get_roadmaps_by_user(user_id: str) -> List[RoadmapRecord]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM roadmaps WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
        results = []
        for r in rows:
            data = dict(r)
            data["stages_json"] = json.loads(data["stages_json"]) if data["stages_json"] else {}
            results.append(RoadmapRecord(**data))
        return results

def get_milestones_by_roadmap(user_id: str, roadmap_id: str) -> List[MilestoneRecord]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM milestones WHERE roadmap_id = ? AND user_id = ? ORDER BY order_index ASC",
            (roadmap_id, user_id)
        ).fetchall()
        results = []
        for r in rows:
            data = dict(r)
            data["resources_json"] = json.loads(data["resources_json"]) if data["resources_json"] else []
            data["is_completed"] = bool(data["is_completed"])
            results.append(MilestoneRecord(**data))
        return results

def update_milestone_completion(user_id: str, milestone_id: str, is_completed: bool) -> Optional[MilestoneRecord]:
    now = datetime.now(timezone.utc).isoformat() if is_completed else None
    with get_db() as conn:
        cursor = conn.execute(
            """
            UPDATE milestones
            SET is_completed = ?, completed_at = ?
            WHERE id = ? AND user_id = ?
            """,
            (1 if is_completed else 0, now, milestone_id, user_id)
        )
        if cursor.rowcount == 0:
            return None
        
        row = conn.execute("SELECT * FROM milestones WHERE id = ?", (milestone_id,)).fetchone()
        if not row:
            return None
        data = dict(row)
        data["resources_json"] = json.loads(data["resources_json"]) if data["resources_json"] else []
        data["is_completed"] = bool(data["is_completed"])
        return MilestoneRecord(**data)

# -------------------------------------------------------------
# CONVERSATION MESSAGES CRUD
# -------------------------------------------------------------

def save_conversation_message(
    user_id: str,
    session_id: str,
    role: str,
    content: str,
    agent_name: Optional[str] = None,
    citations: Optional[List[Dict[str, Any]]] = None
) -> ConversationMessageRecord:
    msg_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    citations_json = json.dumps(citations or [])
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO conversation_messages (id, user_id, session_id, role, content, agent_name, citations_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (msg_id, user_id, session_id, role, content, agent_name, citations_json, now)
        )
    return ConversationMessageRecord(
        id=msg_id, user_id=user_id, session_id=session_id,
        role=role, content=content, agent_name=agent_name,
        citations_json=citations or [], created_at=now
    )

def get_conversation_history(user_id: str, session_id: str, limit: int = 50) -> List[ConversationMessageRecord]:
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM conversation_messages
            WHERE user_id = ? AND session_id = ?
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (user_id, session_id, limit)
        ).fetchall()
        results = []
        for r in rows:
            data = dict(r)
            data["citations_json"] = json.loads(data["citations_json"]) if data["citations_json"] else []
            results.append(ConversationMessageRecord(**data))
        return results

# -------------------------------------------------------------
# DOCUMENT METADATA CRUD
# -------------------------------------------------------------

def register_document(
    filename: str,
    file_path: str,
    file_size: int,
    file_hash: str,
    mime_type: str,
    chunk_count: int,
    user_id: Optional[str] = None,
    is_global: bool = False,
    description: Optional[str] = None
) -> DocumentMetadataRecord:
    doc_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO document_metadata (id, user_id, filename, file_path, file_size, file_hash,
                                          mime_type, chunk_count, is_global, description, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (doc_id, user_id, filename, file_path, file_size, file_hash, mime_type,
             chunk_count, 1 if is_global else 0, description, now)
        )
    return DocumentMetadataRecord(
        id=doc_id, user_id=user_id, filename=filename, file_path=file_path,
        file_size=file_size, file_hash=file_hash, mime_type=mime_type,
        chunk_count=chunk_count, is_global=is_global, description=description, uploaded_at=now
    )

def get_document_by_hash(file_hash: str) -> Optional[DocumentMetadataRecord]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM document_metadata WHERE file_hash = ?", (file_hash,)).fetchone()
        if not row:
            return None
        data = dict(row)
        data["is_global"] = bool(data["is_global"])
        return DocumentMetadataRecord(**data)

def get_documents_accessible_by_user(user_id: Optional[str] = None) -> List[DocumentMetadataRecord]:
    with get_db() as conn:
        if user_id:
            rows = conn.execute(
                """
                SELECT * FROM document_metadata
                WHERE user_id = ? OR is_global = 1
                ORDER BY uploaded_at DESC
                """,
                (user_id,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM document_metadata WHERE is_global = 1 ORDER BY uploaded_at DESC").fetchall()
            
        results = []
        for r in rows:
            data = dict(r)
            data["is_global"] = bool(data["is_global"])
            results.append(DocumentMetadataRecord(**data))
        return results

def delete_document_record(user_id: str, document_id: str) -> bool:
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM document_metadata WHERE id = ? AND (user_id = ? OR ? = 'admin')",
            (document_id, user_id, user_id)
        )
        return cursor.rowcount > 0
