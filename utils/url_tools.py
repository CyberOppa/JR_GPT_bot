import re
import logging
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Basic user agent to avoid some blocks, though many sites block non-browser UAs
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"

def extract_first_url(text: str) -> str | None:
    match = re.search(r"https?://[^\s<>]+", text or "")
    if not match:
        return None
    return match.group(0).rstrip(").,!?\"'")

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

async def fetch_url_content(url: str) -> str | None:
    """
    Fetches the content of a URL and returns the text.
    Returns None if the fetch fails or if the content type is not text/html.
    """
    if not is_valid_url(url):
        return None

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, 
                headers={"User-Agent": USER_AGENT}, 
                timeout=15
            ) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch {url}, status: {response.status}")
                    return None
                
                content_type = response.headers.get('Content-Type', '').lower()
                if 'text/html' not in content_type and 'text/plain' not in content_type:
                    logger.warning(f"Skipping {url} due to content type: {content_type}")
                    return None

                html = await response.text()
                return _parse_html(html)
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

def _parse_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.extract()
    
    # Get text
    text = soup.get_text()
    
    # Break into lines and remove leading/trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text
