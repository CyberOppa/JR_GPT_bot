import asyncio

from openai import AsyncOpenAI
from config import OPENAI_API_KEY
import logging

client = AsyncOpenAI(api_key=OPENAI_API_KEY)
MODEL="gpt-4o-mini"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def ask_gpt(
        user_message: str,
        system_prompt: str = 'You are a helpful scientist-expert assistant. Answer me short and concisely',
        history: list = None
) -> str:
    try:
        messages = [{'role': 'system', 'content': system_prompt}]
        if history:
            messages.extend(history)
        messages.append({'role': 'user', 'content': user_message})
        logger.info(f'GPT messages: {messages[:20]}')

        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1000,
            temperature=0.8
        )
        answer = response.choices[0].message.content
        logger.info(f'GPT answer: {len(answer)} symbols')
        return answer
    except Exception as e:
        logger.error(f'GPT error: {e}')
        return 'Error: try again later'


async def main():
    answer = await ask_gpt(user_message='Hello')
    print(answer)


asyncio.run(main())
