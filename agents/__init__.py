"""
EduPath AI - Agents Package
"""

from agents.profile_agent import get_profile_agent, ProfileAgent
from agents.retrieval_agent import get_retrieval_agent, RetrievalAgent
from agents.recommendation_agent import get_recommendation_agent, RecommendationAgent
from agents.pathway_planner_agent import get_pathway_planner_agent, PathwayPlannerAgent
from agents.qa_agent import get_qa_agent, QAAgent

__all__ = [
    "get_profile_agent",
    "ProfileAgent",
    "get_retrieval_agent",
    "RetrievalAgent",
    "get_recommendation_agent",
    "RecommendationAgent",
    "get_pathway_planner_agent",
    "PathwayPlannerAgent",
    "get_qa_agent",
    "QAAgent",
]
