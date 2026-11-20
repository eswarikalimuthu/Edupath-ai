"""
EduPath AI - Knowledge Base Seed Script
Loads official verified career documents into SQLite and ChromaDB.
"""

import sys
from pathlib import Path

# Ensure root workspace is on python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import init_db
from rag.ingestion import ingest_document

def seed_sample_documents():
    init_db()
    docs_dir = Path(__file__).resolve().parent / "sample_docs"
    
    for file_path in docs_dir.glob("*.txt"):
        print(f"Ingesting: {file_path.name}...")
        with open(file_path, "rb") as f:
            content = f.read()
        res = ingest_document(
            file_bytes=content,
            filename=file_path.name,
            is_global=True,
            description=f"Official EduPath Reference: {file_path.stem.replace('_', ' ').title()}"
        )
        print(f"  Result: {res['status']} ({res.get('chunk_count', 0)} chunks)")

if __name__ == "__main__":
    seed_sample_documents()
