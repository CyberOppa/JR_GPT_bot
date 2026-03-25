from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from services.openai_service import ask_gpt
from aiogram.enums import ChatAction
from keyboards.inline import cancel_quiz_keyboard

TOPICS = {
    'science': {
        'name': '🔬 Science 🔬',
        'prompt_name': 'science & discovery'
    },
    'history': {
        'name': '🧾 History 🧾',
        'prompt_name': 'history'
    },
    'geography': {
        'name': '🌍 Geography 🌍',
        'prompt_name': 'geography'
    },
    'sport': {
        'name': '⚽ Sport ⚽',
        'prompt_name': 'sport'
    },
    'movies': {
        'name': '🎬 Movies 🎬',
        'prompt_name': 'movies'
    },
    'it': {
        'name': '💻 Technology 💻',
        'prompt_name': 'IT & technology'
    }
}


async def generate_answer(topic_key: str, TOPICS: dict) -> str:
    topic = TOPICS[topic_key]

    prompt = (
        f"Generate a challenging quiz question about {topic['prompt_name']}"
        "The question should be concise and have only one correct answer."
        "write only the question, no explanation, no numerated list, no answer"
    )

    return await ask_gpt(user_message=prompt)


async def check_answer(question: str, user_answer: str) -> tuple[bool, str]:
    """
    Check if the user's answer is correct.
    Return (is_correct: bool, answer)
    :param question:
    :param user_answer:
    :return:
    """

    prompt = (
        f"Question: {question}\n"
        f"User answer: {user_answer}\n"
        "Check the user answer, and reply in this format\n"
        "First line: only Correct or Incorrect\n"
        "Second line: short explanation (1-2 Sentences)\n"
        "If Incorrect, show correct answer"
    )

    response = await ask_gpt(user_message=prompt)

    lines = response.strip().split('\n')
    first_line = lines[0].strip().upper()

    is_correct = first_line.startswith('CORRECT')

    explanation = '\n'.join(lines[1:]).strip()

    if not explanation:
        explanation = 'Correct!' if is_correct else 'Incorrect!'

    return is_correct, explanation


async def send_quiz_question(message: Message, state: FSMContext, topic_key: str):
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action=ChatAction.TYPING
    )

    question = await generate_answer(topic_key=topic_key, TOPICS=TOPICS)

    await state.update_data(current_question=question)

    data = await state.get_data()
    score = data.get('score', 0)
    total = data.get('total', 0)
    topic_name = TOPICS[topic_key]['name']

    await message.answer(
        f'<b>{score}/{total}</b> | Theme {topic_name}\n\n'
        f'<b>Question</b>\n{question}',
        reply_markup=cancel_quiz_keyboard()
    )

