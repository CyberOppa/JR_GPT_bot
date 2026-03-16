from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from handlers.random_fact import send_random_fact
from keyboards.inline import main_menu
from utils.telegram_utils import escape_html

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = main_menu()
    user_name = escape_html(message.from_user.first_name or "there")
    await message.answer(
        f"Hello, {user_name}\n\n"
        "I'm GPT bot. Choose your destiny!\n\n",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        '<b>Commands:</b>\n\n'
        '/start - Main menu\n'
        '/random - Random fact\n'
        '/gpt - Dialog with GPT\n'
        '/talk - Dialog with a person\n'
        '/quiz - Quiz mode\n'
        '/rag - Ask your documents\n'
        '/yt - YouTube summary\n'
        '/help - Help\n', parse_mode="HTML"
    )


@router.callback_query(F.data == 'menu:random')
async def on_menu_random(callback: CallbackQuery):
    await callback.answer()
    if callback.message:
        await send_random_fact(callback.message)
