import asyncio
import logging
from typing import Any, Optional

from openai import (
    APIConnectionError,
    APITimeoutError,
    AsyncOpenAI,
    InternalServerError,
    RateLimitError,
)

from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

MODEL = "gpt-4o-mini"
TTS_PRIMARY_MODEL = "gpt-4o-mini-tts"
TTS_FALLBACK_MODEL = "tts-1"
TTS_DEFAULT_VOICE = "shimmer"
REQUEST_TIMEOUT_SECONDS = 30.0
TTS_REQUEST_TIMEOUT_SECONDS = 60.0
MAX_RETRIES = 3
MAX_PARALLEL_OPENAI_REQUESTS = 6
MAX_USER_INPUT_CHARS = 24000
MAX_HISTORY_ITEM_CHARS = 6000
MAX_TTS_INPUT_CHARS = 4200

_TRANSIENT_EXCEPTIONS = (
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    InternalServerError,
)

client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    timeout=REQUEST_TIMEOUT_SECONDS,
    max_retries=0,
)
_openai_semaphore = asyncio.Semaphore(MAX_PARALLEL_OPENAI_REQUESTS)


def _truncate_text(value: str, max_chars: int) -> str:
    cleaned = (value or "").strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars]


async def _request_with_retries(
    request_name: str,
    request_coro_factory,
) -> Any | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with _openai_semaphore:
                return await request_coro_factory()
        except _TRANSIENT_EXCEPTIONS:
            if attempt == MAX_RETRIES:
                logger.exception("%s failed after retries", request_name)
                return None

            delay = 2 ** (attempt - 1)
            logger.warning(
                "%s transient failure (attempt %s/%s), retrying in %ss",
                request_name,
                attempt,
                MAX_RETRIES,
                delay,
            )
            await asyncio.sleep(delay)
        except Exception:
            logger.exception(
                "%s failed with non-retryable error",
                request_name,
            )
            return None

    return None


async def ask_gpt(
    user_message: str,
    system_prompt: str = (
        "You are a helpful scientist-expert assistant. "
        "Answer me short and concisely."
    ),
    history: Optional[list[dict[str, str]]] = None,
) -> str:
    user_payload = _truncate_text(user_message, MAX_USER_INPUT_CHARS)
    if not user_payload:
        return "Error: empty request"

    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt}
    ]
    if history:
        for item in history[-20:]:
            role = item.get("role")
            content = item.get("content", "")
            if role not in {"user", "assistant", "system"}:
                continue
            if not isinstance(content, str):
                continue
            messages.append(
                {
                    "role": role,
                    "content": _truncate_text(content, MAX_HISTORY_ITEM_CHARS),
                }
            )

    messages.append({"role": "user", "content": user_payload})

    response = await _request_with_retries(
        request_name="GPT request",
        request_coro_factory=lambda: client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=900,
            temperature=0.7,
        ),
    )
    if response is None:
        return "Error: try again later"

    answer = response.choices[0].message.content
    if answer:
        return answer.strip()

    logger.error("GPT response has no content")
    return "Error: empty response from model"


async def text_to_speech(
    text: str,
    voice: str = TTS_DEFAULT_VOICE,
) -> bytes | None:
    payload = _truncate_text(text, MAX_TTS_INPUT_CHARS)
    if not payload:
        return None

    for model in (TTS_PRIMARY_MODEL, TTS_FALLBACK_MODEL):
        response = await _request_with_retries(
            request_name=f"TTS request ({model})",
            request_coro_factory=(
                lambda model=model: client.audio.speech.create(
                    model=model,
                    voice=voice,
                    input=payload,
                    response_format="opus",
                    timeout=TTS_REQUEST_TIMEOUT_SECONDS,
                )
            ),
        )
        if response is None:
            continue

        audio_bytes = await response.aread()
        if audio_bytes:
            return audio_bytes

    return None
