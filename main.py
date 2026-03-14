from aiogram import Bot, Dispatcher
import asyncio
import logging
from config import BOT_TOKEN



async def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s')
    bot = Bot(token=BOT_TOKEN)      # Create a bot instance
    dp = Dispatcher()               # Handeln updates, events
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
