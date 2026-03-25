import dotenv
import os
import logging

dotenv.load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


if not BOT_TOKEN:
    logging.error("BOT_TOKEN not set. Create a .env with BOT_TOKEN=your_telegram_bot_token")
    raise RuntimeError("BOT_TOKEN not set. See README.md and create a .env file")

if not OPENAI_API_KEY:
    logging.error("OPENAI_API_KEY not set. Create a .env with OPENAI_API_KEY=your_openai_api_key")
    raise RuntimeError("OPENAI_API_KEY not set. See README.md and create a .env file")