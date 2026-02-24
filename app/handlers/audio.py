import logging
from aiogram import Router, F
from aiogram.types import Message

from app.service import AudioService, UserService
from app.schemas import AudioMessageRequest


router = Router()
logger = logging.getLogger(__name__)


@router.message(F.voice)
async def handle_audio(
    message: Message,
    audio_service: AudioService,
    user_service: UserService,
):
    await message.answer("Принял голосовое, расшифровываю...")

    telegram_id = message.from_user.id
    username = message.from_user.username

    await user_service.create_user(
        telegram_id=telegram_id,
        name=username if username else None,
    )

    try:
        voice_request = AudioMessageRequest(
            file_id=message.voice.file_id,
            duration=message.voice.duration,
            file_size=message.voice.file_size
        )

        result = await audio_service.process_audio_message(
            voice_request,
            user_id=telegram_id
        )

        if result.success and result.text:
            time_info = f"(⏱️ {result.processing_time:.1f}с)" if result.processing_time else ""
            await message.answer(f"📝 {result.text}{time_info}")
        else:
            error_msg = result.error_message or "Не смог ничего разобрать из этого голосового 😔"
            await message.answer(error_msg)

    except ValueError as e:
        logger.warning(f"Ошибка валидации голосового сообщения: {e}")
        await message.answer("Голосовое сообщение не соответствует требованиям (слишком длинное или большое)")