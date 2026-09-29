import hashlib
import logging
import math
import os
import re
from collections.abc import Sequence

from apps.api.core.config import settings

logger = logging.getLogger(__name__)

EMBEDDING_DIMENSION = 768
DEFAULT_EMBEDDING_MODEL = "text-embedding-004"


def generate_fallback_embedding(text: str, dim: int = EMBEDDING_DIMENSION) -> list[float]:
    """
    Generates a deterministic, normalized 768-dimensional float embedding using
    token hashing, subwords, and TF weighting. Guarantees cosine similarity
    proportional to term and subword overlap when external LLM API is unavailable.
    """
    clean_text = text.lower().strip()
    tokens = re.findall(r"\b\w+\b", clean_text)
    if not tokens:
        # Return zero vector with slight noise normalized
        vec = [0.0] * dim
        vec[0] = 1.0
        return vec

    vector = [0.0] * dim

    for i, token in enumerate(tokens):
        # 1. Full word hash
        h_word = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        idx_word = h_word % dim
        sign_word = 1.0 if (h_word >> 8) & 1 else -1.0
        vector[idx_word] += sign_word * 1.5

        # 2. Subword 3-grams for morphological/semantic matching across languages
        if len(token) >= 3:
            for j in range(len(token) - 2):
                ngram = token[j : j + 3]
                h_ng = int(hashlib.sha256(ngram.encode("utf-8")).hexdigest(), 16)
                idx_ng = h_ng % dim
                sign_ng = 1.0 if (h_ng >> 8) & 1 else -1.0
                vector[idx_ng] += sign_ng * 0.5

    # L2 Normalization to unit length
    squared_sum = sum(x * x for x in vector)
    norm = math.sqrt(squared_sum)
    if norm > 0:
        return [round(x / norm, 6) for x in vector]
    else:
        vector[0] = 1.0
        return vector


def cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    """Computes cosine similarity between two numeric vectors."""
    if len(vec_a) != len(vec_b):
        min_len = min(len(vec_a), len(vec_b))
        vec_a = vec_a[:min_len]
        vec_b = vec_b[:min_len]

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return max(-1.0, min(1.0, dot_product / (norm_a * norm_b)))


class EmbeddingService:
    def __init__(self):
        self.api_key = (
            settings.GEMINI_API_KEY
            or settings.GOOGLE_API_KEY
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
        )
        self.client = None
        if self.api_key:
            try:
                from google import genai

                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Google GenAI embedding client: {e}")

    async def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generates dense vector embeddings for a list of text strings.
        Uses Google GenAI SDK if available, falling back to deterministic local embeddings.
        """
        if not texts:
            return []

        if self.client:
            try:
                # Gemini embed_content supports batching
                results: list[list[float]] = []
                # Batch in groups of 20 to avoid API limits
                batch_size = 20
                for i in range(0, len(texts), batch_size):
                    batch = texts[i : i + batch_size]
                    response = self.client.models.embed_content(
                        model=DEFAULT_EMBEDDING_MODEL,
                        contents=batch,
                    )
                    if hasattr(response, "embeddings") and response.embeddings:
                        for item in response.embeddings:
                            results.append(list(item.values))
                    elif hasattr(response, "embedding") and response.embedding:
                        results.append(list(response.embedding.values))

                if len(results) == len(texts):
                    return results
            except Exception as e:
                logger.warning(f"Google GenAI embedding call failed, falling back to local: {e}")

        # Fallback local embeddings
        return [generate_fallback_embedding(t) for t in texts]

    async def get_embedding(self, text: str) -> list[float]:
        """Generates embedding vector for a single text."""
        res = await self.get_embeddings([text])
        return res[0]
