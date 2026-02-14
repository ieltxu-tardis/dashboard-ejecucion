from __future__ import annotations


def chunk_text(text: str, *, max_chars: int = 900, overlap: int = 120) -> list[str]:
    if not text:
        return []
    chunks: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        end = min(i + max_chars, n)
        chunks.append(text[i:end])
        if end == n:
            break
        i = max(0, end - overlap)
    return chunks
