from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎲 Random Fact 🎲", callback_data="menu:random")],
            [InlineKeyboardButton(text="🤖 Chat GPT 🤖", callback_data="menu:gpt")],
            [InlineKeyboardButton(text="👩‍🦰 Dialog with a person 👩‍🦰", callback_data="talk")],
            [InlineKeyboardButton(text="❔ Quiz ❔", callback_data="quiz")]
        ]
    )


def random_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🎲 Another random fact 🎲', callback_data='random:again')],
            [InlineKeyboardButton(text='🛑 Close 🛑', callback_data='random:stop')]
        ]
    )


def gpt_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🛑 Close 🛑', callback_data='gpt:stop')]
        ]
    )


def person_keyboard(persons: dict):
    buttons = [
        [InlineKeyboardButton(text=f'{data["emoji"]} {data["name"]}', callback_data=f'talk:person:{key}')]
        for key, data in persons.items()
    ]
    buttons.append(
        [InlineKeyboardButton(text='🛑 Close 🛑', callback_data='talk:stop')]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def talk_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🔄️️ Change person 🔄️', callback_data='talk:change')],
            [InlineKeyboardButton(text='🛑 Close 🛑', callback_data='talk:stop')]
        ]
    )
