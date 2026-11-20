"""
EduPath AI - Input Validation & Security Sanitization
Protects against path traversal, XSS, malicious uploads, and malformed inputs.
"""

import re
import os
from pathlib import Path
from typing import Tuple
from backend.config import settings

# Disallowed path traversal patterns
PATH_TRAVERSAL_PATTERN = re.compile(r"(\.\./|\.\.\\|/etc/|/var/|C:\\Windows|System32)", re.IGNORECASE)

# Safe filename regex: letters, numbers, hyphens, underscores, dots
SAFE_FILENAME_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]+$")

ALLOWED_EXTENSIONS = {ext.strip().lower() for ext in settings.ALLOWED_EXTENSIONS.split(",")}

# Approved magic bytes / file signatures
ALLOWED_MAGIC_BYTES = {
    "pdf": [b"%PDF-"],
    "txt": [],  # Validated as UTF-8 / ASCII text
    "md": [],   # Validated as UTF-8 / ASCII text
}

def sanitize_string(text: str, max_length: int = 10000) -> str:
    """Sanitize arbitrary user input string, stripping control characters and excessive length."""
    if not text:
        return ""
    # Strip null bytes and non-printable control characters (except newline, carriage return, tab)
    cleaned = "".join(ch for ch in text if ch in ("\n", "\r", "\t") or (ch >= " " and ord(ch) < 65534))
    return cleaned.strip()[:max_length]

def validate_safe_filename(filename: str) -> str:
    """Ensure a filename does not contain path traversal characters and is safe for storage."""
    if not filename:
        raise ValueError("Invalid filename")
        
    # Check for path traversal sequences or directory separators
    if PATH_TRAVERSAL_PATTERN.search(filename) or "/" in filename or "\\" in filename:
        raise ValueError("Path traversal sequence detected in filename")
        
    base_name = os.path.basename(filename).strip()
    if not base_name or base_name in (".", ".."):
        raise ValueError("Invalid filename")
        
    # Replace any unsafe characters with an underscore
    safe_name = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", base_name)
    if not safe_name:
        raise ValueError("Filename is empty after sanitization")
        
    return safe_name

def validate_file_upload(filename: str, content: bytes) -> Tuple[bool, str]:
    """
    Validate file extension, size, and content signature.
    Returns (is_valid, error_message).
    """
    # 1. Size check
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        return False, f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB"
        
    if len(content) == 0:
        return False, "Uploaded file is empty"
        
    # 2. Extension check
    suffix = Path(filename).suffix.lstrip(".").lower()
    if suffix not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file extension '{suffix}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        
    # 3. Magic bytes / Content check
    if suffix == "pdf":
        if not content.startswith(b"%PDF-"):
            return False, "File is not a valid PDF document (magic bytes mismatch)"
    elif suffix in ("txt", "md"):
        try:
            content[:2048].decode("utf-8")
        except UnicodeDecodeError:
            return False, f"File is not valid text formatted in UTF-8"
            
    return True, ""
