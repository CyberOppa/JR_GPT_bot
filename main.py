import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from handlers import router


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        stream=sys.stdout,
        force=True,
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting bot")

    dp = Dispatcher()
    dp.include_router(router)

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode='HTML')
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped manually")
