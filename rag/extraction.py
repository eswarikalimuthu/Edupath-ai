"""
EduPath AI - Document Extraction Module
Extracts text and page-level metadata from PDF, TXT, and Markdown files.
"""

from pathlib import Path
from typing import List, Dict, Any
import pypdf

class DocumentExtractionError(Exception):
    pass

def extract_text_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract text from PDF page by page.
    Returns a list of dicts: [{"page_number": int, "text": str}]
    """
    path = Path(file_path)
    if not path.exists():
        raise DocumentExtractionError(f"File not found: {file_path}")
        
    pages = []
    try:
        reader = pypdf.PdfReader(str(path))
        for idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append({
                    "page_number": idx,
                    "text": text
                })
    except Exception as e:
        raise DocumentExtractionError(f"Failed to extract text from PDF: {str(e)}")
        
    if not pages:
        # Fallback for empty or scanned PDF
        pages.append({"page_number": 1, "text": ""})
        
    return pages

def extract_text_from_text_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract text from plain text or Markdown file.
    """
    path = Path(file_path)
    if not path.exists():
        raise DocumentExtractionError(f"File not found: {file_path}")
        
    try:
        with open(str(path), "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        return [{"page_number": 1, "text": content}]
    except Exception as e:
        raise DocumentExtractionError(f"Failed to read text file: {str(e)}")

def extract_document(file_path: str) -> List[Dict[str, Any]]:
    """
    Universal extractor routing based on file extension.
    """
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    elif suffix in (".txt", ".md", ".json", ".csv"):
        return extract_text_from_text_file(file_path)
    else:
        raise DocumentExtractionError(f"Unsupported file format: {suffix}")
