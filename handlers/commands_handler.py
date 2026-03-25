from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards.inline import main_menu

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = main_menu()
    await message.answer(f"Hello, {message.from_user.first_name}\n\n"
                         "I'm AI-Powered Chatbot.\nWhat would you like to do?\n\n", reply_markup=keyboard)


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        '<b>Commands:</b>\n\n'
        '/start - Main menu\n'
        '/random - Random fact\n'
        '/gpt - Dialog with GPT\n'
        '/talk - Dialog with a person\n'
        '/quiz - Quiz\n'
        '/help - Help\n'
    )