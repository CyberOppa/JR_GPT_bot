from aiogram.fsm.state import State, StatesGroup

class GptSates(StatesGroup):
    chatting = State()


class TalkStates(StatesGroup):
    choosing_person = State()
    chatting = State()


class QuizStates(StatesGroup):
    choosing_topic = State()
    answering = State()


class RagStates(StatesGroup):
    awaiting_source = State()
    chatting = State()


class YouTubeStates(StatesGroup):
    waiting_url = State()
    choosing_lang = State()