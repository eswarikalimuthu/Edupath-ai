"""
EduPath AI - Security Package
"""

from security.password import hash_password, verify_password
from security.authentication import (
    create_access_token, create_refresh_token, decode_token, AuthenticationError
)
from security.authorization import (
    get_current_user, get_optional_current_user, require_role, verify_ownership
)
from security.validation import (
    sanitize_string, validate_safe_filename, validate_file_upload
)
from security.prompt_injection import (
    detect_direct_prompt_injection, sanitize_retrieved_context,
    wrap_untrusted_context, sanitize_llm_output
)

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "AuthenticationError",
    "get_current_user",
    "get_optional_current_user",
    "require_role",
    "verify_ownership",
    "sanitize_string",
    "validate_safe_filename",
    "validate_file_upload",
    "detect_direct_prompt_injection",
    "sanitize_retrieved_context",
    "wrap_untrusted_context",
    "sanitize_llm_output",
]
