"""
EduPath AI - Q&A Agent (Agent 5)
Interactive mentor answering career and academic queries with grounded RAG citations.
"""

from typing import Dict, Any, List
from rag.retriever import get_retriever
from rag.citations import format_citations_markdown
from backend.services.llm_service import get_llm_service
from database.crud import save_conversation_message, get_conversation_history
from security.prompt_injection import (
    detect_direct_prompt_injection,
    wrap_untrusted_context
)

class QAAgent:
    def __init__(self):
        self.retriever = get_retriever()
        self.llm = get_llm_service()

    def answer_question(
        self,
        query: str,
        user_id: str,
        session_id: str = "default_session"
    ) -> Dict[str, Any]:
        """
        Grounded Question Answering pipeline with security checks and verifiable citations.
        """
        # 1. Direct prompt injection defense
        is_attack, attack_reason = detect_direct_prompt_injection(query)
        if is_attack:
            safe_refusal = (
                "⚠️ **Security Notice:** Your query could not be processed because it triggered "
                "our prompt injection and safety guardrails. Please ask a direct educational or career-related question."
            )
            save_conversation_message(
                user_id=user_id,
                session_id=session_id,
                role="user",
                content=query
            )
            save_conversation_message(
                user_id=user_id,
                session_id=session_id,
                role="assistant",
                content=safe_refusal,
                agent_name="QAAgent"
            )
            return {
                "agent": "QAAgent",
                "answer": safe_refusal,
                "citations": [],
                "is_grounded": False,
                "security_alert": True
            }

        # 2. Retrieve grounded context via RAG
        rag_res = self.retriever.retrieve(query=query, user_id=user_id, top_k=4)
        has_context = rag_res["has_context"]
        citations = rag_res["citations"]

        # 3. Fetch recent conversation history for conversational context
        history = get_conversation_history(user_id=user_id, session_id=session_id, limit=6)
        history_formatted = []
        for msg in history:
            history_formatted.append(f"{msg.role.upper()}: {msg.content}")
        history_str = "\n".join(history_formatted) if history_formatted else "None"

        # 4. Formulate LLM Prompt with Grounded Boundaries
        system_prompt = (
            "You are EduPath AI, an expert educational and career guidance mentor (SIH25094). "
            "Your answers must be clear, well-structured, empowering, and grounded in verified facts. "
            "If retrieved context is provided, ground your answer in it and cite facts accurately. "
            "If retrieved information is insufficient, honestly state what is known and advise on standard best practices. "
            "Never fabricate course titles, fake credentials, or false statistical numbers."
        )

        context_block = wrap_untrusted_context([c["text"] for c in rag_res.get("chunks", [])])

        user_prompt = f"""
Recent Conversation Context:
{history_str}

Reference Retrieved Knowledge:
{context_block}

Student Question:
{query}

Provide a comprehensive, well-organized response. If reference documents were retrieved, explain how they apply to the student's question.
"""
        generated_answer = self.llm.generate(user_prompt, system_instruction=system_prompt)

        # 5. Append citations markdown if retrieved context was used
        if citations:
            citations_md = format_citations_markdown(citations)
            full_response = f"{generated_answer}{citations_md}"
        else:
            full_response = generated_answer

        # 6. Save message history to DB
        save_conversation_message(
            user_id=user_id,
            session_id=session_id,
            role="user",
            content=query
        )
        save_conversation_message(
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            content=full_response,
            agent_name="QAAgent",
            citations=citations
        )

        return {
            "agent": "QAAgent",
            "answer": full_response,
            "citations": citations,
            "is_grounded": has_context,
            "security_alert": False
        }

_qa_agent_instance = None

def get_qa_agent() -> QAAgent:
    global _qa_agent_instance
    if _qa_agent_instance is None:
        _qa_agent_instance = QAAgent()
    return _qa_agent_instance
