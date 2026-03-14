from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎲 Random Fact 🎲", callback_data="menu:random_fact")],
            [InlineKeyboardButton(text="🤖 Chat GPT 🤖", callback_data="menu:gpt")],
            [InlineKeyboardButton(text="👩‍🦰 Dialog with a person 👩‍🦰", callback_data="talk")],
            [InlineKeyboardButton(text="❔ Quiz ❔", callback_data="quiz")]
        ]
    )
    return keyboard