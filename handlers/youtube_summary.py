import logging

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from keyboards.inline import main_menu, yt_length_keyboard
from services.openai_service import ask_gpt, text_to_speech
from states.state import YouTubeStates
from utils.chat_locks import get_chat_lock
from utils.rate_limit import get_retry_after
from utils.telegram_utils import answer_long_text
from utils.youtube_tools import extract_first_url, extract_youtube_video_id
from utils.youtube_tools import fetch_youtube_transcript

router = Router()
logger = logging.getLogger(__name__)

SUMMARY_SYSTEM_PROMPT = (
    "You are a learning assistant. "
    "Create practical summaries from transcripts. "
    "Avoid filler, keep structure clear, and stay faithful to the source."
)


async def _open_youtube_mode(message: Message, state: FSMContext) -> None:
    await state.set_state(YouTubeStates.waiting_url)
    await state.update_data(
        yt_video_id=None,
        yt_url=None,
        yt_transcript=None,
        yt_last_summary=None,
    )
    await message.answer(
        "YouTube summary mode.\n\n"
        "Send a YouTube link.\n"
        "You can also use command format:\n"
        "/yt <url> 2  or  /yt <url> 5",
        reply_markup=yt_length_keyboard(),
    )


def _parse_command_payload(command_text: str) -> tuple[str | None, int | None]:
    parts = command_text.split()
    if len(parts) < 2:
        return None, None

    payload = " ".join(parts[1:])
    url = extract_first_url(payload)
    if not url:
        return None, None

    minutes = None
    for part in parts[1:]:
        if part.isdigit():
            value = int(part)
            if value in {2, 5}:
                minutes = value
                break

    return url, minutes


async def _set_video_from_url(
    message: Message,
    state: FSMContext,
    url: str,
) -> bool:
    video_id = extract_youtube_video_id(url)
    if not video_id:
        await message.answer("Invalid YouTube link. Send a valid URL.")
        return False

    await state.set_state(YouTubeStates.choosing_length)
    await state.update_data(
        yt_video_id=video_id,
        yt_url=url,
        yt_transcript=None,
        yt_last_summary=None,
    )
    return True


def _word_target(minutes: int) -> str:
    if minutes == 2:
        return "300-450 words"
    return "700-900 words"


def _trim_transcript(text: str, max_chars: int = 24000) -> str:
    if len(text) <= max_chars:
        return text

    half = max_chars // 2
    return f"{text[:half]}\n...\n{text[-half:]}"


def _trim_for_voice(text: str, max_chars: int = 4200) -> str:
    if len(text) <= max_chars:
        return text
    return (
        text[:max_chars]
        + "\n\n[Voice version trimmed due to length.]"
    )


async def _generate_summary(
    message: Message,
    state: FSMContext,
    minutes: int,
) -> None:
    data = await state.get_data()
    video_id = data.get("yt_video_id")
    source_url = data.get("yt_url")
    transcript = data.get("yt_transcript")
    if not video_id:
        await _open_youtube_mode(message, state)
        return

    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING,
    )

    if not transcript:
        try:
            transcript = await fetch_youtube_transcript(video_id)
        except Exception:
            logger.exception("Failed to fetch transcript for %s", video_id)
            await message.answer(
                "Could not fetch transcript for this video. "
                "Try another link with subtitles.",
                reply_markup=yt_length_keyboard(),
            )
            return

        transcript = _trim_transcript(transcript)
        await state.update_data(yt_transcript=transcript)

    summary = await ask_gpt(
        user_message=(
            f"Video URL: {source_url}\n"
            f"Target reading time: {minutes} minutes "
            f"({_word_target(minutes)}).\n\n"
            "Output format:\n"
            "1) TL;DR (2-3 bullets)\n"
            "2) Main points\n"
            "3) Actionable takeaways\n"
            "4) Open questions\n\n"
            f"Transcript:\n{transcript}"
        ),
        system_prompt=SUMMARY_SYSTEM_PROMPT,
    )
    await state.update_data(yt_last_summary=summary)
    await answer_long_text(message, summary, reply_markup=yt_length_keyboard())


@router.message(Command("yt"))
async def cmd_youtube_summary(message: Message, state: FSMContext):
    url, minutes = _parse_command_payload(message.text or "")
    if not url:
        await _open_youtube_mode(message, state)
        return

    is_valid = await _set_video_from_url(message, state, url)
    if not is_valid:
        return

    if minutes in {2, 5}:
        retry_after = get_retry_after(
            user_id=message.from_user.id if message.from_user else 0,
            scope="yt_summary",
            limit=5,
            window_seconds=60,
        )
        if retry_after:
            await message.answer(
                f"Too many requests. Try again in {retry_after}s.",
                reply_markup=yt_length_keyboard(),
            )
            return

        lock = get_chat_lock(message.chat.id, "youtube")
        async with lock:
            await _generate_summary(message, state, minutes)
        return

    await message.answer(
        "Choose summary length:",
        reply_markup=yt_length_keyboard(),
    )


