"""
EduPath AI - Pathway Planner Agent (Agent 4)
Builds structured learning roadmaps divided into Beginner, Intermediate, and Advanced stages.
"""

from typing import Dict, Any, List
from database.crud import (
    get_student_profile, get_skills_by_user,
    get_career_goal, save_roadmap,
    get_roadmaps_by_user, get_milestones_by_roadmap,
    update_milestone_completion
)
from rag.retriever import get_retriever
from backend.services.llm_service import get_llm_service
from security.prompt_injection import wrap_untrusted_context

class PathwayPlannerAgent:
    def __init__(self):
        self.retriever = get_retriever()
        self.llm = get_llm_service()

    def generate_roadmap(self, user_id: str, role_title: str = "") -> Dict[str, Any]:
        """
        Generate a personalized 3-stage learning roadmap (Beginner, Intermediate, Advanced).
        """
        profile = get_student_profile(user_id)
        skills = get_skills_by_user(user_id)
        goal = get_career_goal(user_id)

        target_role = role_title or (goal.target_role if goal else "AI Application Engineer")

        # 1. Retrieve curriculum guidelines and learning resources
        query = f"Curriculum and learning roadmap for {target_role} prerequisites projects"
        rag_res = self.retriever.retrieve(query=query, user_id=user_id, top_k=3)

        # 2. Formulate LLM synthesis prompt
        system_prompt = (
            "You are the EduPath Pathway Planner Agent. Structure clear, realistic learning pathways. "
            "Divide into Beginner (foundations), Intermediate (applied implementations), and Advanced (system architecture/projects). "
            "Every stage must have concrete milestone objectives and hands-on projects."
        )

        user_prompt = f"""
Target Role: {target_role}
Student Current Degree: {profile.education_level if profile else 'Student'} in {profile.field_of_study if profile else 'Technology'}
Existing Skills: {', '.join([s.skill_name for s in skills]) if skills else 'Basic computer skills'}

Reference Curriculum Context:
{wrap_untrusted_context([c['text'] for c in rag_res.get('chunks', [])])}

Generate a structured multi-stage roadmap for this student.
"""
        roadmap_text = self.llm.generate(user_prompt, system_instruction=system_prompt)

        # 3. Create structured milestone data
        milestones = [
            {
                "title": "Stage 1: Core Programming & Computational Foundations",
                "stage": "beginner",
                "description": "Master core Python syntax, algorithms, data structures, and Git version control.",
                "project_prompt": "Develop an algorithmic data parsing CLI utility with unit tests.",
                "resources": [{"name": "Official Python Tutorial", "type": "Documentation"}, {"name": "CS50 Computer Science", "type": "Course"}]
            },
            {
                "title": "Stage 2: Backend REST APIs & Relational Database Design",
                "stage": "intermediate",
                "description": "Build high-performance REST APIs with FastAPI, SQLite WAL mode, and Pydantic validation.",
                "project_prompt": "Build an authenticated multi-tenant task and resource management API.",
                "resources": [{"name": "FastAPI Official Documentation", "type": "Docs"}, {"name": "Full-Stack Web APIs", "type": "Course"}]
            },
            {
                "title": "Stage 3: Vector Databases & Hybrid RAG Architecture",
                "stage": "intermediate",
                "description": "Implement ChromaDB embeddings, BM25 Okapi lexical search, and reciprocal rank fusion.",
                "project_prompt": "Build an end-to-end RAG document search engine with verifiable citations.",
                "resources": [{"name": "ChromaDB Concepts & Guides", "type": "Docs"}, {"name": "Information Retrieval Basics", "type": "Article"}]
            },
            {
                "title": "Stage 4: Multi-Agent Systems & LangGraph Production Deployment",
                "stage": "advanced",
                "description": "Orchestrate multi-agent workflows using LangGraph, cyclical states, and automated evaluation.",
                "project_prompt": "Deploy an autonomous multi-agent guidance assistant with comprehensive evaluation metrics.",
                "resources": [{"name": "LangGraph Production Guide", "type": "Docs"}, {"name": "DeepLearning.AI Multi-Agent Systems", "type": "Course"}]
            }
        ]

        stages_data = {
            "beginner": {"duration_weeks": 4, "focus": "Foundations & Scripting"},
            "intermediate": {"duration_weeks": 6, "focus": "Backend, Databases & RAG"},
            "advanced": {"duration_weeks": 6, "focus": "Agent Orchestration & Enterprise Evaluation"}
        }

        # 4. Save to database
        saved_roadmap = save_roadmap(
            user_id=user_id,
            role_title=target_role,
            description=roadmap_text[:300] + "...",
            stages_data=stages_data,
            milestones_list=milestones
        )

        return {
            "agent": "PathwayPlannerAgent",
            "roadmap_id": saved_roadmap.id,
            "role_title": target_role,
            "stages": stages_data,
            "milestones": milestones,
            "overview_text": roadmap_text,
            "citations": rag_res.get("citations", [])
        }

    def update_progress(self, user_id: str, milestone_id: str, completed: bool) -> Dict[str, Any]:
        """Update student milestone completion."""
        updated = update_milestone_completion(user_id, milestone_id, completed)
        return {
            "status": "success" if updated else "not_found",
            "milestone": updated.model_dump() if updated else None
        }

_pathway_agent_instance = None

def get_pathway_planner_agent() -> PathwayPlannerAgent:
    global _pathway_agent_instance
    if _pathway_agent_instance is None:
        _pathway_agent_instance = PathwayPlannerAgent()
    return _pathway_agent_instance
