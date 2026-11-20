"""
EduPath AI - ChromaDB Vector Store Integration
Manages persistent collection, metadata filtering, and user isolation.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.config import settings
from rag.embeddings import get_embedding_model
from rag.chunking import DocumentChunk

class ChromaVectorStore:
    def __init__(self, persist_dir: str = None, collection_name: str = None):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIRECTORY
        self.collection_name = collection_name or settings.DEFAULT_COLLECTION_NAME
        Path(self.persist_dir).mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False, is_persistent=True)
        )
        self.embedder = get_embedding_model()
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "EduPath AI Knowledge Base"}
        )

    def add_chunks(self, chunks: List[DocumentChunk]) -> int:
        """Insert or update chunks in ChromaDB with their embeddings and metadata."""
        if not chunks:
            return 0

        ids = [c.chunk_id for c in chunks]
        texts = [c.text for c in chunks]
        metadatas = []
        for c in chunks:
            m = dict(c.metadata)
            # Ensure primitive values for ChromaDB metadata
            clean_m = {}
            for k, v in m.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_m[k] = v
                else:
                    clean_m[k] = str(v)
            metadatas.append(clean_m)

        embeddings = self.embedder.embed_documents(texts)

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
        return len(chunks)

    def search_dense(
        self,
        query: str,
        top_k: int = 10,
        user_id: Optional[str] = None,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform dense vector similarity search with user-isolation metadata filtering.
        """
        query_embedding = self.embedder.embed_query(query)
        
        # Build ChromaDB metadata filter
        where_filter = None
        conditions = []
        
        if user_id:
            conditions.append({"$or": [{"user_id": user_id}, {"is_global": True}, {"is_global": "True"}]})
            
        if filter_dict:
            for k, v in filter_dict.items():
                conditions.append({k: v})
                
        if len(conditions) == 1:
            where_filter = conditions[0]
        elif len(conditions) > 1:
            where_filter = {"$and": conditions}

        total_docs = self.collection.count()
        if total_docs == 0:
            return []

        actual_k = min(top_k, total_docs)
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": actual_k,
            "include": ["documents", "metadatas", "distances"]
        }
        if where_filter:
            try:
                kwargs["where"] = where_filter
                results = self.collection.query(**kwargs)
            except Exception:
                # If complex where filter causes issue in older Chroma, fallback to simpler filter
                del kwargs["where"]
                results = self.collection.query(**kwargs)
        else:
            results = self.collection.query(**kwargs)

        output = []
        if not results or not results["ids"] or not results["ids"][0]:
            return []

        for i in range(len(results["ids"][0])):
            cid = results["ids"][0][i]
            text = results["documents"][0][i]
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            dist = results["distances"][0][i] if results["distances"] else 1.0
            
            # Convert cosine distance to similarity score in [0, 1]
            score = max(0.0, min(1.0, 1.0 - (dist / 2.0)))
            
            # Additional Python-side user ownership check for strict isolation
            chunk_user_id = meta.get("user_id")
            is_global = meta.get("is_global") in (True, "True", 1, "1")
            if user_id and chunk_user_id != user_id and not is_global:
                continue

            output.append({
                "chunk_id": cid,
                "text": text,
                "metadata": meta,
                "dense_score": score,
                "distance": dist
            })

        return output

    def delete_document_chunks(self, doc_id: str) -> int:
        """Delete all chunks associated with a specific document ID."""
        try:
            self.collection.delete(where={"doc_id": doc_id})
            return 1
        except Exception:
            return 0

    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Retrieve all chunks stored in the collection."""
        res = self.collection.get(include=["documents", "metadatas"])
        chunks = []
        if not res or not res["ids"]:
            return []
        for i in range(len(res["ids"])):
            chunks.append({
                "chunk_id": res["ids"][i],
                "text": res["documents"][i],
                "metadata": res["metadatas"][i] if res["metadatas"] else {}
            })
        return chunks

    def count(self) -> int:
        return self.collection.count()

_vector_store_instance: Optional[ChromaVectorStore] = None

def get_vector_store() -> ChromaVectorStore:
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = ChromaVectorStore()
    return _vector_store_instance
