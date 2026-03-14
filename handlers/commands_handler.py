from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from keyboards.inline import main_menu

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = main_menu()
    await message.answer("What would you like to do?", reply_markup=keyboard)