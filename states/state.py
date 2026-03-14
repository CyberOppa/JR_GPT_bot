from aiogram.fsm.state import State, StatesGroup

class GptSates(StatesGroup):
    chatting = State()


class TalkStates(StatesGroup):
    choosing_person = State()
    chatting = State()
