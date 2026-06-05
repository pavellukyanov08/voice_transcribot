import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.core.db import AsyncSessionLocal
from app.core import transcribot, settings
from app.core.transcriber import BaseSTTTranscriber
from app.crud import MessageRepository, UserRepository
from app.service import AudioService, UserService
from app.api import OpenRouterClient

logger = logging.getLogger(__name__)


class DependencyMiddleware(BaseMiddleware):
    def __init__(self, stt_service: BaseSTTTranscriber):
        self.stt_service = stt_service
        self.openrouter_client = OpenRouterClient(api_key=settings.OPEN_ROUTER_API_KEY)

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        async with AsyncSessionLocal() as session:
            audio_repo = MessageRepository(session)
            user_repo = UserRepository(session)
            audio_service = AudioService(transcribot, audio_repo, self.stt_service)
            user_service = UserService(user_repo)

            data.update({
                "audio_service": audio_service,
                "user_service": user_service,
                "openrouter_client": self.openrouter_client,
            })
            return await handler(event, data)
