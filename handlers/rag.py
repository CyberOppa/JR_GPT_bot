import io
import logging
from pathlib import Path

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from pypdf import PdfReader

from keyboards.inline import main_menu, rag_keyboard
from services.openai_service import ask_gpt
from states.state import RagStates
from utils.rag_tools import select_relevant_chunks, split_text_into_chunks
from utils.youtube_tools import extract_first_url, extract_youtube_video_id
from utils.youtube_tools import fetch_youtube_transcript

router = Router()
logger = logging.getLogger(__name__)

RAG_SYSTEM_PROMPT = (
    "You are a retrieval assistant. "
    "Use ONLY the provided context to answer the user's question. "
    "If the answer is not in context, say it clearly. "
    "Answer briefly and clearly."
)


async def _open_rag_mode(message: Message, state: FSMContext) -> None:
    await state.set_state(RagStates.awaiting_source)
    await state.update_data(rag_source_name=None, rag_source_chunks=[])
    await message.answer(
        "RAG mode is active.\n\n"
        "Send one source first:\n"
        "- upload .txt/.md/.pdf file\n"
        "- paste plain text\n"
        "- send YouTube link\n\n"
        "After source is loaded, send questions.",
        reply_markup=rag_keyboard(),
    )


async def _set_source(
    message: Message,
    state: FSMContext,
    source_name: str,
    source_text: str,
) -> None:
    chunks = split_text_into_chunks(source_text)
    if not chunks:
        await message.answer("No readable text was found in that source.")
        return

    await state.update_data(
        rag_source_name=source_name,
        rag_source_chunks=chunks,
    )
    await state.set_state(RagStates.chatting)
    await message.answer(
        f"Source loaded: {source_name}\n"
        f"Chunks: {len(chunks)}\n\n"
        "Now send your question.",
        reply_markup=rag_keyboard(),
    )


async def _extract_text_from_document(
    message: Message,
) -> tuple[str, str] | None:
    if not message.document:
        return None

    document = message.document
    file_name = document.file_name or "document"
    ext = Path(file_name).suffix.lower()

    buffer = io.BytesIO()
    await message.bot.download(document, destination=buffer)
    data = buffer.getvalue()

    if ext in {".txt", ".md", ".csv", ".json", ".log", ".py"}:
        return file_name, _decode_text_bytes(data)

    if ext == ".pdf":
        pdf_reader = PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in pdf_reader.pages]
        return file_name, "\n".join(pages).strip()

    return None


def _decode_text_bytes(data: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1251", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="ignore")


async def _answer_with_rag(message: Message, state: FSMContext) -> None:
    question = message.text.strip()
    data = await state.get_data()
    chunks: list[str] = data.get("rag_source_chunks", [])
    source_name = data.get("rag_source_name", "source")

    if not chunks:
        await _open_rag_mode(message, state)
        return

    relevant = select_relevant_chunks(chunks, question, top_k=4)
    context = "\n\n---\n\n".join(relevant)

    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING,
    )

    response = await ask_gpt(
        user_message=(
            f"Source name: {source_name}\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}"
        ),
        system_prompt=RAG_SYSTEM_PROMPT,
    )
    await message.answer(response, reply_markup=rag_keyboard())


@router.message(Command("rag"))
async def cmd_rag(message: Message, state: FSMContext):
    await _open_rag_mode(message, state)


@router.callback_query(F.data == "menu:rag")
async def on_menu_rag(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.message:
        await _open_rag_mode(callback.message, state)


@router.message(RagStates.awaiting_source, F.document)
async def on_rag_document(message: Message, state: FSMContext):
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING,
    )
    parsed = await _extract_text_from_document(message)
    if not parsed:
        await message.answer(
            "Unsupported file type. Please upload .txt/.md/.pdf"
        )
        return

    source_name, source_text = parsed
    await _set_source(message, state, source_name, source_text)


@router.message(RagStates.awaiting_source, F.text)
async def on_rag_source_text(message: Message, state: FSMContext):
    text = message.text.strip()
    url = extract_first_url(text)
    video_id = extract_youtube_video_id(url) if url else None

    if video_id:
        await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action=ChatAction.TYPING,
        )
        try:
            transcript = await fetch_youtube_transcript(video_id)
        except Exception:
            logger.exception("Failed to fetch YouTube transcript in RAG mode")
            await message.answer(
                "Could not load transcript for this YouTube video."
            )
            return

        await _set_source(
            message,
            state,
            source_name=f"YouTube:{video_id}",
            source_text=transcript,
        )
        return

    if len(text) < 30:
        await message.answer("Send more source text or upload a file.")
        return

    await _set_source(
        message,
        state,
        source_name="Pasted text",
        source_text=text,
    )


@router.message(RagStates.chatting, F.text)
async def on_rag_question(message: Message, state: FSMContext):
    await _answer_with_rag(message, state)


@router.callback_query(F.data == "rag:change")
async def on_rag_change_source(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.message:
        await _open_rag_mode(callback.message, state)


@router.callback_query(F.data == "rag:clear")
async def on_rag_clear_source(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RagStates.awaiting_source)
    await state.update_data(rag_source_name=None, rag_source_chunks=[])
    await callback.answer("Source cleared")
    if callback.message:
        await callback.message.answer(
            "Source cleared. Send a new file/text/link.",
            reply_markup=rag_keyboard(),
        )


@router.callback_query(F.data == "rag:stop")
async def on_rag_stop(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            "RAG mode ended.",
            reply_markup=main_menu(),
        )
