"""
EduPath AI - Frontend API Client
Handles authenticated communication between Streamlit and FastAPI backend.
"""

import httpx
from typing import Dict, Any, Optional, List
import streamlit as st

BACKEND_BASE_URL = "http://127.0.0.1:8000/api/v1"

class EduPathAPIClient:
    def __init__(self, base_url: str = BACKEND_BASE_URL):
        self.base_url = base_url

    def _get_headers(self) -> Dict[str, str]:
        token = st.session_state.get("access_token")
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    # ---------------- AUTH ----------------
    def login(self, username: str, password: str) -> Dict[str, Any]:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password}
            )
            return {"status_code": res.status_code, "data": res.json()}

    def register(self, email: str, username: str, password: str) -> Dict[str, Any]:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(
                f"{self.base_url}/auth/register",
                json={"email": email, "username": username, "password": password, "role": "student"}
            )
            return {"status_code": res.status_code, "data": res.json()}

    def get_me(self) -> Dict[str, Any]:
        with httpx.Client(timeout=10.0) as client:
            res = client.get(f"{self.base_url}/auth/me", headers=self._get_headers())
            return {"status_code": res.status_code, "data": res.json() if res.status_code == 200 else {}}

    # ---------------- PROFILE ----------------
    def get_profile(self) -> Dict[str, Any]:
        with httpx.Client(timeout=10.0) as client:
            res = client.get(f"{self.base_url}/profile", headers=self._get_headers())
            return res.json() if res.status_code == 200 else {}

    def update_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        with httpx.Client(timeout=10.0) as client:
            res = client.put(f"{self.base_url}/profile", json=data, headers=self._get_headers())
            return res.json()

    def add_skill(self, skill_name: str, category: str, proficiency: str) -> Dict[str, Any]:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(
                f"{self.base_url}/profile/skills",
                json={"skill_name": skill_name, "category": category, "proficiency": proficiency},
                headers=self._get_headers()
            )
            return res.json()

    def delete_skill(self, skill_id: str) -> bool:
        with httpx.Client(timeout=10.0) as client:
            res = client.delete(f"{self.base_url}/profile/skills/{skill_id}", headers=self._get_headers())
            return res.status_code == 200

    def add_interest(self, interest_name: str, category: Optional[str] = None, priority: int = 1) -> Dict[str, Any]:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(
                f"{self.base_url}/profile/interests",
                json={"interest_name": interest_name, "category": category, "priority": priority},
                headers=self._get_headers()
            )
            return res.json()

    def delete_interest(self, interest_id: str) -> bool:
        with httpx.Client(timeout=10.0) as client:
            res = client.delete(f"{self.base_url}/profile/interests/{interest_id}", headers=self._get_headers())
            return res.status_code == 200

    def set_goal(self, target_role: str, target_industry: Optional[str] = None, timeline_months: int = 12) -> Dict[str, Any]:
        with httpx.Client(timeout=10.0) as client:
            res = client.post(
                f"{self.base_url}/profile/goal",
                json={"target_role": target_role, "target_industry": target_industry, "timeline_months": timeline_months},
                headers=self._get_headers()
            )
            return res.json()

    # ---------------- RECOMMENDATIONS ----------------
    def generate_recommendations(self, target_role: Optional[str] = None) -> Dict[str, Any]:
        with httpx.Client(timeout=25.0) as client:
            res = client.post(
                f"{self.base_url}/recommendations/generate",
                json={"target_role": target_role},
                headers=self._get_headers()
            )
            return res.json() if res.status_code == 200 else {}

    def get_recommendations(self) -> List[Dict[str, Any]]:
        with httpx.Client(timeout=10.0) as client:
            res = client.get(f"{self.base_url}/recommendations", headers=self._get_headers())
            return res.json() if res.status_code == 200 else []

    def get_skill_gaps(self, recommendation_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with httpx.Client(timeout=10.0) as client:
            params = {"recommendation_id": recommendation_id} if recommendation_id else {}
            res = client.get(f"{self.base_url}/recommendations/gaps", params=params, headers=self._get_headers())
            return res.json() if res.status_code == 200 else []

    # ---------------- ROADMAPS ----------------
    def generate_roadmap(self, role_title: Optional[str] = None) -> Dict[str, Any]:
        with httpx.Client(timeout=25.0) as client:
            res = client.post(
                f"{self.base_url}/roadmaps/generate",
                json={"role_title": role_title},
                headers=self._get_headers()
            )
            return res.json() if res.status_code == 200 else {}

    def get_roadmaps(self) -> List[Dict[str, Any]]:
        with httpx.Client(timeout=10.0) as client:
            res = client.get(f"{self.base_url}/roadmaps", headers=self._get_headers())
            return res.json() if res.status_code == 200 else []

    def update_milestone(self, milestone_id: str, is_completed: bool) -> Dict[str, Any]:
        with httpx.Client(timeout=10.0) as client:
            res = client.put(
                f"{self.base_url}/roadmaps/milestones/{milestone_id}",
                json={"is_completed": is_completed},
                headers=self._get_headers()
            )
            return res.json() if res.status_code == 200 else {}

    # ---------------- CHAT ----------------
    def send_chat_message(self, query: str, session_id: str = "default_session") -> Dict[str, Any]:
        with httpx.Client(timeout=30.0) as client:
            res = client.post(
                f"{self.base_url}/chat",
                json={"query": query, "session_id": session_id},
                headers=self._get_headers()
            )
            return res.json() if res.status_code == 200 else {"answer": "Error connecting to AI Assistant.", "citations": []}

    def get_chat_history(self, session_id: str = "default_session") -> List[Dict[str, Any]]:
        with httpx.Client(timeout=10.0) as client:
            res = client.get(f"{self.base_url}/chat/history?session_id={session_id}", headers=self._get_headers())
            return res.json() if res.status_code == 200 else []

    # ---------------- DOCUMENTS ----------------
    def upload_document(self, file_bytes: bytes, filename: str, description: Optional[str] = None) -> Dict[str, Any]:
        with httpx.Client(timeout=20.0) as client:
            files = {"file": (filename, file_bytes, "application/octet-stream")}
            data = {"description": description or "", "is_global": "false"}
            res = client.post(
                f"{self.base_url}/documents/upload",
                files=files,
                data=data,
                headers=self._get_headers()
            )
            return {"status_code": res.status_code, "data": res.json()}

    def get_documents(self) -> List[Dict[str, Any]]:
        with httpx.Client(timeout=10.0) as client:
            res = client.get(f"{self.base_url}/documents", headers=self._get_headers())
            return res.json() if res.status_code == 200 else []

    def delete_document(self, doc_id: str) -> bool:
        with httpx.Client(timeout=10.0) as client:
            res = client.delete(f"{self.base_url}/documents/{doc_id}", headers=self._get_headers())
            return res.status_code == 200

    # ---------------- PROGRESS ----------------
    def get_progress_summary(self) -> Dict[str, Any]:
        with httpx.Client(timeout=10.0) as client:
            res = client.get(f"{self.base_url}/progress/summary", headers=self._get_headers())
            return res.json() if res.status_code == 200 else {}

api_client = EduPathAPIClient()
