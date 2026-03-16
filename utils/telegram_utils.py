from html import escape as html_escape

from aiogram.types import InlineKeyboardMarkup, Message

MAX_TELEGRAM_MESSAGE_LEN = 4096
SAFE_TELEGRAM_CHUNK_LEN = 3900


def split_for_telegram(
    text: str,
    max_len: int = SAFE_TELEGRAM_CHUNK_LEN,
) -> list[str]:
    cleaned = (text or "").strip()
    if not cleaned:
        return []

    chunks: list[str] = []
    remaining = cleaned
    while len(remaining) > max_len:
        split_at = remaining.rfind("\n", 0, max_len)
        if split_at < max_len // 2:
            split_at = remaining.rfind(" ", 0, max_len)
        if split_at < max_len // 2:
            split_at = max_len

        chunks.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()

    if remaining:
        chunks.append(remaining)
    return chunks


async def answer_long_text(
    message: Message,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: str | None = None,
) -> None:
    chunks = split_for_telegram(text)
    if not chunks:
        chunks = ["(empty response)"]

    for index, chunk in enumerate(chunks):
        await message.answer(
            chunk,
            reply_markup=reply_markup if index == 0 else None,
            parse_mode=parse_mode,
        )


def escape_html(text: str) -> str:
    return html_escape(text, quote=False)
