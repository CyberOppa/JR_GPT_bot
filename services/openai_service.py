import logging
from typing import Optional

from openai import AsyncOpenAI

from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

MODEL = "gpt-4o-mini"
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
