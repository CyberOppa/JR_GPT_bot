from aiogram import Router
from handlers.commands_handler import router as commands_router

router = Router()

router.include_router(commands_router)