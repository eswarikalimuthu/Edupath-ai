"""
EduPath AI - Database Connection & Initialization
SQLite connection management with WAL mode, foreign keys, and safe migrations.
"""

import sqlite3
from contextlib import contextmanager
from typing import Generator
from pathlib import Path
from backend.config import settings

def get_db_path() -> str:
    path = Path(settings.DATABASE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)

def create_connection() -> sqlite3.Connection:
    """Create a configured SQLite database connection."""
    conn = sqlite3.connect(get_db_path(), timeout=30.0)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for concurrency and foreign key constraints
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    return conn

@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for acquiring and closing database connections safely."""
    conn = create_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db() -> None:
    """Initialize database tables and indexes if they do not exist."""
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS student_profiles (
            id TEXT PRIMARY KEY,
            user_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            education_level TEXT NOT NULL,
            field_of_study TEXT NOT NULL,
            institution TEXT,
            graduation_year INTEGER,
            gpa REAL,
            bio TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS skills (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            skill_name TEXT NOT NULL,
            category TEXT NOT NULL, -- technical, soft, domain
            proficiency TEXT NOT NULL, -- beginner, intermediate, advanced, expert
            verified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS interests (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            interest_name TEXT NOT NULL,
            category TEXT,
            priority INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS career_goals (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            target_role TEXT NOT NULL,
            target_industry TEXT,
            timeline_months INTEGER DEFAULT 12,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS career_recommendations (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            role_title TEXT NOT NULL,
            match_percentage REAL NOT NULL,
            justification TEXT NOT NULL,
            key_skills_required TEXT, -- JSON array
            recommended_courses TEXT, -- JSON array
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS skill_gaps (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            recommendation_id TEXT,
            missing_skill TEXT NOT NULL,
            category TEXT,
            importance TEXT NOT NULL, -- critical, moderate, optional
            recommendation_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (recommendation_id) REFERENCES career_recommendations (id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS roadmaps (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            role_title TEXT NOT NULL,
            description TEXT,
            stages_json TEXT NOT NULL, -- full stage hierarchy JSON
            status TEXT NOT NULL DEFAULT 'active', -- active, completed, archived
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS milestones (
            id TEXT PRIMARY KEY,
            roadmap_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            stage TEXT NOT NULL, -- beginner, intermediate, advanced
            description TEXT,
            order_index INTEGER NOT NULL DEFAULT 0,
            project_prompt TEXT,
            resources_json TEXT, -- JSON array of course links/books/docs
            is_completed INTEGER NOT NULL DEFAULT 0,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (roadmap_id) REFERENCES roadmaps (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS conversation_messages (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL, -- user, assistant, system
            content TEXT NOT NULL,
            agent_name TEXT,
            citations_json TEXT, -- JSON array of citation objects
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS document_metadata (
            id TEXT PRIMARY KEY,
            user_id TEXT, -- NULL means global system document
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            file_hash TEXT UNIQUE NOT NULL,
            mime_type TEXT NOT NULL,
            chunk_count INTEGER NOT NULL DEFAULT 0,
            is_global INTEGER NOT NULL DEFAULT 0,
            description TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        );

        -- Performance Indexes
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_profiles_user ON student_profiles(user_id);
        CREATE INDEX IF NOT EXISTS idx_skills_user ON skills(user_id);
        CREATE INDEX IF NOT EXISTS idx_interests_user ON interests(user_id);
        CREATE INDEX IF NOT EXISTS idx_recommendations_user ON career_recommendations(user_id);
        CREATE INDEX IF NOT EXISTS idx_gaps_user ON skill_gaps(user_id);
        CREATE INDEX IF NOT EXISTS idx_roadmaps_user ON roadmaps(user_id);
        CREATE INDEX IF NOT EXISTS idx_milestones_roadmap ON milestones(roadmap_id);
        CREATE INDEX IF NOT EXISTS idx_milestones_user ON milestones(user_id);
        CREATE INDEX IF NOT EXISTS idx_conv_user_session ON conversation_messages(user_id, session_id);
        CREATE INDEX IF NOT EXISTS idx_docs_user ON document_metadata(user_id);
        CREATE INDEX IF NOT EXISTS idx_docs_hash ON document_metadata(file_hash);
        """)
