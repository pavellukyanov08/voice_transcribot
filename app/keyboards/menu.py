from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)


def main_menu_reply() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Создать напоминание")],
            [KeyboardButton(text="📋 Мои записи")],
            [KeyboardButton(text="👤 Профиль")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
