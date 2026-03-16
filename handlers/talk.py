import logging

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from keyboards.inline import main_menu, person_keyboard, talk_keyboard
from services.openai_service import ask_gpt
from states.state import TalkStates
from utils.chat_locks import get_chat_lock
from utils.rate_limit import get_retry_after
from utils.telegram_utils import answer_long_text, escape_html


router = Router()
logger = logging.getLogger(__name__)


PERSONS = {
    'Pushkin': {
        'name': 'Александр Сергеевич Пушкин',
        'emoji': '🪶',
        'prompt': (
            "Ты, Александр Сергеевич Пушкин, "
            "известный русский поэт конца 19-го века. "
            "Говори изысканно, используй русский язык "
            "на подобающем уровне. "
            "Вставляй стихи oder прозу в свою речь. "
            "Говори исключительно на русском языке"
        )
    },
    'musk': {
        'name': 'Elon Musk',
        'emoji': '🚀',
        'prompt': (
            "You are Elon Musk in real-time conversation."
            "Respond exactly like Elon: concise, witty, sarcastic humor, "
            "memes/emojis (🚀😂🐶). "
            "Use casual slang (dude, bro, btw, lol), bold vision on "
            "Mars/Tesla/xAI/AI/free speech, zero fluff, occasional typos. "
            "Use current real knowledge, tweet-style brevity. "
            "Never break character or say you're AI. "
            "Start every reply as Elon would text. "
            "Talk only in English language"
        )
    },
    'jobs': {
        'name': 'Steve Jobs',
        'emoji': '💼',
        'prompt': (
            "You are Steve Jobs in real-time conversation."
            "Respond exactly like Steve: minimalist, intense, visionary, "
            "direct and sometimes abrasive; short powerful sentences, "
            "zero fluff, perfectionist tone. "
            "Focus on design, simplicity, innovation, Apple, user "
            "experience with phrases like “insanely great” and "
            "“think different.” "
            "Use knowledge from his life and speeches. "
            "Never break character or say you're AI. "
            "Start every reply as Steve would text. "
            "Talk only in Englisch language"
        )
    },
    'einstein': {
        'name': 'Albert Einstein',
        'emoji': '🧠',
        'prompt': (
            "Du bist Albert Einstein in einem Echtzeit-Gespräch."
            "Antworte genau wie Einstein: tiefgründige, aber bescheidene "
            "Weisheit, sanfter witziger Humor, einfache Analogien für "
            "komplexe Ideen, endlose Neugier auf Universum/Wissenschaft/"
            "Vorstellungskraft/Frieden. "
            "Verwende Phrasen wie „Imagination ist wichtiger als Wissen“ "
            "oder Gedankenexperimente. "
            "Nachdenklicher, gelassener Ton mit gelegentlichem deutschen "
            "Flair (z. B. „Ja, mein Freund“). "
            "Breche niemals den Charakter oder sage, dass du KI bist. "
            "Starte jede Antwort so, wie Einstein texten würde. "
            "Antworte nur auf Deutsch"
        )
    }
}


@router.message(Command('talk'))
@router.callback_query(F.data == 'talk')
async def cmd_talk(event: Message | CallbackQuery, state: FSMContext):
    await state.set_state(TalkStates.choosing_person)

    message = event if isinstance(event, Message) else event.message
    if message is None:
        if isinstance(event, CallbackQuery):
            await event.answer("Can't open chat from this update")
        return

    try:
        photo = FSInputFile('images/talk.jpg')
        await message.answer_photo(
            photo=photo,
            caption='<b>Dialog with a person</b>\n\nChoose your Speaker:',
            reply_markup=person_keyboard(PERSONS),
            parse_mode='HTML',
        )
    except Exception:
        logger.exception("Talk image was not sent")
        await message.answer(
            text='<b>Dialog with a person</b>\n\nChoose your Speaker:',
            reply_markup=person_keyboard(PERSONS),
            parse_mode='HTML',
        )

    if isinstance(event, CallbackQuery):
        await event.answer()


@router.callback_query(TalkStates.choosing_person,
                       F.data.startswith('talk:person:'))
async def on_person_choosen(callback: CallbackQuery, state: FSMContext):
    person_key = callback.data.split(':')[-1]

    if person_key not in PERSONS:
        await callback.answer('Unknown person')
        return

    person = PERSONS[person_key]

    await state.update_data(person_key=person_key, history=[])
    await state.set_state(TalkStates.chatting)

    await callback.answer(f'Starting conversation with {person["name"]}')

    if callback.message is None:
        return

    await callback.message.edit_caption(
        caption=(
            f'{person["emoji"]} <b>You speaks with '
            f'{escape_html(person["name"])}</b>\n\n'
            'Type any Questions\n'
        ),
        reply_markup=talk_keyboard(),
        parse_mode='HTML',
    )


@router.message(TalkStates.chatting, F.text)
async def cmd_talk_message(message: Message, state: FSMContext):
    user_id = message.from_user.id if message.from_user else 0
    retry_after = get_retry_after(
        user_id=user_id,
        scope="talk_chat",
        limit=8,
        window_seconds=60,
    )
    if retry_after:
        await message.answer(
            f"Too many requests. Try again in {retry_after}s.",
            reply_markup=talk_keyboard(),
        )
        return

    user_text = (message.text or "").strip()
    if not user_text:
        await message.answer(
            'Send a text message.',
            reply_markup=talk_keyboard(),
        )
        return

    lock = get_chat_lock(message.chat.id, "talk")
    async with lock:
        data = await state.get_data()
        person_key = data.get('person_key')
        history = data.get('history', [])

        if person_key not in PERSONS:
            await message.answer('Unknown person')
            await state.clear()
            return

        person = PERSONS[person_key]
        await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action=ChatAction.TYPING
        )

        response = await ask_gpt(
            user_message=user_text,
            system_prompt=person['prompt'],
            history=history,
        )

        history.append({'role': 'user', 'content': user_text})
        history.append({'role': 'assistant', 'content': response})

        if len(history) > 16:
            history = history[-16:]

        await state.update_data(history=history)

    await answer_long_text(
        message,
        f'{person["emoji"]} {person["name"]}\n\n{response}',
        reply_markup=talk_keyboard(),
    )


@router.callback_query(F.data == 'talk:stop')
async def stop_talk(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if callback.message:
        await callback.message.answer(
            'Conversation ended.',
            reply_markup=main_menu(),
        )
    await callback.answer()


@router.callback_query(F.data == 'talk:change')
async def change_person(callback: CallbackQuery, state: FSMContext):
    await cmd_talk(callback, state)
