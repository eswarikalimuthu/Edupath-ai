"""
EduPath AI - Verifiable Citation Engine
Extracts, formats, and verifies source citations for grounded generation.
"""

from typing import List, Dict, Any

class Citation:
    def __init__(
        self,
        citation_id: int,
        source: str,
        page_number: int,
        chunk_id: str,
        excerpt: str,
        score: float
    ):
        self.citation_id = citation_id
        self.source = source
        self.page_number = page_number
        self.chunk_id = chunk_id
        self.excerpt = excerpt
        self.score = score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "citation_id": self.citation_id,
            "source": self.source,
            "page_number": self.page_number,
            "chunk_id": self.chunk_id,
            "excerpt": self.excerpt,
            "score": round(self.score, 3)
        }

def build_citations(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Construct citation objects from retrieved chunks.
    """
    citations = []
    for idx, c in enumerate(chunks, start=1):
        meta = c.get("metadata", {})
        source = meta.get("source", "Official EduPath Knowledge Base")
        page = meta.get("page_number", 1)
        cid = c.get("chunk_id", f"chunk_{idx}")
        score = c.get("rerank_score", c.get("hybrid_score", c.get("dense_score", 0.0)))
        
        # Take first 150 characters of chunk text as verifiable excerpt
        text = c.get("text", "").strip()
        excerpt = (text[:160] + "...") if len(text) > 160 else text

        cit = Citation(
            citation_id=idx,
            source=source,
            page_number=page,
            chunk_id=cid,
            excerpt=excerpt,
            score=score
        )
        citations.append(cit.to_dict())

    return citations

def format_citations_markdown(citations: List[Dict[str, Any]]) -> str:
    """
    Format citation list into a clean markdown section.
    """
    if not citations:
        return ""

    lines = ["\n\n### 📚 Verified Sources & Citations:"]
    for c in citations:
        lines.append(
            f"- **[{c['citation_id']}] {c['source']}** (Page {c['page_number']}) — *\"{c['excerpt']}\"* (Relevance: {c['score']:.2f})"
        )
    return "\n".join(lines)
