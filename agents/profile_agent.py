"""
EduPath AI - Profile Agent (Agent 1)
Understands student backgrounds, skills, interests, and identifies profile gaps.
"""

from typing import Dict, Any, List
from database.crud import (
    get_student_profile, upsert_student_profile,
    get_skills_by_user, add_skill,
    get_interests_by_user, add_interest,
    get_career_goal, set_career_goal
)
from rag.retriever import get_retriever
from backend.services.llm_service import get_llm_service
from security.prompt_injection import wrap_untrusted_context

class ProfileAgent:
    def __init__(self):
        self.retriever = get_retriever()
        self.llm = get_llm_service()

    def analyze_profile(self, user_id: str, context_message: str = "") -> Dict[str, Any]:
        """
        Synthesize current student profile, retrieve skill taxonomies, and identify missing info.
        """
        profile = get_student_profile(user_id)
        skills = get_skills_by_user(user_id)
        interests = get_interests_by_user(user_id)
        goal = get_career_goal(user_id)

        # 1. Check for missing critical profile fields
        missing_fields = []
        if not profile:
            missing_fields.extend(["Full Name", "Education Level", "Field of Study"])
        else:
            if not profile.education_level:
                missing_fields.append("Education Level")
            if not profile.field_of_study:
                missing_fields.append("Field of Study")
            if not profile.graduation_year:
                missing_fields.append("Graduation Year")

        if not skills:
            missing_fields.append("Technical & Soft Skills")
        if not interests:
            missing_fields.append("Career Interests")
        if not goal:
            missing_fields.append("Target Career Goal")

        # 2. RAG Retrieval for qualification benchmarks
        query = f"Qualification standards for {profile.field_of_study if profile else 'Computer Science and Engineering'}"
        rag_res = self.retriever.retrieve(query=query, user_id=user_id, top_k=2)

        # 3. LLM synthesis
        system_prompt = (
            "You are the EduPath Profile Agent. Your mission is to understand the student's background, "
            "evaluate their skills, and clearly outline what information is complete and what is missing."
        )

        user_prompt = f"""
Student Profile State:
- Name: {profile.full_name if profile else 'Not Provided'}
- Education Level: {profile.education_level if profile else 'Not Provided'}
- Field of Study: {profile.field_of_study if profile else 'Not Provided'}
- Institution: {profile.institution if profile else 'Not Provided'}
- Skills: {[s.skill_name + ' (' + s.proficiency + ')' for s in skills] if skills else 'None recorded'}
- Interests: {[i.interest_name for i in interests] if interests else 'None recorded'}
- Career Goal: {goal.target_role if goal else 'Not defined'}

Retrieved Benchmark Context:
{wrap_untrusted_context([c['text'] for c in rag_res.get('chunks', [])])}

User Note / Message: {context_message}

Provide a concise, encouraging profile summary with actionable feedback on missing items.
"""
        response_text = self.llm.generate(user_prompt, system_instruction=system_prompt)

        return {
            "agent": "ProfileAgent",
            "profile": profile.model_dump() if profile else None,
            "skills": [s.model_dump() for s in skills],
            "interests": [i.model_dump() for i in interests],
            "career_goal": goal.model_dump() if goal else None,
            "missing_fields": missing_fields,
            "analysis_text": response_text,
            "citations": rag_res.get("citations", [])
        }

_profile_agent_instance = None

def get_profile_agent() -> ProfileAgent:
    global _profile_agent_instance
    if _profile_agent_instance is None:
        _profile_agent_instance = ProfileAgent()
    return _profile_agent_instance
