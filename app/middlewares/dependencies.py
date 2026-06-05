import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.core.db import AsyncSessionLocal
from app.core import transcribot, settings
from app.core.transcriber import BaseSTTTranscriber
from app.core.generator import BaseTextGenerator
from app.crud import MessageRepository, UserRepository
from app.service import AudioService, UserService, TextService
from app.api import OpenRouterClient

logger = logging.getLogger(__name__)


class DependencyMiddleware(BaseMiddleware):
    def __init__(self, stt_transcriber: BaseSTTTranscriber, text_generator: BaseTextGenerator):
        self.stt_transcriber = stt_transcriber
        self.text_generator = text_generator
        self.openrouter_client = OpenRouterClient(api_key=settings.OPEN_ROUTER_API_KEY)

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        async with AsyncSessionLocal() as session:
            message_repo = MessageRepository(session)
            user_repo = UserRepository(session)
            audio_service = AudioService(transcribot, message_repo, self.stt_transcriber)
            text_service = TextService(transcribot, message_repo, self.text_generator)
            user_service = UserService(user_repo)

            data.update({
                "audio_service": audio_service,
                "text_service": text_service,
                "user_service": user_service,
                "openrouter_client": self.openrouter_client,
            })
            return await handler(event, data)
