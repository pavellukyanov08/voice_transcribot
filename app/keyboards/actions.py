from typing import Iterable
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton
)

def record_actions(records: Iterable[RecordRead]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for record in records:
        record_id = record.id
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit:{record_id}"),
            InlineKeyboardButton(text="⏰ Перенести", callback_data=f"move:{record_id}"),
            InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete:{record_id}")
        ])
    return keyboard