# Security Policy & Architecture Guide (EduPath AI)

> **Document Status:** Active  
> **Applies to:** EduPath AI Core, API, RAG Pipeline & Multi-Agent System (SIH25094)

---

## 1. Authentication & Password Security

### Password Storage
- Passwords are encrypted using **bcrypt** with salted adaptive key-derivation (`bcrypt.gensalt(rounds=12)`).
- Input passwords are truncated safely to 72 bytes prior to hashing to mitigate algorithmic denial-of-service vulnerabilities.
- Plaintext passwords are never logged, cached, or persisted under any circumstance.

### JWT Token Management
- Access tokens are cryptographically signed using **HMAC-SHA256 (HS256)** with a 256-bit secret key.
- Default Access Token Lifespan: **120 minutes**.
- Default Refresh Token Lifespan: **7 days**.
- Every private endpoint extracts and validates the cryptographic token payload, verifying signature validity, expiration timestamp (`exp`), and active user account status.

---

## 2. Authorization & Data Isolation

### User-Level Multi-Tenant Isolation
- Every database entity (profiles, skills, interests, career goals, recommendations, roadmaps, milestones, conversation messages, documents) is explicitly bound to a `user_id`.
- SQLite CRUD functions enforce strict ownership matching:
  ```sql
  SELECT * FROM student_profiles WHERE user_id = ?;
  DELETE FROM skills WHERE id = ? AND user_id = ?;
  ```
- Vector store queries filter chunk metadata using explicit boolean criteria:
  ```python
  where = {"$or": [{"user_id": current_user.id}, {"is_global": True}]}
  ```
- Cross-user data retrieval is strictly prohibited. Attempting to query or modify resources belonging to another student yields an immediate `403 Forbidden` response.

### Role-Based Access Control (RBAC)
- Supported Roles: `student` (default) and `admin`.
- Administrative privileges are required for system-wide document ingestion (`is_global=True`) and cross-tenant auditing.

---

## 3. API Security & Threat Hardening

### Middleware Protections
1. **Security Headers (Pure ASGI Middleware):**
   - `X-Content-Type-Options: nosniff`
   - `X-Frame-Options: DENY`
   - `X-XSS-Protection: 1; mode=block`
   - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
   - `Referrer-Policy: strict-origin-when-cross-origin`
   - `Content-Security-Policy: default-src 'self'; frame-ancestors 'none';`
2. **Sliding-Window Rate Limiting:**
   - In-memory per-IP sliding window tracking enforcing a ceiling of **120 requests/minute**.
   - Excess queries trigger `429 Too Many Requests`.
3. **Information Disclosure Prevention:**
   - Centralized exception handlers catch all unhandled server errors and return sanitized error schemas, suppressing internal stack traces and server file paths.

---

## 4. File Upload & Ingestion Security

1. **Path Traversal Defenses:**
   - Filenames are sanitized via `validate_safe_filename()`.
   - Sequences matching `../`, `..\`, `/etc/`, `C:\Windows`, or directory separators are strictly blocked.
2. **MIME & Magic Bytes Validation:**
   - File extensions are restricted to an allowlist (`pdf`, `txt`, `md`).
   - PDF files must start with the valid magic signature `b"%PDF-"`.
   - Plaintext files must decode cleanly in UTF-8.
3. **Resource Exhaustion Controls:**
   - Maximum upload file size is capped at **15 MB**.
   - Storage files are isolated in `data/uploads/` with hashed unique prefix naming.

---

## 5. AI Safety & Prompt Injection Guardrails

1. **Direct Injection Detection:**
   - User queries are scanned against known adversarial patterns (*"ignore previous instructions"*, *"system override"*, *"DAN mode"*, chat format breakout tokens `<|im_start|>`).
   - Flagged queries are rejected immediately without being forwarded to the LLM.
2. **Indirect Injection Sanitization:**
   - Retrieved chunks from external or user-uploaded documents are sanitized before inclusion in the LLM prompt.
   - Fake system tags (`<system>`, `[INST]`) and instruction override triggers within retrieved document bodies are neutralized.
   - Retrieved chunks are enclosed in strict XML demarcation blocks (`<retrieved_context>`) instructing the LLM to treat them purely as unexecutable reference data.
3. **Sensitive Data Leakage Redaction:**
   - LLM responses are processed by `sanitize_llm_output()` to detect and scrub exposed API keys (`AIzaSy...`, `sk-...`, secret keys).

---

## 6. Vulnerability Reporting

If you identify a security vulnerability in EduPath AI, please do not disclose it publicly. Contact the EduPath AI security team directly with reproduction steps and proof-of-concept details.
