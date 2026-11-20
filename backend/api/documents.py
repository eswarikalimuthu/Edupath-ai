"""
EduPath AI - Document Management API
Secure upload, indexing, listing, and deletion of educational documents.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from typing import Optional, List
from pathlib import Path
from security.authorization import get_current_user
from database.models import UserRecord
from database.crud import (
    get_documents_accessible_by_user,
    delete_document_record
)
from rag.ingestion import ingest_document, IngestionError
from rag.vector_store import get_vector_store

router = APIRouter(prefix="/documents", tags=["Document Management"])

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    is_global: bool = Form(False),
    current_user: UserRecord = Depends(get_current_user)
):
    # Only admins can upload global documents
    global_flag = is_global and (current_user.role == "admin")

    file_bytes = await file.read()
    filename = file.filename or "uploaded_document.txt"

    try:
        result = ingest_document(
            file_bytes=file_bytes,
            filename=filename,
            user_id=current_user.id,
            is_global=global_flag,
            description=description
        )
        return result
    except IngestionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("")
def list_documents(current_user: UserRecord = Depends(get_current_user)):
    docs = get_documents_accessible_by_user(current_user.id)
    return [d.model_dump() for d in docs]

@router.delete("/{document_id}")
def delete_document(document_id: str, current_user: UserRecord = Depends(get_current_user)):
    docs = get_documents_accessible_by_user(current_user.id)
    target = next((d for d in docs if d.id == document_id), None)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if target.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to delete this document")

    # Delete physical file
    if target.file_path and Path(target.file_path).exists():
        try:
            Path(target.file_path).unlink()
        except Exception:
            pass

    # Delete vector chunks from ChromaDB
    doc_id_prefix = f"doc_{target.file_hash[:10]}"
    vector_store = get_vector_store()
    vector_store.delete_document_chunks(doc_id_prefix)

    # Delete SQLite record
    delete_document_record(current_user.id, document_id)

    return {"status": "success", "message": "Document and associated vectors deleted successfully."}
