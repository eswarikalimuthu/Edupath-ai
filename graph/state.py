"""
EduPath AI - LangGraph Shared State Definition
Defines the multi-agent state schema flowing across all nodes in the workflow.
"""

from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict

class EduPathState(TypedDict, total=False):
    # Core identifiers
    user_id: str
    session_id: str
    user_input: str
    intent: str  # "profile", "retrieval", "recommendation", "roadmap", "qa"
    
    # Context & Data shared between agents
    profile_data: Optional[Dict[str, Any]]
    retrieval_data: Optional[Dict[str, Any]]
    recommendation_data: Optional[Dict[str, Any]]
    roadmap_data: Optional[Dict[str, Any]]
    qa_data: Optional[Dict[str, Any]]
    
    # Final unified output
    final_response: str
    citations: List[Dict[str, Any]]
    agent_used: str
    errors: List[str]
