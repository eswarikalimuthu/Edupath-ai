"""
EduPath AI - Complete Document Ingestion Pipeline
Validates, extracts, cleans, chunks, embeds, and indexes educational documents.
"""

import hashlib
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

from backend.config import settings
from database.crud import register_document, get_document_by_hash
from rag.extraction import extract_document
from rag.cleaning import clean_text
from rag.chunking import chunk_document_pages
from rag.vector_store import get_vector_store
from rag.bm25_search import get_bm25_engine
from security.validation import validate_file_upload, validate_safe_filename

class IngestionError(Exception):
    pass

def ingest_document(
    file_bytes: bytes,
    filename: str,
    user_id: Optional[str] = None,
    is_global: bool = False,
    description: Optional[str] = None,
    doc_type: str = "educational"
) -> Dict[str, Any]:
    """
    Complete end-to-end document ingestion pipeline:
    File Validation -> Hash Check -> Storage -> Text Extraction -> Cleaning ->
    Chunking -> Embedding -> ChromaDB Indexing -> BM25 Indexing -> Database Registration.
    """
    # 1. File Validation
    is_valid, err_msg = validate_file_upload(filename, file_bytes)
    if not is_valid:
        raise IngestionError(f"File validation failed: {err_msg}")

    safe_name = validate_safe_filename(filename)

    # 2. Hash & Duplicate Detection
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    existing_doc = get_document_by_hash(sha256)
    if existing_doc:
        return {
            "status": "already_exists",
            "document_id": existing_doc.id,
            "filename": existing_doc.filename,
            "chunk_count": existing_doc.chunk_count,
            "message": "Document with identical content already ingested."
        }

    # 3. Store file securely
    upload_dir = Path(settings.UPLOAD_STORAGE_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    stored_path = upload_dir / f"{sha256[:12]}_{safe_name}"
    
    with open(stored_path, "wb") as f:
        f.write(file_bytes)

    # 4. Text Extraction
    try:
        pages_data = extract_document(str(stored_path))
    except Exception as e:
        if stored_path.exists():
            stored_path.unlink()
        raise IngestionError(f"Failed to extract document contents: {str(e)}")

    # 5. Cleaning
    for page in pages_data:
        page["text"] = clean_text(page.get("text", ""))

    # 6. Chunking
    doc_id = f"doc_{sha256[:10]}"
    chunks = chunk_document_pages(
        pages=pages_data,
        doc_id=doc_id,
        source_name=safe_name,
        user_id=user_id,
        is_global=is_global,
        doc_type=doc_type
    )

    if not chunks:
        if stored_path.exists():
            stored_path.unlink()
        raise IngestionError("Document contained no readable text after extraction and cleaning.")

    # 7. Embedding & ChromaDB Indexing
    vector_store = get_vector_store()
    vector_store.add_chunks(chunks)

    # 8. Rebuild / Synchronize BM25 Engine
    bm25_engine = get_bm25_engine()
    all_chunks = vector_store.get_all_chunks()
    bm25_engine.build_index(all_chunks)

    # 9. Register in SQLite Database
    doc_record = register_document(
        filename=safe_name,
        file_path=str(stored_path),
        file_size=len(file_bytes),
        file_hash=sha256,
        mime_type=Path(safe_name).suffix.lstrip("."),
        chunk_count=len(chunks),
        user_id=user_id,
        is_global=is_global,
        description=description
    )

    return {
        "status": "success",
        "document_id": doc_record.id,
        "filename": doc_record.filename,
        "chunk_count": len(chunks),
        "file_hash": sha256,
        "message": f"Successfully ingested and indexed {len(chunks)} chunks."
    }