@router.callback_query(F.data == "menu:yt")
async def on_menu_youtube(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.message:
        await _open_youtube_mode(callback.message, state)


@router.message(YouTubeStates.waiting_url, F.text)
async def on_youtube_url_received(message: Message, state: FSMContext):
    url = extract_first_url(message.text or "")
    if not url:
        await message.answer("Send a valid YouTube link.")
        return

    is_valid = await _set_video_from_url(message, state, url)
    if not is_valid:
        return

    await message.answer(
        "Choose summary length:",
        reply_markup=yt_length_keyboard(),
    )


@router.message(YouTubeStates.choosing_length, F.text)
async def on_youtube_text_while_choosing(
    message: Message,
    state: FSMContext,
):
    text = (message.text or "").strip()
    url = extract_first_url(text)
    if url:
        is_valid = await _set_video_from_url(message, state, url)
        if not is_valid:
            return
        await message.answer(
            "New video accepted. Choose summary length:",
            reply_markup=yt_length_keyboard(),
        )
        return

    if text in {"2", "5"}:
        minutes = int(text)
        retry_after = get_retry_after(
            user_id=message.from_user.id if message.from_user else 0,
            scope="yt_summary",
            limit=5,
            window_seconds=60,
        )
        if retry_after:
            await message.answer(
                f"Too many requests. Try again in {retry_after}s.",
                reply_markup=yt_length_keyboard(),
            )
            return

        lock = get_chat_lock(message.chat.id, "youtube")
        async with lock:
            await _generate_summary(message, state, minutes)
        return

    await message.answer(
        (
            "Use buttons or send `2` / `5`. "
            "You can also send another YouTube link."
        ),
        reply_markup=yt_length_keyboard(),
    )


@router.callback_query(
    YouTubeStates.choosing_length,
    F.data.startswith("yt:length:"),
)
async def on_youtube_length(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not callback.message:
        return

    length_text = callback.data.split(":")[-1]
    minutes = int(length_text) if length_text.isdigit() else 2
    if minutes not in {2, 5}:
        minutes = 2

    retry_after = get_retry_after(
        user_id=callback.from_user.id,
        scope="yt_summary",
        limit=5,
        window_seconds=60,
    )
    if retry_after:
        await callback.message.answer(
            f"Too many requests. Try again in {retry_after}s.",
            reply_markup=yt_length_keyboard(),
        )
        return

    lock = get_chat_lock(callback.message.chat.id, "youtube")
    async with lock:
        await _generate_summary(callback.message, state, minutes)


@router.callback_query(F.data == "yt:new")
async def on_youtube_new_link(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.message:
        await _open_youtube_mode(callback.message, state)


@router.callback_query(F.data == "yt:read")
async def on_youtube_read_aloud(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not callback.message:
        return

    retry_after = get_retry_after(
        user_id=callback.from_user.id,
        scope="yt_tts",
        limit=4,
        window_seconds=60,
    )
    if retry_after:
        await callback.message.answer(
            f"Too many requests. Try again in {retry_after}s.",
            reply_markup=yt_length_keyboard(),
        )
        return

    data = await state.get_data()
    summary = data.get("yt_last_summary")
    if not summary:
        await callback.message.answer(
            "Generate a summary first, then tap Read aloud.",
            reply_markup=yt_length_keyboard(),
        )
        return

    await callback.message.bot.send_chat_action(
        chat_id=callback.message.chat.id,
        action=ChatAction.RECORD_VOICE,
    )
    lock = get_chat_lock(callback.message.chat.id, "youtube")
    async with lock:
        audio_bytes = await text_to_speech(_trim_for_voice(summary))
    if not audio_bytes:
        await callback.message.answer(
            "Could not generate voice right now. Try again later.",
            reply_markup=yt_length_keyboard(),
        )
        return

    voice_file = BufferedInputFile(audio_bytes, filename="yt_summary.ogg")
    await callback.message.answer_voice(
        voice=voice_file,
        caption="🔊 YouTube summary (audio)",
        reply_markup=yt_length_keyboard(),
    )


@router.callback_query(F.data == "yt:cancel")
async def on_youtube_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            "YouTube summary mode ended.",
            reply_markup=main_menu(),
        )
