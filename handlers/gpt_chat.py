import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from keyboards.inline import gpt_keyboard, main_menu
from states.state import GptSates
from aiogram.enums import ChatAction
from services.openai_service import ask_gpt


router = Router()
logger = logging.getLogger(__name__)

GPT_SYSTEM_PROMPT = (
    'You are a scientific expert in all areas of science.'
    'Answer my questions briefly but clearly, including important details for understanding.'
    'Your answer should be in the same language as the question.'
)


async def _start_gpt_ui(message: Message, state: FSMContext):
    """Minimal helper to open GPT chat UI and set FSM state."""
    await state.set_state(GptSates.chatting)
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
            parse_mode='HTML'
        )
    except Exception:
        await message.answer(
            '<b>Chat GPT</b>\n\n'
            'Type any Questions\n'
            'Context dialogue is retained\n'
            'Push <b>Close</b> to quit',
            reply_markup=gpt_keyboard(),
            parse_mode='HTML'
        )


@router.message(Command('gpt'))
async def cmd_gpt(message: Message, state: FSMContext):
    await _start_gpt_ui(message, state)


@router.callback_query(F.data == 'menu:gpt')
async def on_menu_gpt(callback: CallbackQuery, state: FSMContext):
    # Stop button flash
    await callback.answer()
    # Prefer calling the existing /gpt handler so the command flow is identical
    if callback.message:
        # Re-use the same Message object and call the command handler directly
        await cmd_gpt(callback.message, state)
        return

    # Fallback: if there's no associated message, create the UI and set FSM
    await state.set_state(GptSates.chatting)
    await state.update_data(history=[])

    try:
        photo = FSInputFile('images/gpt.jpg')
        await callback.bot.send_photo(
            chat_id=callback.from_user.id,
            photo=photo,
            caption=(
                '<b>Chat GPT</b>\n\n'
                'Type any Questions\n'
                'Context dialogue is retained\n'
                'Push <b>Close</b> to quit'
            ),
            reply_markup=gpt_keyboard(),
            parse_mode='HTML'
        )
    except Exception:
        await callback.bot.send_message(
            chat_id=callback.from_user.id,
            text=(
                '<b>Chat GPT</b>\n\n'
                'Type any Questions\n'
                'Context dialogue is retained\n'
                'Push <b>Close</b> to quit'
            ),
            reply_markup=gpt_keyboard(),
            parse_mode='HTML'
        )


@router.message(GptSates.chatting, F.text)
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

    try:
        await callback.message.edit_caption(caption='GPT mode ends')
    except Exception:
        await callback.message.edit_text(text='GPT mode ends')