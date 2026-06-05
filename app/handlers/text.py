import logging
from aiogram import Router, F
from aiogram.types import Message

from app.service import UserService, TextService
from app.schemas import UserRequestText


router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == '/request')
async def handle_request(
    message: Message,
    text_service: TextService,
    user_service: UserService,
):
    await message.answer("Пришли мне запрос")

    telegram_id = message.from_user.id
    username = message.from_user.username

    await user_service.create_user(
        telegram_id=telegram_id,
        name=username if username else None,
    )

    text_request = UserRequestText(
        text=message.text,
    )
    try:
        result = await text_service.process_text(
            text_request=text_request,
            user_id=telegram_id
        )

        if result.success and result.generated_text:
            await message.answer(f"📝 {result.generated_text}")
        else:
            error_msg = result.error_message or "Ошибка генерации текста 😔"
            await message.answer(error_msg)

    except ValueError as e:
        logger.warning(f"Ошибка генерации текста: {e}")
        # await message.answer("Голосовое сообщение не соответствует требованиям (слишком длинное или большое)")