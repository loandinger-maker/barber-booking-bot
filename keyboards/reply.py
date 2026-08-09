from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config import ADMIN_ID


def get_main_keyboard(user_id: int):

    keyboard = [
        [
            KeyboardButton(text="📅 Записатися")
        ],
        [
            KeyboardButton(text="📖 Мої записи")
        ],
        [
            KeyboardButton(text="❓ Допомога")
        ]
    ]

    if str(user_id) == str(ADMIN_ID):
        keyboard.append(
            [
                KeyboardButton(text="👨‍💼 Адмін-панель")
            ]
        )

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Оберіть дію..."
    )