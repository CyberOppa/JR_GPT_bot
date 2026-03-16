from services.openai_service import ask_gpt

QUIZ_QUESTION_SYSTEM_PROMPT = (
    "You are a quiz generator. Create one multiple-choice question with four "
    "options. Return only plain text in this exact format:\n"
    "Question: ...\n"
    "A) ...\n"
    "B) ...\n"
    "C) ...\n"
    "D) ...\n"
    "Do not reveal the correct option."
)

QUIZ_CHECK_SYSTEM_PROMPT = (
    "You are a strict quiz evaluator. "
    "Follow the user's format instructions exactly. "
    "Output only the final answer text, without extra labels."
)


async def generate_question(topic_name: str) -> str:
    return await ask_gpt(
        user_message=f"Topic: {topic_name}. Create one new quiz question now.",
        system_prompt=QUIZ_QUESTION_SYSTEM_PROMPT,
    )


async def check_answer(question: str, user_answer: str) -> str:
    prompt = (
        f"Quiz question {question}\n"
        f"User answer {user_answer}\n\n"
        "Chek the user answer. Make your Answer in this format:\n"
        "Only one word: True or False\n"
        "Under True or False short description 1-3 sentences."
        "If antwort is false, show the right answer"
    )

    return await ask_gpt(
        user_message=prompt,
        system_prompt=QUIZ_CHECK_SYSTEM_PROMPT,
    )
