"""
EduPath AI - RAG Evaluation Benchmark Dataset
Standard ground-truth dataset for evaluating educational and career guidance retrieval.
"""

BENCHMARK_QUERIES = [
    {
        "query": "What are the core mathematical foundations and programming languages needed for Machine Learning Engineers?",
        "expected_sources": ["ai_ml_career_framework.txt", "official_career_standards_sih.md"],
        "keywords": ["python", "linear algebra", "calculus", "pytorch", "probability"]
    },
    {
        "query": "What are the key technical competencies for Full-Stack Cloud and Backend Engineers?",
        "expected_sources": ["fullstack_cloud_guide.txt", "official_career_standards_sih.md"],
        "keywords": ["fastapi", "docker", "kubernetes", "sqlite", "postgresql", "rest"]
    },
    {
        "query": "Which certifications are recommended for Cybersecurity Specialists and ethical hacking?",
        "expected_sources": ["cybersecurity_pathway.txt"],
        "keywords": ["security+", "cissp", "ceh", "oscp", "cryptography"]
    },
    {
        "query": "What is the role of vector databases and LangGraph multi-agent systems in AI engineering?",
        "expected_sources": ["ai_ml_career_framework.txt", "official_career_standards_sih.md"],
        "keywords": ["chromadb", "langgraph", "multi-agent", "rag", "retrieval"]
    },
    {
        "query": "What are the staged milestones for learning web security, OWASP defenses, and password hashing?",
        "expected_sources": ["fullstack_cloud_guide.txt", "cybersecurity_pathway.txt"],
        "keywords": ["bcrypt", "jwt", "owasp", "rate limiting", "token"]
    },
    {
        "query": "What certifications should a machine learning student take to prove industry readiness?",
        "expected_sources": ["ai_ml_career_framework.txt"],
        "keywords": ["deeplearning.ai", "google cloud professional", "aws certified"]
    },
    {
        "query": "How is penetration testing and vulnerability assessment structured across milestones?",
        "expected_sources": ["cybersecurity_pathway.txt"],
        "keywords": ["penetration testing", "linux", "vulnerability", "threat modeling"]
    },
    {
        "query": "What tools and frameworks are required for containerization and microservices architecture?",
        "expected_sources": ["fullstack_cloud_guide.txt", "official_career_standards_sih.md"],
        "keywords": ["docker", "kubernetes", "fastapi", "microservices"]
    }
]
