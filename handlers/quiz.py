import logging

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from keyboards.inline import after_answer_keyboard, main_menu, topics_keyboard
from states.state import QuizStates
from utils.quiz_generate import check_answer, generate_question

router = Router()
logger = logging.getLogger(__name__)

TOPICS: dict[str, dict[str, str]] = {
    "science": {
        "name": "👨‍🎓 Science 👨‍🎓",
        "prompt_name": "Science and discovery",
    },
    "technology": {
        "name": "🔬 Technology 🔬",
        "prompt_name": "Technology",
    },
    "movies": {
        "name": "🎬 Movies 🎬",
        "prompt_name": "Movies",
    },
    "music": {
        "name": "🎵 Music 🎵",
        "prompt_name": "Music",
    },
    "games": {
        "name": "🎮 VideoGames 🎮",
        "prompt_name": "Games",
    },
    "sports": {
        "name": "🏃 Sports 🏃",
        "prompt_name": "Sports",
    },
}


def _extract_topic_key(callback_data: str | None) -> str | None:
    if not callback_data:
        return None
    if callback_data.startswith("quiz:topic:"):
        return callback_data.split(":", 2)[2]
    if callback_data.startswith("quiz:topic"):
        # Backward compatibility for old keyboard format: quiz:topic<key>
        return callback_data.replace("quiz:topic", "", 1)
    return None


async def _send_topic_menu(message: Message, state: FSMContext) -> None:
    await state.set_state(QuizStates.choosing_topic)
    caption = "<b>Quiz</b>\n\nChoose your topic"

    try:
        photo = FSInputFile("images/quiz.png")
        await message.answer_photo(
            photo=photo,
            caption=caption,
            reply_markup=topics_keyboard(topics=TOPICS),
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("Quiz image was not sent")
        await message.answer(
            caption,
            reply_markup=topics_keyboard(topics=TOPICS),
            parse_mode="HTML",
        )


async def _send_next_question(
        message: Message,
        state: FSMContext,
        topic_key: str) -> None:
    topic = TOPICS[topic_key]
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING,
    )

    question = await generate_question(topic['prompt_name'])

    await state.update_data(topic_key=topic_key, last_question=question)
    await message.answer(
        f"{topic['name']}\n\n{question}\n\nSend your answer as text.",
        reply_markup=after_answer_keyboard(),
    )


@router.message(Command("quiz"))
async def cmd_quiz(message: Message, state: FSMContext):
    await _send_topic_menu(message, state)


@router.callback_query(F.data == "quiz")
async def on_menu_quiz(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.message:
        await _send_topic_menu(callback.message, state)


@router.callback_query(QuizStates.choosing_topic,
                       F.data.startswith("quiz:topic"))
async def on_topic_choosen(callback: CallbackQuery, state: FSMContext):
    topic_key = _extract_topic_key(callback.data)
    if topic_key not in TOPICS:
        await callback.answer("Unknown topic")
        return

    await state.set_state(QuizStates.answering)
    await callback.answer()
    if callback.message:
        await _send_next_question(callback.message, state, topic_key)


@router.message(QuizStates.answering, F.text)
async def on_user_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    topic_key = data.get("topic_key")
    last_question = data.get("last_question")

    if topic_key not in TOPICS or not last_question:
        await _send_topic_menu(message, state)
        return

    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING,
    )
    feedback = await check_answer(last_question, message.text)
    await message.answer(feedback, reply_markup=after_answer_keyboard())


@router.callback_query(QuizStates.answering, F.data == "quiz:next")
async def on_next_question(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    topic_key = data.get("topic_key")

    if topic_key not in TOPICS:
        await callback.answer("Choose topic first")
        if callback.message:
            await _send_topic_menu(callback.message, state)
        return

    await callback.answer()
    if callback.message:
        await _send_next_question(callback.message, state, topic_key)


@router.callback_query(F.data == "quiz:change_topic")
async def on_change_topic(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.message:
        await _send_topic_menu(callback.message, state)


@router.callback_query(F.data.in_({"quiz:cancel", "quiz:stop"}))
async def on_quiz_stop(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            "Quiz mode ended.",
            reply_markup=main_menu(),
        )
