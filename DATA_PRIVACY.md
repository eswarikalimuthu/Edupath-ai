# EduPath AI - Student Data Privacy & Governance Policy

> **Commitment:** Privacy-by-Design, Minimal Data Collection, and Zero Data Monetization (SIH25094)

---

## 1. Privacy Principles

EduPath AI adheres to strict educational data privacy standards:
1. **Data Minimization:** We collect only the information strictly necessary to formulate personalized career recommendations and staged learning roadmaps.
2. **User Ownership:** Students retain full ownership and intellectual property rights over their profiles, uploaded documents, and learning milestones.
3. **Local-First Processing:** Core relational data and vector indexes reside on local persistent infrastructure (`edupath.db` and local ChromaDB), preventing unnecessary cloud exfiltration.

---

## 2. Categories of Collected Data

| Data Category | Specific Data Elements | Purpose & Usage |
| :--- | :--- | :--- |
| **Account Credentials** | Email, username, salted bcrypt password hash. | Identity verification and session management. |
| **Academic Qualifications** | Full name, degree level, major, institution, graduation year, GPA. | Formulate baseline career readiness and eligibility. |
| **Skills & Competencies** | Technical stack, soft skills, domain proficiencies. | Compute skill gap analysis and compatibility scores. |
| **Learning Progress** | Completed milestones, timestamps, project submissions. | Roadmap progress tracking and adaptive pacing. |
| **Uploaded Materials** | Curriculum syllabi, educational reference PDFs. | Ingested for grounded RAG query answering. |

---

## 3. External AI Provider Data Handling

EduPath AI interacts with external Large Language Models under strict privacy constraints:
- **Google Gemini (Primary):**
  - Only anonymized query strings and sanitized curriculum context chunks are transmitted to the Gemini API.
  - Personal identifiable credentials (passwords, student emails, physical addresses) are never bundled into prompts.
  - Google Gemini API terms specify that data submitted through paid API keys is not used to train foundation models.
- **Local Ollama (Fallback):**
  - When running in local mode with Ollama, **100% of LLM inference occurs on-premises**. No data leaves the local network boundary.
- **Offline Heuristic Engine:**
  - In air-gapped environments, inference is performed deterministically on the local CPU without external network calls.

---

## 4. Data Retention, Portability & Deletion

- **Instant Document Deletion:** Deleting a document instantly wipes the physical disk file, removes all corresponding vector embeddings from ChromaDB, and deletes metadata from SQLite.
- **Cascade Account Deletion:** When a student account is removed, SQLite `ON DELETE CASCADE` constraints automatically purge all corresponding profiles, skills, goals, roadmaps, milestones, and conversation histories.
- **No Third-Party Tracking:** EduPath AI contains no third-party commercial trackers, advertising scripts, or data brokers.
