import asyncio
import re
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi


def extract_youtube_video_id(url: str) -> str | None:
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower().replace("www.", "")

    if host == "youtu.be":
        video_id = parsed.path.lstrip("/")
        return video_id.split("/")[0] if video_id else None

    if host in {"youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]
        if parsed.path.startswith("/shorts/"):
            return parsed.path.split("/")[2]
        if parsed.path.startswith("/embed/"):
            return parsed.path.split("/")[2]

    return None


def extract_first_url(text: str) -> str | None:
    match = re.search(r"https?://\S+", text)
    if not match:
        return None
    return match.group(0).strip()


async def fetch_youtube_transcript(video_id: str) -> str:
    return await asyncio.to_thread(_fetch_transcript_sync, video_id)


def _fetch_transcript_sync(video_id: str) -> str:
    languages = ["en", "en-US", "de", "ru"]

    # youtube-transcript-api <= 0.6 style
    try:
        items = YouTubeTranscriptApi.get_transcript(
            video_id,
            languages=languages,
        )
        text = _join_items(items)
        if text:
            return text
    except Exception:
        pass

    # youtube-transcript-api newer style with class instance
    api = YouTubeTranscriptApi()
    if hasattr(api, "fetch"):
        fetched = api.fetch(video_id, languages=languages)
        snippets = getattr(fetched, "snippets", fetched)
        text = _join_items(snippets)
        if text:
            return text

    raise RuntimeError("Transcript is unavailable for this video")


def _join_items(items) -> str:
    parts: list[str] = []
    for item in items:
        text = ""
        if isinstance(item, dict):
            text = str(item.get("text", "")).strip()
        else:
            text = str(getattr(item, "text", "")).strip()

        if text:
            parts.append(text)

    return " ".join(parts).strip()
