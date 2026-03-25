import logging

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from keyboards.inline import quiz_keyboard, after_quiz_keyboard, main_menu
from states.state import QuizStates
from utils.quiz_generate import TOPICS
from utils.quiz_generate import check_answer, send_quiz_question

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command('quiz'))
@router.callback_query(F.data == 'quiz')
@router.callback_query(F.data == 'menu:quiz')
async def cmd_quiz(event: Message | CallbackQuery, state: FSMContext):
    await state.set_state(QuizStates.choosing_topic)

    message = event if isinstance(event, Message) else event.message

    try:
        photo = FSInputFile('images/quiz.png')
        await message.answer_photo(photo=photo, caption=(
            '<b>Quiz with ChatGPT</b>\n'
            'Choose your topic'
        ), reply_markup=quiz_keyboard(topics=TOPICS))
    except Exception:
        await message.answer('<b>Quiz with ChatGPT</b>\nChoose your topic',
                             reply_markup=quiz_keyboard(topics=TOPICS))

    if isinstance(event, CallbackQuery):
        await event.answer()


@router.callback_query(QuizStates.choosing_topic, F.data.startswith('quiz:topic:'))
async def on_topic_chosen(callback: CallbackQuery, state: FSMContext):
    topic_key = callback.data.split(':')[-1]
    if topic_key not in TOPICS:
        await callback.answer('Unknown topic')
        return

    topic = TOPICS[topic_key]

    data = await state.get_data()
    score = data.get('score', 0)
    total = data.get('total', 0)

    await state.update_data(
        topic_key=topic_key,
        topic=topic,
        score=score,
        total=total,
        current_question=''
    )

    await state.set_state(QuizStates.answering)

    await callback.answer(f'Starting quiz on {topic["name"]}')

    try:
        if callback.message.caption:
            await callback.message.edit_caption(
                caption=f'<b>{topic["name"]}</b> - great choice!\n\nA question is generated'
            )
        else:
            await callback.message.edit_text(
                text=f'<b>{topic["name"]}</b> - great choice!\n\nA question is generated'
            )
    except Exception:
        await callback.message.answer(f'<b>{topic["name"]}</b> - great choice!\n\nA question is generated')

    await send_quiz_question(callback.message, state, topic_key)


@router.message(QuizStates.answering, F.text)
async def cmd_quiz_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    current_question = data.get('current_question', '')
    score = data.get('score', 0)
    total = data.get('total', 0)

    if not current_question:
        await message.answer("Please start a new quiz.")
        await state.clear()
        return

    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING
    )

    is_correct, explanation = await check_answer(current_question, message.text)

    await state.update_data(score=score + 1 if is_correct else score, total=total + 1, current_question='')

    result_text = "✅ <b>Correct!</b>" if is_correct else "❌ <b>Incorrect!</b>"
    await message.answer(
        f'{result_text}\n\n'
        f'{explanation}\n\n'
        f'Score <b>{score + 1 if is_correct else score}/{total + 1}</b>\n\n',
        reply_markup=after_quiz_keyboard()
    )


@router.callback_query(F.data == 'quiz:next')
async def on_quiz_next(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    topic_key = data.get('topic_key')

    if not topic_key:
        await callback.message.answer("Session expired. Please choose a topic.")
        await state.clear()
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await send_quiz_question(callback.message, state, topic_key)


@router.callback_query(F.data == 'quiz:change_topic')
async def on_quiz_change_topic(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuizStates.choosing_topic)
    await state.update_data(current_question='')

    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        'Choose your topic',
        reply_markup=quiz_keyboard(topics=TOPICS)
    )


@router.callback_query(F.data == 'quiz:stop')
async def on_quiz_stop(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get('score', 0)
    total = data.get('total', 0)

    await state.clear()
    await callback.answer('Quiz stopped')
    await callback.message.edit_reply_markup(reply_markup=None)

    if score == 0 and total == 0:
        verdict = "You don't answered any question"
    elif score == total:
        verdict = "Bravo! You answered all questions correctly"
    elif score / total >= 0.75:
        verdict = f"Great result! You answered {score} of {total} questions correctly"
    elif score / total >= 0.4:
        verdict = f"Not bad! You answered {score} of {total} questions correctly"
    else:
        verdict = f"You must learn more! You answered {score} of {total} questions correctly"

    await callback.message.answer(
        f'Quiz ended\n\n'
        f'Score <b>{score}/{total}</b>\n\n'
        f'{verdict}',
        reply_markup=main_menu()
    )


@router.callback_query(F.data == 'quiz:cancel')
async def on_quiz_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()

    try:
        if callback.message.caption:
            await callback.message.edit_caption(caption='Quiz canceled', reply_markup=main_menu())
        else:
            await callback.message.edit_text(text='Quiz canceled', reply_markup=main_menu())
    except Exception:
        await callback.message.answer(text='Quiz canceled', reply_markup=main_menu())
