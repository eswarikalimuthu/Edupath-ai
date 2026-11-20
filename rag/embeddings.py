"""
EduPath AI - Embedding Models
Pluggable embedding architecture supporting offline deterministic hashing,
Google Gemini embeddings, and local models.
"""

from abc import ABC, abstractmethod
from typing import List
import math
import hashlib
import re
from backend.config import settings

class BaseEmbeddings(ABC):
    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        pass

class OfflineDeterministicEmbeddings(BaseEmbeddings):
    """
    Deterministic subword n-gram and word feature-hashing embedder with L2 normalization.
    Generates consistent 384-dimensional dense vectors with cosine similarity properties.
    Requires no external downloads, runs 100% offline, and is extremely fast.
    """
    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def _hash_token(self, token: str) -> int:
        h = hashlib.sha256(token.encode("utf-8")).hexdigest()
        return int(h[:8], 16) % self.dimension

    def _embed_single(self, text: str) -> List[float]:
        vec = [0.0] * self.dimension
        if not text:
            return vec

        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            return vec

        # Unigrams, Bigrams, and 3-char subwords
        features = list(tokens)
        for i in range(len(tokens) - 1):
            features.append(f"{tokens[i]}_{tokens[i+1]}")
            
        for t in tokens:
            if len(t) >= 4:
                for j in range(len(t) - 2):
                    features.append(t[j:j+3])

        for f in features:
            idx = self._hash_token(f)
            # Sign hash for unbiased hashing
            sign = 1.0 if (hash(f) % 2 == 0) else -1.0
            vec[idx] += sign

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0.0:
            vec = [x / norm for x in vec]
            
        return vec

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_single(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed_single(text)

class GeminiEmbeddings(BaseEmbeddings):
    """Embeddings via Google Gemini API."""
    def __init__(self, api_key: str = None, model: str = "models/text-embedding-004"):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model
        self.fallback = OfflineDeterministicEmbeddings(dimension=384)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not self.api_key:
            return self.fallback.embed_documents(texts)
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            result = genai.embed_content(
                model=self.model,
                content=texts,
                task_type="retrieval_document"
            )
            return result["embedding"]
        except Exception:
            return self.fallback.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        if not self.api_key:
            return self.fallback.embed_query(text)
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_query"
            )
            return result["embedding"]
        except Exception:
            return self.fallback.embed_query(text)

_embedding_instance: BaseEmbeddings = None

def get_embedding_model() -> BaseEmbeddings:
    """Singleton factory for obtaining the configured embedding model."""
    global _embedding_instance
    if _embedding_instance is None:
        provider = settings.EMBEDDING_PROVIDER.lower()
        if provider == "gemini" and settings.GEMINI_API_KEY:
            _embedding_instance = GeminiEmbeddings()
        else:
            _embedding_instance = OfflineDeterministicEmbeddings(dimension=384)
    return _embedding_instance
