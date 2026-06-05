import logging
from pathlib import Path
from aiogram import Bot

from app.core import settings
from app.core.generator import BaseTextGenerator
from app.schemas import (
    MessageProcessingResult,
    UserRequestText,
    MessageResult
)
from app.crud import MessageRepository


logger = logging.getLogger(__name__)


class TextService:
    def __init__(
        self,
        bot: Bot,
        message_repo: MessageRepository,
        text_service: BaseTextGenerator
    ):
        self._bot = bot
        self._message_repo = message_repo
        self._text_service = text_service
        self._audio_dir = Path(settings.AUDIO_DIR)

    async def process_text(
        self,
        text_request: UserRequestText,
        user_id: int,
    ) -> MessageProcessingResult:
        content = text_request.text
        try:
            result = await self._text_service.process_text(
                content=content
            )
            if not result:
                return MessageProcessingResult(
                    success=False,
                    error_message="Не удалось сгенерировать ответ"
                )

            saved = await self._save_request_text_to_db(
                text=text_request.text,
                user_id=user_id,
            )

            return MessageProcessingResult(
                success=True,
                generated_text=result,
                saved_to_db=saved,
            )
        except Exception as e:
            logger.exception("Ошибка при генерации ответа =%s", e)
            return MessageProcessingResult(
                success=False,
                error_message=f"Внутренняя ошибка: {str(e)}",
            )

    async def _save_request_text_to_db(
        self,
        text: str,
        user_id: int,
    ) -> bool:
        try:
            message_data = MessageResult(
                text=text,
                user_id=user_id
            )
            await self._message_repo.create_message(message_data=message_data)
            logger.info(f"Сгенерированный сохранена в БД для пользователя {user_id}")
            return True
        except Exception as e:
            logger.exception("Ошибка при сохранении транскрипции в БД =%s", e)
            return False
