from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from keyboards.inline import main_menu
from handlers.random_fact import send_random_fact

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = main_menu()
    await message.answer(f"Hello, {message.from_user.first_name}\n\n"
                         "I'm GPT bot. Choose your destiny!\n\n", reply_markup=keyboard, parse_mode="HTML")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        '<b>Commands:</b>\n\n'
        '/start - Main menu\n'
        '/random - Random fact\n'
        '/gpt - Dialog with GPT\n'
        '/talk - Dialog with a person\n'
        '/help - Help\n', parse_mode="HTML"
    )


@router.callback_query(F.data == 'menu:random')
async def on_menu_random(callback: CallbackQuery):
    await callback.answer()     # Buttons flimmern deaktivieren
    await send_random_fact(callback.message)


@router.callback_query(F.data == 'menu:gpt')
async def on_menu_gpt(callback: CallbackQuery):
    await callback.answer()  # Buttons flimmern deaktivieren
    await callback.message.answer('Type /gpt to start ChatGPT')