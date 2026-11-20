"""
EduPath AI - FastAPI Application Entry Point
High-performance backend for educational and career guidance (SIH25094).
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from backend.config import settings
from backend.api import api_router
from backend.middleware.security_headers import SecurityHeadersMiddleware
from backend.middleware.rate_limit import RateLimiterMiddleware
from backend.middleware.error_handler import (
    validation_exception_handler,
    generic_exception_handler
)
from database.connection import init_db
from rag.vector_store import get_vector_store
from rag.ingestion import ingest_document

def seed_baseline_knowledge():
    """Seed baseline verified career and educational benchmarks if vector store is empty."""
    vector_store = get_vector_store()
    if vector_store.count() == 0:
        sample_doc = (
            b"# EduPath AI - Verified National Career & Educational Standards (SIH25094)\n\n"
            b"## 1. Artificial Intelligence & Machine Learning Engineering\n"
            b"Foundational requirements include advanced Python programming, linear algebra, multivariable calculus, "
            b"and probability theory. Core frameworks include PyTorch, TensorFlow, Scikit-Learn, and ONNX. "
            b"Applied competencies require hands-on experience in Retrieval-Augmented Generation (RAG), vector databases "
            b"(ChromaDB, Milvus), reciprocal rank fusion, and LangGraph multi-agent orchestration.\n\n"
            b"## 2. Cloud-Native Backend & Microservices Engineering\n"
            b"Key proficiencies include FastAPI, Go, Docker containerization, Kubernetes orchestration, and "
            b"relational database optimization (PostgreSQL, SQLite WAL mode). Candidates must understand API security, "
            b"JWT token lifecycles, OWASP Top 10 vulnerabilities, and rate limiting.\n\n"
            b"## 3. Data Science & Big Data Engineering\n"
            b"Essential capabilities encompass exploratory data analysis, Pandas, Apache Spark, SQL query optimization, "
            b"data warehousing, feature engineering, and statistical hypothesis testing.\n\n"
            b"## 4. Full-Stack Web Development\n"
            b"Requirements include modern JavaScript/TypeScript, React/Next.js or Streamlit for rapid AI prototyping, "
            b"state management, responsive design, and secure RESTful endpoint consumption.\n"
        )
        try:
            ingest_document(
                file_bytes=sample_doc,
                filename="official_career_standards_sih.md",
                is_global=True,
                description="Official National Career & Educational Frameworks Baseline"
            )
        except Exception:
            pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize SQLite schema & seed baseline knowledge
    init_db()
    seed_baseline_knowledge()
    yield
    # Shutdown

app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent AI-Powered Educational & Career Guidance Platform (SIH25094)",
    version="2.0.0"
)

# 1. Custom Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 2. Sliding Window Rate Limiting Middleware
app.add_middleware(RateLimiterMiddleware, max_requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE)

# 3. Explicit CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 4. Centralized Exception Handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# 5. Include API Routers
app.include_router(api_router)

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.BACKEND_PORT, reload=settings.DEBUG)
