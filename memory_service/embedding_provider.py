from __future__ import annotations

import hashlib
from typing import Protocol


class EmbeddingProvider(Protocol):
    model_name: str
    dimension: int

    def embed_text(self, text: str) -> list[float]: ...


class LocalHashEmbeddingProvider:
    """CPU-friendly deterministic local embedding provider.

    Not semantically rich like transformer models, but useful for local OSS baseline
    and integration testing without external API dependencies.
    """

    def __init__(self, dimension: int = 1536, model_name: str = "local-hash-1536"):
        self.dimension = dimension
        self.model_name = model_name

    def embed_text(self, text: str) -> list[float]:
        vec = [0.0] * self.dimension
        words = text.split()
        if not words:
            return vec
        for w in words:
            digest = hashlib.sha256(w.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % self.dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vec[idx] += sign
        norm = sum(v * v for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec
