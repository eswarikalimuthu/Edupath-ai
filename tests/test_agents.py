"""
EduPath AI - Agents & LangGraph Workflow Unit Tests
"""

import pytest
import uuid
from database.connection import init_db
from database.crud import create_user, upsert_student_profile, add_skill, set_career_goal
from security.password import hash_password
from agents.profile_agent import get_profile_agent
from agents.retrieval_agent import get_retrieval_agent
from agents.recommendation_agent import get_recommendation_agent
from agents.pathway_planner_agent import get_pathway_planner_agent
from agents.qa_agent import get_qa_agent
from graph.workflow import run_agent_workflow

@pytest.fixture(scope="module")
def test_user():
    init_db()
    uid = uuid.uuid4().hex[:8]
    user = create_user(f"agent_test_{uid}@edupath.ai", f"agent_{uid}", hash_password("Pass123!"))
    upsert_student_profile(user.id, "Jordan Lee", "B.Tech", "Computer Science")
    add_skill(user.id, "Python", "technical", "advanced")
    add_skill(user.id, "Machine Learning", "technical", "intermediate")
    set_career_goal(user.id, "AI Systems Engineer", "AI/ML", 12)
    return user

def test_profile_agent(test_user):
    agent = get_profile_agent()
    res = agent.analyze_profile(test_user.id)
    assert res["agent"] == "ProfileAgent"
    assert res["profile"]["full_name"] == "Jordan Lee"
    assert len(res["skills"]) >= 2

def test_retrieval_agent(test_user):
    agent = get_retrieval_agent()
    res = agent.search_knowledge_base("Python and Machine Learning", user_id=test_user.id)
    assert res["agent"] == "RetrievalAgent"
    assert "chunks_count" in res

def test_recommendation_agent(test_user):
    agent = get_recommendation_agent()
    res = agent.generate_recommendations(test_user.id, custom_focus="AI Systems Engineer")
    assert res["agent"] == "RecommendationAgent"
    assert res["match_percentage"] > 0
    assert len(res["recommended_courses"]) > 0

def test_pathway_planner_agent(test_user):
    agent = get_pathway_planner_agent()
    res = agent.generate_roadmap(test_user.id, role_title="AI Systems Engineer")
    assert res["agent"] == "PathwayPlannerAgent"
    assert len(res["milestones"]) > 0
    assert "beginner" in res["stages"]

def test_qa_agent(test_user):
    agent = get_qa_agent()
    res = agent.answer_question("What skills are required for an AI Engineer?", user_id=test_user.id)
    assert res["agent"] == "QAAgent"
    assert len(res["answer"]) > 10

def test_langgraph_workflow_routing(test_user):
    # Test routing to recommendation
    r1 = run_agent_workflow("Recommend career opportunities for my profile", user_id=test_user.id)
    assert r1["agent_used"] == "RecommendationAgent"

    # Test routing to roadmap
    r2 = run_agent_workflow("Give me a step-by-step learning roadmap", user_id=test_user.id)
    assert r2["agent_used"] == "PathwayPlannerAgent"

    # Test routing to Q&A
    r3 = run_agent_workflow("What is the difference between supervised and unsupervised learning?", user_id=test_user.id)
    assert r3["agent_used"] == "QAAgent"
