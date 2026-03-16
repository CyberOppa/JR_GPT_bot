from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.inline import (
    main_menu,
    recommendation_actions_keyboard,
    recommendation_categories_keyboard,
)
from services.openai_service import ask_gpt
from states.state import RecommendationStates

router = Router()

CATEGORY_LABELS = {
    "movies": "movies",
    "books": "books",
    "music": "music",
}

RECOMMEND_SYSTEM_PROMPT = (
    "You are a recommendation assistant. "
    "Return exactly this format:\n"
    "Title: <name>\n"
    "Why: <1-3 concise sentences>\n"
    "No extra text."
)


async def _open_recommend_mode(message: Message, state: FSMContext) -> None:
    await state.set_state(RecommendationStates.choosing_genre)
    await state.update_data(
        rec_category=None,
        rec_genre=None,
        rec_disliked=[],
        rec_last_title=None,
    )
    await message.answer(
        "Recommendation mode.\n\nChoose a category:",
        reply_markup=recommendation_categories_keyboard(),
    )


async def _send_recommendation(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    category = data.get("rec_category")
    genre = data.get("rec_genre")
    disliked: list[str] = data.get("rec_disliked", [])

    if category not in CATEGORY_LABELS or not genre:
        await _open_recommend_mode(message, state)
        return

    disliked_block = ", ".join(disliked[-20:]) if disliked else "none"
    prompt = (
        f"Category: {CATEGORY_LABELS[category]}.\n"
        f"Genre: {genre}.\n"
        f"Titles user does not like: {disliked_block}.\n"
        "Suggest one recommendation the user has not rejected yet."
    )

    recommendation = await ask_gpt(
        user_message=prompt,
        system_prompt=RECOMMEND_SYSTEM_PROMPT,
    )
    title = _extract_title(recommendation)
    await state.update_data(rec_last_title=title)

    await message.answer(
        recommendation,
        reply_markup=recommendation_actions_keyboard(),
    )


def _extract_title(recommendation_text: str) -> str:
    for line in recommendation_text.splitlines():
        if line.lower().startswith("title:"):
            return line.split(":", 1)[1].strip()
    first_line = (
        recommendation_text.splitlines()[0]
        if recommendation_text
        else ""
    )
    return first_line.strip()[:80]


@router.message(Command("recommend"))
async def cmd_recommend(message: Message, state: FSMContext):
    await _open_recommend_mode(message, state)


@router.callback_query(F.data == "menu:recommend")
async def on_menu_recommend(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.message:
        await _open_recommend_mode(callback.message, state)


@router.callback_query(
    RecommendationStates.choosing_genre,
    F.data.startswith("rec:cat:"),
)
async def on_category_selected(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split(":")[-1]
    if category not in CATEGORY_LABELS:
        await callback.answer("Unknown category")
        return

    await state.update_data(rec_category=category)
    await callback.answer()

    if callback.message:
        await callback.message.answer(
            f"Category set to {CATEGORY_LABELS[category]}.\n"
            "Now send a genre (for example: sci-fi, thriller, jazz).",
        )


@router.message(RecommendationStates.choosing_genre, F.text)
async def on_genre_received(message: Message, state: FSMContext):
    genre = message.text.strip()
    if len(genre) < 2:
        await message.answer("Send a valid genre text.")
        return

    data = await state.get_data()
    category = data.get("rec_category")
    if category not in CATEGORY_LABELS:
        await message.answer(
            "Choose category first.",
            reply_markup=recommendation_categories_keyboard(),
        )
        return

    await state.update_data(rec_genre=genre)
    await state.set_state(RecommendationStates.browsing)
    await _send_recommendation(message, state)


@router.callback_query(RecommendationStates.browsing, F.data == "rec:another")
async def on_recommend_another(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.message:
        await _send_recommendation(callback.message, state)


@router.callback_query(RecommendationStates.browsing, F.data == "rec:dislike")
async def on_recommend_dislike(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    disliked: list[str] = data.get("rec_disliked", [])
    last_title = data.get("rec_last_title")
    if last_title and last_title not in disliked:
        disliked.append(last_title)
        await state.update_data(rec_disliked=disliked)

    await callback.answer("Will avoid this one")
    if callback.message:
        await _send_recommendation(callback.message, state)


@router.callback_query(F.data == "rec:change")
async def on_recommend_change(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.message:
        await _open_recommend_mode(callback.message, state)


@router.callback_query(F.data == "rec:stop")
async def on_recommend_stop(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            "Recommendation mode ended.",
            reply_markup=main_menu(),
        )
