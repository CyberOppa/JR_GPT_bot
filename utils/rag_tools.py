import re
import logging
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"


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

        start = end - overlap
        if start < 0:
            start = 0

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
    # Use \w+ to match words in different languages
    return set(re.findall(r"\w{2,}", text.lower()))


async def fetch_url_content(url: str) -> str | None:
    """
    Fetches the content of a URL and returns the text.
    Returns None if the fetch fails or if the content type is not text/html.
    """
    if not _is_valid_url(url):
        return None

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, 
                headers={"User-Agent": USER_AGENT}, 
                timeout=15
            ) as response:
                if response.status != 200:
                    logger.warning("Failed to fetch %s, status: %s", url, response.status)
                    return None
                
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' not in content_type and 'text/plain' not in content_type:
                    logger.warning("Skipping %s due to content type: %s", url, content_type)
                    return None

                html = await response.text()
                return _parse_html(html)
    except Exception as e:
        logger.error("Error fetching %s: %s", url, e)
        return None


def _is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def _parse_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        script.extract()
    
    # Get text
    text = soup.get_text(separator=' ')
    
    # Break into lines and remove leading/trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text
