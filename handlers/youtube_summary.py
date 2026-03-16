import logging

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.inline import main_menu, yt_length_keyboard
from services.openai_service import ask_gpt
from states.state import YouTubeStates
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
    await state.update_data(yt_video_id=None, yt_url=None)
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
    await state.update_data(yt_video_id=video_id, yt_url=url)
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


async def _generate_summary(
    message: Message,
    state: FSMContext,
    minutes: int,
) -> None:
    data = await state.get_data()
    video_id = data.get("yt_video_id")
    source_url = data.get("yt_url")
    if not video_id:
        await _open_youtube_mode(message, state)
        return

    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING,
    )

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
    await message.answer(summary, reply_markup=yt_length_keyboard())


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

    await _generate_summary(callback.message, state, minutes)


@router.callback_query(F.data == "yt:new")
async def on_youtube_new_link(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.message:
        await _open_youtube_mode(callback.message, state)


@router.callback_query(F.data == "yt:cancel")
async def on_youtube_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            "YouTube summary mode ended.",
            reply_markup=main_menu(),
        )
