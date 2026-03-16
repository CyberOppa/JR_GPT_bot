import logging

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from keyboards.inline import gpt_keyboard, main_menu
from services.openai_service import ask_gpt
from states.state import GptStates


router = Router()
logger = logging.getLogger(__name__)

GPT_SYSTEM_PROMPT = (
    'You are a scientific expert in all areas of science.'
    'Answer my questions briefly but clearly, including important '
    'details for understanding.'
    'Your answer should be in the same language as the question.'
)


@router.message(Command('gpt'))
async def cmd_gpt(message: Message, state: FSMContext):
    await state.set_state(GptStates.chatting)
    await state.update_data(history=[])

    try:
        photo = FSInputFile('images/gpt.jpg')
        await message.answer_photo(
            photo=photo,
            caption=(
                '<b>Chat GPT</b>\n\n'
                'Type any Questions\n'
                'Context dialogue is retained\n'
                'Push <b>Close</b> to quit'
            ),
            reply_markup=gpt_keyboard(),
            parse_mode='HTML',
        )
    except Exception:
        logger.exception("GPT image was not sent")
        await message.answer(
            '<b>Chat GPT</b>\n\n'
            'Type any Questions\n'
            'Context dialogue is retained\n'
            'Push <b>Close</b> to quit',
            reply_markup=gpt_keyboard(),
            parse_mode='HTML',
        )


@router.callback_query(F.data == 'menu:gpt')
async def on_menu_gpt(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.message:
        await cmd_gpt(callback.message, state)


@router.message(GptStates.chatting, F.text)
async def cmd_gpt_message(message: Message, state: FSMContext):
    data = await state.get_data()
    history = data.get('history', [])

    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING
    )

    history.append({'role': 'user', 'content': message.text})

    response = await ask_gpt(
        user_message=message.text,
        system_prompt=GPT_SYSTEM_PROMPT,
        history=history[:-1]
    )

    history.append({'role': 'assistant', 'content': response})
    await state.update_data(history=history)

    if len(history) > 20:
        history = history[-20:]
        await state.update_data(history=history)
        await message.answer(response, reply_markup=gpt_keyboard())
    else:
        await message.answer(response, reply_markup=gpt_keyboard())


@router.callback_query(F.data == 'gpt:stop')
async def on_gpt_stop(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer('Quit GPT mode')

    if callback.message:
        user_name = callback.from_user.first_name or "there"
        await callback.message.answer(
            f"Hello, {user_name}\n\n"
            "I'm GPT bot. Choose your destiny!\n\n",
            reply_markup=main_menu(),
        )
