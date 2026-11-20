"""
EduPath AI - Recommendation Agent (Agent 3)
Generates grounded career recommendations and performs skill gap analysis.
"""

from typing import Dict, Any, List
from database.crud import (
    get_student_profile, get_skills_by_user,
    get_interests_by_user, get_career_goal,
    save_career_recommendation
)
from rag.retriever import get_retriever
from backend.services.llm_service import get_llm_service
from security.prompt_injection import wrap_untrusted_context

class RecommendationAgent:
    def __init__(self):
        self.retriever = get_retriever()
        self.llm = get_llm_service()

    def generate_recommendations(self, user_id: str, custom_focus: str = "") -> Dict[str, Any]:
        """
        Analyze student profile and retrieve verified career requirements to generate recommendations.
        """
        profile = get_student_profile(user_id)
        skills = get_skills_by_user(user_id)
        interests = get_interests_by_user(user_id)
        goal = get_career_goal(user_id)

        target = custom_focus or (goal.target_role if goal else "Software and AI Engineering")
        
        # 1. Retrieve verified industry benchmarks for this domain
        query = f"Career requirements, essential skills, and certifications for {target}"
        rag_res = self.retriever.retrieve(query=query, user_id=user_id, top_k=3)

        # 2. Match Analysis
        student_skill_names = [s.skill_name.lower() for s in skills]
        
        # Standard skill taxonomies for key careers
        benchmark_skills = ["python", "machine learning", "data structures", "fastapi", "sql", "git", "cloud"]
        matched_skills = [s for s in benchmark_skills if s in student_skill_names]
        missing_skills = [s for s in benchmark_skills if s not in student_skill_names]

        match_score = round(max(45.0, min(95.0, (len(matched_skills) / max(len(benchmark_skills), 1)) * 100)), 1)

        # 3. Formulate LLM Prompt with Grounded Context
        system_prompt = (
            "You are the EduPath Career Recommendation Agent. Ground all recommendations strictly in verified "
            "industry standards and the provided reference documents. Provide clear justifications, pinpoint "
            "concrete skill gaps, and suggest high-yield courses."
        )

        user_prompt = f"""
Student Background:
- Degree: {profile.education_level if profile else 'Undergraduate'} in {profile.field_of_study if profile else 'Computer Science'}
- Existing Skills: {', '.join([s.skill_name for s in skills]) if skills else 'None specified'}
- Career Goal: {target}

Retrieved Industry Standards & Course Context:
{wrap_untrusted_context([c['text'] for c in rag_res.get('chunks', [])])}

Generate a comprehensive recommendation report:
1. Target Role & Match Assessment ({match_score}%)
2. Justification grounded in their background
3. Concrete Skill Gap Breakdown (Critical, Moderate, Optional)
4. Recommended Courses & Certifications
"""
        recommendation_text = self.llm.generate(user_prompt, system_instruction=system_prompt)

        # 4. Save to Database
        key_skills = benchmark_skills[:5]
        courses = [
            {"title": "Full-Stack AI & Deep Learning Specialization", "provider": "DeepLearning.AI", "duration": "8 weeks"},
            {"title": "FastAPI & Distributed Microservices Masterclass", "provider": "Coursera", "duration": "4 weeks"},
            {"title": "Vector Databases and Production RAG Systems", "provider": "EduPath Verified", "duration": "3 weeks"}
        ]
        skill_gaps = [
            {"missing_skill": s.title(), "category": "technical", "importance": "critical" if idx == 0 else "moderate",
             "recommendation_text": f"Complete targeted hands-on modules in {s.title()}"}
            for idx, s in enumerate(missing_skills[:3])
        ]

        rec_record = save_career_recommendation(
            user_id=user_id,
            role_title=target.title(),
            match_percentage=match_score,
            justification=recommendation_text[:300] + "...",
            key_skills_required=key_skills,
            recommended_courses=courses,
            skill_gaps=skill_gaps
        )

        return {
            "agent": "RecommendationAgent",
            "recommendation_id": rec_record.id,
            "target_role": target.title(),
            "match_percentage": match_score,
            "justification": recommendation_text,
            "key_skills_required": key_skills,
            "recommended_courses": courses,
            "skill_gaps": skill_gaps,
            "citations": rag_res.get("citations", [])
        }

_recommendation_agent_instance = None

def get_recommendation_agent() -> RecommendationAgent:
    global _recommendation_agent_instance
    if _recommendation_agent_instance is None:
        _recommendation_agent_instance = RecommendationAgent()
    return _recommendation_agent_instance
