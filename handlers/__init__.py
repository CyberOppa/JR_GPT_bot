from aiogram import Router
from handlers.commands_handler import router as commands_router
from handlers.random_fact import router as random_fact_router
from handlers.gpt_chat import router as gpt_chat_router
from handlers.talk import router as talk_router
from handlers.quiz import router as quiz_router
from handlers.rag import router as rag_router
from handlers.youtube_summary import router as youtube_router


router = Router()

router.include_routers(
    commands_router,
    random_fact_router,
    gpt_chat_router,
    talk_router,
    quiz_router,
    rag_router,
    youtube_router,
)
