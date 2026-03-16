import logging

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message, FSInputFile

from keyboards.inline import main_menu, yt_read_keyboard, yt_lang_keyboard, yt_after_read_keyboard, yt_cancel_keyboard
from services.openai_service import ask_gpt, text_to_speech
from states.state import YouTubeStates
from utils.chat_locks import get_chat_lock
from utils.rate_limit import get_retry_after
from utils.telegram_utils import answer_long_text, escape_html
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
        yt_lang="en",  # Default to English if not chosen
    )
    
    caption_text = (
        "YouTube summary mode.\n\n"
        "Send a YouTube link.\n"
        "You can also use command format:\n"
        f"/yt {escape_html('<url>')}"
    )

    try:
        photo = FSInputFile('images/yt.png')
        await message.answer_photo(
            photo=photo,
            caption=caption_text,
            reply_markup=yt_cancel_keyboard(),
            parse_mode='HTML',
        )
    except Exception:
        logger.exception("YouTube image was not sent")
        await message.answer(
            caption_text,
            reply_markup=yt_cancel_keyboard(),
            parse_mode='HTML',
        )


def _parse_command_payload(command_text: str) -> str | None:
    parts = command_text.split()
    if len(parts) < 2:
        return None

    payload = " ".join(parts[1:])
    url = extract_first_url(payload)
    return url


async def _set_video_from_url(
    message: Message,
    state: FSMContext,
    url: str,
) -> bool:
    video_id = extract_youtube_video_id(url)
    if not video_id:
        await message.answer("Invalid YouTube link. Send a valid URL.")
        return False

    await state.set_state(YouTubeStates.choosing_lang)
    await state.update_data(
        yt_video_id=video_id,
        yt_url=url,
        yt_transcript=None,
        yt_last_summary=None,
    )
    return True


def _word_target() -> str:
    return "500-600 words"


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
) -> None:
    await state.set_state(YouTubeStates.waiting_url)

    data = await state.get_data()
    video_id = data.get("yt_video_id")
    source_url = data.get("yt_url")
    transcript = data.get("yt_transcript")
    lang_code = data.get("yt_lang", "en")
    minutes = 3

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
                reply_markup=yt_read_keyboard(),
            )
            return

        transcript = _trim_transcript(transcript)
        await state.update_data(yt_transcript=transcript)

    lang_instruction = ""
    if lang_code == "de":
        lang_instruction = "IMPORTANT: Write the summary strictly in GERMAN language."
    elif lang_code == "ru":
        lang_instruction = "IMPORTANT: Write the summary strictly in RUSSIAN language."
    else:
        lang_instruction = "IMPORTANT: Write the summary strictly in ENGLISH language."

    summary = await ask_gpt(
        user_message=(
            f"Video URL: {source_url}\n"
            f"Target reading time: {3} minutes "
            f"({_word_target()}).\n"
            f"{lang_instruction}\n\n"
            "Output format:\n"
            "1) TL;DR (4-5 bullets)\n"
            "2) Main points\n"
            "3) Actionable takeaways\n"
            "4) Open questions\n\n"
            f"Transcript:\n{transcript}"
        ),
        system_prompt=SUMMARY_SYSTEM_PROMPT,
    )
    await state.update_data(yt_last_summary=summary)
    await answer_long_text(message, summary, reply_markup=yt_read_keyboard())


@router.message(Command("yt"))
async def cmd_youtube_summary(message: Message, state: FSMContext):
    url = _parse_command_payload(message.text or "")
    if not url:
        await _open_youtube_mode(message, state)
        return

    is_valid = await _set_video_from_url(message, state, url)
    if is_valid:
        await message.answer(
            "Link accepted. Choose summary language:",
            reply_markup=yt_lang_keyboard(),
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
    if is_valid:
        await message.answer(
            "Choose summary language:",
            reply_markup=yt_lang_keyboard(),
        )


@router.callback_query(
    YouTubeStates.choosing_lang,
    F.data.startswith("yt:lang:"),
)
async def on_youtube_lang_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    lang_code = callback.data.split(":")[-1]
    
    await state.update_data(yt_lang=lang_code)
    
    lang_name = "English"
    if lang_code == 'de':
        lang_name = "German"
    elif lang_code == 'ru':
        lang_name = "Russian"

    if callback.message:
        await callback.message.edit_text(
            f"Language: {lang_name}. Generating summary...",
            reply_markup=None
        )
        retry_after = get_retry_after(
            user_id=callback.from_user.id,
            scope="yt_summary",
            limit=5,
            window_seconds=60,
        )
        if retry_after:
            await callback.message.answer(
                f"Too many requests. Try again in {retry_after}s.",
                reply_markup=yt_read_keyboard(),
            )
            return

        lock = get_chat_lock(callback.message.chat.id, "youtube")
        async with lock:
            await _generate_summary(callback.message, state)
        

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
            reply_markup=yt_read_keyboard(),
        )
        return

    data = await state.get_data()
    summary = data.get("yt_last_summary")
    if not summary:
        await callback.message.answer(
            "Generate a summary first, then tap Read aloud.",
            reply_markup=yt_read_keyboard(),
        )
        return

    # Sende eine "Generiere Audio..."-Nachricht
    processing_message = await callback.message.answer(
        "🔊 Generating audio...",
        reply_markup=None # Kein Keyboard, da es eine temporäre Nachricht ist
    )

    await callback.message.bot.send_chat_action(
        chat_id=callback.message.chat.id,
        action=ChatAction.RECORD_VOICE,
    )
    lock = get_chat_lock(callback.message.chat.id, "youtube")
    async with lock:
        audio_bytes = await text_to_speech(_trim_for_voice(summary))
    
    # Lösche die "Generiere Audio..."-Nachricht
    await processing_message.delete()

    if not audio_bytes:
        await callback.message.answer(
            "Could not generate voice right now. Try again later.",
            reply_markup=yt_read_keyboard(),
        )
        return

    voice_file = BufferedInputFile(audio_bytes, filename="yt_summary.ogg")
    await callback.message.answer_voice(
        voice=voice_file,
        caption="🔊 YouTube summary (audio)",
        reply_markup=yt_after_read_keyboard(),
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
