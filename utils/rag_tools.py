import re


def split_text_into_chunks(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 150,
) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []

    if len(normalized) <= chunk_size:
        return [normalized]

    chunks: list[str] = []
    start = 0
    text_length = len(normalized)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = normalized[start:end]

        if end < text_length:
            last_space = chunk.rfind(" ")
            if last_space > chunk_size // 2:
                chunk = chunk[:last_space]
                end = start + last_space

        chunk = chunk.strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = max(end - overlap, 0)

    return chunks


def select_relevant_chunks(
    chunks: list[str],
    query: str,
    top_k: int = 4,
) -> list[str]:
    if not chunks:
        return []

    query_terms = _tokenize(query)
    if not query_terms:
        return chunks[:top_k]

    scored: list[tuple[int, int]] = []
    for index, chunk in enumerate(chunks):
        overlap = len(query_terms & _tokenize(chunk))
        if overlap > 0:
            scored.append((overlap, index))

    if not scored:
        return chunks[:top_k]

    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunks[index] for _, index in scored[:top_k]]


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[0-9a-zA-Zа-яА-ЯёЁ]{2,}", text.lower()))
