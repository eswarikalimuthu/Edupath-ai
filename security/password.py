"""
EduPath AI - Password Security Module
Implements salted bcrypt password hashing and verification.
"""

import bcrypt

def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt and auto-generated salt."""
    if not password:
        raise ValueError("Password cannot be empty")
    # Truncate to 72 bytes if necessary to prevent bcrypt overflow attack
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    if not plain_password or not hashed_password:
        return False
    try:
        plain_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(plain_bytes, hash_bytes)
    except Exception:
        return False
