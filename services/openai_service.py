import logging
from typing import Optional

from openai import AsyncOpenAI

from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

MODEL = "gpt-4o-mini"
TTS_PRIMARY_MODEL = "gpt-4o-mini-tts"
TTS_FALLBACK_MODEL = "tts-1"
TTS_DEFAULT_VOICE = "alloy"
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def ask_gpt(
    user_message: str,
    system_prompt: str = (
        "You are a helpful scientist-expert assistant. "
        "Answer me short and concisely."
    ),
    history: Optional[list[dict[str, str]]] = None,
) -> str:
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt}
    ]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1000,
            temperature=0.8,
        )
    except Exception:
        logger.exception("GPT request failed")
        return "Error: try again later"

    answer = response.choices[0].message.content
    if answer:
        return answer

    logger.error("GPT response has no content")
    return "Error: empty response from model"


async def text_to_speech(
    text: str,
    voice: str = TTS_DEFAULT_VOICE,
) -> bytes | None:
    payload = text.strip()
    if not payload:
        return None

    for model in (TTS_PRIMARY_MODEL, TTS_FALLBACK_MODEL):
        try:
            response = await client.audio.speech.create(
                model=model,
                voice=voice,
                input=payload,
                response_format="opus",
            )
            audio_bytes = await response.aread()
            if audio_bytes:
                return audio_bytes
        except Exception:
            logger.exception("TTS request failed for model %s", model)

    return None
