"""
EduPath AI - API Package
"""

from fastapi import APIRouter
from backend.api.auth import router as auth_router
from backend.api.profile import router as profile_router
from backend.api.recommendations import router as recommendations_router
from backend.api.roadmaps import router as roadmaps_router
from backend.api.qa import router as qa_router
from backend.api.documents import router as documents_router
from backend.api.progress import router as progress_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(recommendations_router)
api_router.include_router(roadmaps_router)
api_router.include_router(qa_router)
api_router.include_router(documents_router)
api_router.include_router(progress_router)

__all__ = ["api_router"]
