import asyncio
import logging
import re
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)
_YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def _normalize_video_id(candidate: str | None) -> str | None:
    if not candidate:
        return None
    value = candidate.strip()
    return value if _YOUTUBE_ID_RE.fullmatch(value) else None


def extract_youtube_video_id(url: str) -> str | None:
    parsed = urlparse((url or "").strip())
    host = parsed.netloc.lower().replace("www.", "")

    if host == "youtu.be":
        video_id = parsed.path.lstrip("/")
        short_id = video_id.split("/")[0] if video_id else None
        return _normalize_video_id(short_id)

    if host in {"youtube.com", "m.youtube.com", "youtube-nocookie.com"}:
        if parsed.path == "/watch":
            query_video_id = parse_qs(parsed.query).get("v", [None])[0]
            return _normalize_video_id(query_video_id)
        if parsed.path.startswith("/shorts/"):
            parts = parsed.path.split("/")
            return _normalize_video_id(parts[2] if len(parts) > 2 else None)
        if parsed.path.startswith("/embed/"):
            parts = parsed.path.split("/")
            return _normalize_video_id(parts[2] if len(parts) > 2 else None)

    return None


def extract_first_url(text: str) -> str | None:
    match = re.search(r"https?://[^\s<>]+", text or "")
    if not match:
        return None
    return match.group(0).rstrip(").,!?\"'")


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
    except Exception as error:
        logger.debug(
            "Legacy transcript fetch failed for %s: %s",
            video_id,
            error,
        )

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
