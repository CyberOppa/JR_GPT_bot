from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎲 Random Fact 🎲",
                    callback_data="menu:random",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🤖 Chat GPT 🤖",
                    callback_data="menu:gpt",
                )
            ],
            [
                InlineKeyboardButton(
                    text="👩‍🦰 Dialog with a person 👩‍🦰",
                    callback_data="talk",
                )
            ],
            [InlineKeyboardButton(text="❔ Quiz ❔", callback_data="quiz")],
            [
                InlineKeyboardButton(
                    text="🎬 Recommendations 🎬",
                    callback_data="menu:recommend",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📚 Ask Your Docs 📚",
                    callback_data="menu:rag",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎥 YouTube Summary 🎥",
                    callback_data="menu:yt",
                )
            ],
        ]
    )


def random_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🎲 Another random fact 🎲',
                    callback_data='random:again',
                )
            ],
            [
                InlineKeyboardButton(
                    text='🛑 Close 🛑',
                    callback_data='random:stop',
                )
            ]
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
        [
            InlineKeyboardButton(
                text=f'{data["emoji"]} {data["name"]}',
                callback_data=f'talk:person:{key}',
            )
        ]
        for key, data in persons.items()
    ]
    buttons.append(
        [InlineKeyboardButton(text='🛑 Close 🛑', callback_data='talk:stop')]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def talk_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🔄️️ Change person 🔄️',
                    callback_data='talk:change',
                )
            ],
            [InlineKeyboardButton(text='🛑 Close 🛑', callback_data='talk:stop')]
        ]
    )


def topics_keyboard(topics: dict) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=data["name"],
                callback_data=f'quiz:topic:{key}',
            )
        ]
        for key, data in topics.items()
    ]
    buttons.append(
        [InlineKeyboardButton(text='🛑 Close 🛑', callback_data='quiz:cancel')]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def after_answer_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='➡️ Next question ➡️',
                    callback_data='quiz:next',
                )
            ],
            [
                InlineKeyboardButton(
                    text='🔄️ Change topic 🔄️',
                    callback_data='quiz:change_topic',
                )
            ],
            [InlineKeyboardButton(text='🛑 Close 🛑', callback_data='quiz:stop')]
        ]
    )


def recommendation_categories_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🎬 Movies',
                    callback_data='rec:cat:movies',
                ),
                InlineKeyboardButton(
                    text='📚 Books',
                    callback_data='rec:cat:books',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🎵 Music',
                    callback_data='rec:cat:music',
                )
            ],
            [InlineKeyboardButton(text='🛑 Close 🛑', callback_data='rec:stop')],
        ]
    )


def recommendation_actions_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🎲 Another',
                    callback_data='rec:another',
                ),
                InlineKeyboardButton(
                    text='👎 Not interested',
                    callback_data='rec:dislike',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔄 Change category',
                    callback_data='rec:change',
                )
            ],
            [InlineKeyboardButton(text='🛑 Close 🛑', callback_data='rec:stop')],
        ]
    )


def rag_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🧹 Clear source',
                    callback_data='rag:clear',
                ),
                InlineKeyboardButton(
                    text='🔄 New source',
                    callback_data='rag:change',
                ),
            ],
            [InlineKeyboardButton(text='🛑 Close 🛑', callback_data='rag:stop')],
        ]
    )


def yt_length_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='⏱ 2 min',
                    callback_data='yt:length:2',
                ),
                InlineKeyboardButton(
                    text='⏱ 5 min',
                    callback_data='yt:length:5',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔗 New link',
                    callback_data='yt:new',
                )
            ],
            [
                InlineKeyboardButton(
                    text='🛑 Close 🛑',
                    callback_data='yt:cancel',
                )
            ],
        ]
    )
