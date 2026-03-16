from aiogram.fsm.state import State, StatesGroup


class GptStates(StatesGroup):
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
    choosing_length = State()


# Backward compatible alias for old typo.
GptSates = GptStates
