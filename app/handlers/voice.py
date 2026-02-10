import logging
from aiogram import Router, F
from aiogram.types import Message

from app.service import MessageService, UserService
from app.schemas import VoiceMessageRequest


router = Router()
logger = logging.getLogger(__name__)


@router.message(F.voice)
async def handle_voice(
    message: Message,
    message_service: MessageService,
    user_service: UserService,
):
    """Обработчик голосовых сообщений"""
    await message.answer("Принял голосовое, расшифровываю...")

    telegram_id = message.from_user.id
    user_tg_name = message.from_user.username

    current_user = await user_service.get_user(telegram_id=telegram_id)
    if not current_user:
        await user_service.create_user(
            telegram_id=telegram_id,
            name=user_tg_name if user_tg_name else None,
        )

    try:
        voice_request = VoiceMessageRequest(
            file_id=message.voice.file_id,
            duration=message.voice.duration,
            file_size=message.voice.file_size
        )
        
        result = await message_service.process_voice_message(
            voice_request, 
            user_id=message.from_user.id
        )
        
        if result.success and result.text:
            time_info = f" (⏱️ {result.processing_time:.1f}с)" if result.processing_time else ""
            await message.answer(f"📝 {result.text}{time_info}")
        else:
            error_msg = result.error_message or "Не смог ничего разобрать из этого голосового 😔"
            await message.answer(error_msg)
            
    except ValueError as e:
        # Ошибки валидации Pydantic
        logger.warning(f"Ошибка валидации голосового сообщения: {e}")
        await message.answer("Голосовое сообщение не соответствует требованиям (слишком длинное или большое)")
        
    except Exception as e:
        logger.exception("Неожиданная ошибка при обработке голосового сообщения")
        await message.answer("Произошла ошибка при распознавании речи. Попробуйте еще раз.")