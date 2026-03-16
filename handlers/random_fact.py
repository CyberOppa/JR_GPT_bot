import logging

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import CallbackQuery, FSInputFile, Message

from keyboards.inline import main_menu, random_keyboard
from services.openai_service import ask_gpt

router = Router()
logger = logging.getLogger(__name__)

FACT_PROMPT = (
    'Let me know a random fact from a different sciences.'
    'Fact must be amazing, new one and not longer then 4 sentences.'
    'You should start directly "Du you know that..."'
)


async def send_random_fact(message: Message):
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING
    )

    fact = await ask_gpt(user_message=FACT_PROMPT)

    try:
        photo = FSInputFile('images/random.png')
        await message.answer_photo(
            photo=photo,
            caption=f'<b>Random fact</b>\n\n{fact}',
            reply_markup=random_keyboard(),
            parse_mode='HTML',
        )
    except Exception:
        logger.exception('Random fact image was not sent')
        await message.answer(
            f'<b>Random fact</b>\n\n{fact}',
            reply_markup=random_keyboard(),
            parse_mode='HTML',
        )


@router.message(Command('random'))
async def cmd_random(message: Message):
    await send_random_fact(message)


@router.callback_query(F.data == 'random:again')
async def cmd_random_again(callback: CallbackQuery):
    await callback.answer()
    if callback.message:
        await send_random_fact(callback.message)


@router.callback_query(F.data == 'random:stop')
async def on_random_stop(callback: CallbackQuery):
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            'Choose your mode.',
            reply_markup=main_menu(),
        )
