"""
EduPath AI - Q&A and Multi-Agent Chat API
Direct and Multi-Agent query execution with conversation history.
"""

from fastapi import APIRouter, Depends
from security.authorization import get_current_user
from database.models import UserRecord
from database.crud import get_conversation_history
from graph.workflow import run_agent_workflow
from backend.schemas import ChatQueryRequest, ChatQueryResponse

router = APIRouter(prefix="/chat", tags=["AI Career Assistant"])

@router.post("", response_model=ChatQueryResponse)
def ask_question(
    req: ChatQueryRequest,
    current_user: UserRecord = Depends(get_current_user)
):
    """
    Execute full LangGraph multi-agent workflow on the user's message.
    Routes intelligently to QAAgent, RecommendationAgent, ProfileAgent, etc.
    """
    workflow_output = run_agent_workflow(
        user_input=req.query,
        user_id=current_user.id,
        session_id=req.session_id
    )

    return ChatQueryResponse(
        answer=workflow_output.get("response", ""),
        citations=workflow_output.get("citations", []),
        agent_used=workflow_output.get("agent_used", "EduPath AI"),
        is_grounded=len(workflow_output.get("citations", [])) > 0,
        security_alert=False
    )

@router.get("/history")
def get_chat_history(
    session_id: str = "default_session",
    current_user: UserRecord = Depends(get_current_user)
):
    history = get_conversation_history(user_id=current_user.id, session_id=session_id)
    return [m.model_dump() for m in history]
