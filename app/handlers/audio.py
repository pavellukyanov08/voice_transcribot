import logging
import tempfile

from aiogram import Router, F
from aiogram.types import Message

from app.core import settings
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


@router.message(F.video_note)
async def handle_video_note(
    message: Message,
    audio_service: AudioService,
    user_service: UserService,
):
    await message.answer("Принял кружок, расшифровываю...")

    telegram_id = message.from_user.id
    username = message.from_user.username

    await user_service.create_user(
        telegram_id=telegram_id,
        name=username if username else None,
    )

    try:
        video_request = AudioMessageRequest(
            file_id=message.video_note.file_id,
            duration=message.video_note.duration,
            file_size=message.video_note.file_size
        )

        result = await audio_service.process_audio_message(
            video_request,
            user_id=telegram_id
        )

        if result.success and result.text:
            time_info = f"(⏱️ {result.processing_time:.1f}с)" if result.processing_time else ""
            await message.answer(f"📝 {result.text}{time_info}")
        else:
            error_msg = result.error_message or "Не смог ничего разобрать из этого кружка 😔"
            await message.answer(error_msg)

    except ValueError as e:
        logger.warning(f"Ошибка валидации кружка: {e}")
        await message.answer("Кружок не соответствует требованиям (слишком длинное или большое)")


@router.message(F.document)
async def handle_file(
    message: Message,
    audio_service: AudioService,
):
    telegram_id = message.from_user.id
    doc = message.document
    mime = doc.mime_type or ''

    await message.answer("Принял файл, расшифровываю...")

    try:
        file_request = AudioMessageRequest(
            file_id=message.document.file_id,
            file_size=message.document.file_size,
            mime_type=mime,
        )

        result = await audio_service.process_video(
            file_request,
            user_id=telegram_id
        )

        if result.success and result.text:
            time_info = f"(⏱️ {result.processing_time:.1f}с)" if result.processing_time else ""
            await message.answer(f"📝 {result.text}{time_info}")
        else:
            error_msg = result.error_message or "Не смог ничего разобрать из этого файла 😔"
            await message.answer(error_msg)

    except ValueError as e:
        logger.warning(f"Ошибка валидации файла: {e}")
        await message.answer("Файл не соответствует требованиям")

