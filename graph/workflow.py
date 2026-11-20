"""
EduPath AI - LangGraph Multi-Agent Orchestration Workflow
Orchestrates Profile, Retrieval, Recommendation, Pathway, and Q&A agents.
"""

import re
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from graph.state import EduPathState
from agents.profile_agent import get_profile_agent
from agents.retrieval_agent import get_retrieval_agent
from agents.recommendation_agent import get_recommendation_agent
from agents.pathway_planner_agent import get_pathway_planner_agent
from agents.qa_agent import get_qa_agent

# -------------------------------------------------------------------------
# NODES
# -------------------------------------------------------------------------

def classify_intent_node(state: EduPathState) -> Dict[str, Any]:
    """
    Classify user request to determine the primary handling agent.
    """
    user_input = state.get("user_input", "").lower().strip()
    
    # Priority-based intent classification
    if any(k in user_input for k in ["recommend", "career path", "career choice", "what job", "suitable role", "gap analysis", "skill gap"]):
        intent = "recommendation"
    elif any(k in user_input for k in ["roadmap", "learning path", "curriculum", "milestone", "how to learn", "study plan"]):
        intent = "roadmap"
    elif any(k in user_input for k in ["profile", "my skills", "education", "qualifications", "who am i", "my background"]):
        intent = "profile"
    elif any(k in user_input for k in ["search doc", "lookup document", "find in documents", "retrieval search"]):
        intent = "retrieval"
    else:
        intent = "qa"

    return {"intent": intent}

def profile_agent_node(state: EduPathState) -> Dict[str, Any]:
    agent = get_profile_agent()
    user_id = state.get("user_id", "default_user")
    res = agent.analyze_profile(user_id=user_id, context_message=state.get("user_input", ""))
    return {
        "profile_data": res,
        "final_response": res.get("analysis_text", ""),
        "citations": res.get("citations", []),
        "agent_used": "ProfileAgent"
    }

def retrieval_agent_node(state: EduPathState) -> Dict[str, Any]:
    agent = get_retrieval_agent()
    user_id = state.get("user_id", "default_user")
    res = agent.search_knowledge_base(query=state.get("user_input", ""), user_id=user_id)
    text = (
        f"### 🔎 Retrieval Agent Knowledge Discovery:\n\n"
        f"**Found {res.get('chunks_count', 0)} relevant chunks** matching your query:\n\n"
        f"{res.get('context_text', 'No documents found.')}"
    )
    return {
        "retrieval_data": res,
        "final_response": text,
        "citations": res.get("citations", []),
        "agent_used": "RetrievalAgent"
    }

def recommendation_agent_node(state: EduPathState) -> Dict[str, Any]:
    agent = get_recommendation_agent()
    user_id = state.get("user_id", "default_user")
    res = agent.generate_recommendations(user_id=user_id, custom_focus=state.get("user_input", ""))
    return {
        "recommendation_data": res,
        "final_response": res.get("justification", ""),
        "citations": res.get("citations", []),
        "agent_used": "RecommendationAgent"
    }

def pathway_planner_node(state: EduPathState) -> Dict[str, Any]:
    agent = get_pathway_planner_agent()
    user_id = state.get("user_id", "default_user")
    res = agent.generate_roadmap(user_id=user_id, role_title=state.get("user_input", ""))
    return {
        "roadmap_data": res,
        "final_response": res.get("overview_text", ""),
        "citations": res.get("citations", []),
        "agent_used": "PathwayPlannerAgent"
    }

def qa_agent_node(state: EduPathState) -> Dict[str, Any]:
    agent = get_qa_agent()
    user_id = state.get("user_id", "default_user")
    session_id = state.get("session_id", "default_session")
    res = agent.answer_question(query=state.get("user_input", ""), user_id=user_id, session_id=session_id)
    return {
        "qa_data": res,
        "final_response": res.get("answer", ""),
        "citations": res.get("citations", []),
        "agent_used": "QAAgent"
    }

def synthesizer_node(state: EduPathState) -> Dict[str, Any]:
    """Ensure formatting, metadata, and citation consistency on output."""
    final_resp = state.get("final_response", "")
    citations = state.get("citations", [])
    agent_used = state.get("agent_used", "EduPath Multi-Agent")
    return {
        "final_response": final_resp,
        "citations": citations,
        "agent_used": agent_used
    }

# -------------------------------------------------------------------------
# CONDITIONAL ROUTER
# -------------------------------------------------------------------------

def route_intent(state: EduPathState) -> Literal["profile", "retrieval", "recommendation", "roadmap", "qa"]:
    return state.get("intent", "qa")

# -------------------------------------------------------------------------
# GRAPH COMPILATION
# -------------------------------------------------------------------------

def build_edupath_graph():
    workflow = StateGraph(EduPathState)

    # Register Nodes
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("profile_agent", profile_agent_node)
    workflow.add_node("retrieval_agent", retrieval_agent_node)
    workflow.add_node("recommendation_agent", recommendation_agent_node)
    workflow.add_node("pathway_planner_agent", pathway_planner_node)
    workflow.add_node("qa_agent", qa_agent_node)
    workflow.add_node("synthesizer", synthesizer_node)

    # Set Entry Point
    workflow.set_entry_point("classify_intent")

    # Add Conditional Edges from Classifier
    workflow.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "profile": "profile_agent",
            "retrieval": "retrieval_agent",
            "recommendation": "recommendation_agent",
            "roadmap": "pathway_planner_agent",
            "qa": "qa_agent"
        }
    )

    # Edges from all agents to Synthesizer
    workflow.add_edge("profile_agent", "synthesizer")
    workflow.add_edge("retrieval_agent", "synthesizer")
    workflow.add_edge("recommendation_agent", "synthesizer")
    workflow.add_edge("pathway_planner_agent", "synthesizer")
    workflow.add_edge("qa_agent", "synthesizer")

    # Synthesizer completes execution
    workflow.add_edge("synthesizer", END)

    return workflow.compile()

# Singleton compiled app
edupath_graph_app = build_edupath_graph()

def run_agent_workflow(user_input: str, user_id: str = "default_user", session_id: str = "default_session") -> Dict[str, Any]:
    """Execute the multi-agent workflow on a given student input."""
    initial_state: EduPathState = {
        "user_id": user_id,
        "session_id": session_id,
        "user_input": user_input,
        "errors": []
    }
    final_state = edupath_graph_app.invoke(initial_state)
    return {
        "response": final_state.get("final_response", ""),
        "citations": final_state.get("citations", []),
        "agent_used": final_state.get("agent_used", "EduPath AI"),
        "intent": final_state.get("intent", "qa")
    }
