"""
EduPath AI - Document Chunking Module
Recursive character splitting preserving sentence and paragraph integrity.
"""

from typing import List, Dict, Any
from backend.config import settings

class DocumentChunk:
    def __init__(
        self,
        chunk_id: str,
        text: str,
        metadata: Dict[str, Any]
    ):
        self.chunk_id = chunk_id
        self.text = text
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "metadata": self.metadata
        }

def recursive_split_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    separators: List[str] = None
) -> List[str]:
    """
    Split text recursively by separators: paragraphs (\n\n), sentences (\n, . ), phrases (, ), and spaces.
    """
    if separators is None:
        separators = ["\n\n", "\n", ". ", "; ", ", ", " "]
        
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
        
    # Find the highest priority separator present in the text
    chosen_sep = ""
    for sep in separators:
        if sep in text:
            chosen_sep = sep
            break
            
    if not chosen_sep:
        # Fallback to hard character slicing if no separator matches
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += chunk_size - chunk_overlap
        return chunks
        
    splits = text.split(chosen_sep)
    chunks = []
    current_chunk = ""
    
    for split in splits:
        if not split.strip():
            continue
            
        candidate = f"{current_chunk}{chosen_sep}{split}".strip() if current_chunk else split.strip()
        
        if len(candidate) <= chunk_size:
            current_chunk = candidate
        else:
            if current_chunk:
                chunks.append(current_chunk)
                
            # If a single split is larger than chunk_size, recurse on it with sub-separators
            if len(split) > chunk_size:
                sub_seps = separators[separators.index(chosen_sep) + 1:] if chosen_sep in separators else []
                sub_chunks = recursive_split_text(split, chunk_size, chunk_overlap, sub_seps)
                if sub_chunks:
                    chunks.extend(sub_chunks[:-1])
                    current_chunk = sub_chunks[-1]
                else:
                    current_chunk = ""
            else:
                # Start new chunk with overlap if possible
                overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else ""
                current_chunk = f"{overlap_text} {split}".strip() if overlap_text else split.strip()
                
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def chunk_document_pages(
    pages: List[Dict[str, Any]],
    doc_id: str,
    source_name: str,
    user_id: str = None,
    is_global: bool = False,
    doc_type: str = "educational",
    chunk_size: int = None,
    chunk_overlap: int = None
) -> List[DocumentChunk]:
    """
    Split pages into enriched DocumentChunks with source, page number, and ownership metadata.
    """
    c_size = chunk_size or settings.CHUNK_SIZE
    c_overlap = chunk_overlap or settings.CHUNK_OVERLAP
    
    all_chunks: List[DocumentChunk] = []
    chunk_counter = 0
    
    for page in pages:
        page_num = page.get("page_number", 1)
        raw_text = page.get("text", "")
        if not raw_text.strip():
            continue
            
        splits = recursive_split_text(raw_text, chunk_size=c_size, chunk_overlap=c_overlap)
        
        for split in splits:
            if not split.strip():
                continue
            chunk_counter += 1
            chunk_id = f"{doc_id}_p{page_num}_c{chunk_counter}"
            
            metadata = {
                "doc_id": doc_id,
                "source": source_name,
                "page_number": page_num,
                "chunk_index": chunk_counter,
                "user_id": user_id or "global",
                "is_global": is_global,
                "doc_type": doc_type,
            }
            
            all_chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                text=split,
                metadata=metadata
            ))
            
    return all_chunks
