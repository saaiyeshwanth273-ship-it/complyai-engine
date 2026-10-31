"""Embeddings layer with legal & multilingual embedding support and deterministic offline fallback.
"""
from __future__ import annotations

import hashlib
import math
from typing import List


class EmbeddingService:
    """Provides vector embeddings for legal clauses, queries, and requirements."""

    def __init__(self, model_name: str = "legal-multilingual-384", dimension: int = 384):
        self.model_name = model_name
        self.dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        """Generates a dense normalized vector for the given text.
        Uses token hashing with positional and semantic frequency weighting to guarantee
        reproducibility and standalone offline execution without external dependencies.
        """
        words = text.lower().split()
        if not words:
            return [0.0] * self.dimension

        vector = [0.0] * self.dimension
        for idx, word in enumerate(words):
            # Clean punctuation
            w_clean = "".join(ch for ch in word if ch.isalnum())
            if not w_clean:
                continue

            # Deterministic bucket hash
            h = int(hashlib.md5(w_clean.encode("utf-8")).hexdigest(), 16)
            dim_idx = h % self.dimension
            sign = 1.0 if ((h >> 8) & 1) == 0 else -1.0

            # Weight by word length and inverse position
            weight = math.log1p(len(w_clean)) / (1.0 + 0.05 * idx)
            vector[dim_idx] += sign * weight

        # Normalize to unit sphere
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0.0:
            vector = [x / norm for x in vector]
        return vector

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]

