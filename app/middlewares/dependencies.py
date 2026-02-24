import logging
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.core.db import AsyncSessionLocal
from app.core import transcribot
from app.core.transcriber import BaseSTTTranscriber
from app.crud import AudioRepository, UserRepository
from app.service import AudioService, UserService


logger = logging.getLogger(__name__)


class DependencyMiddleware(BaseMiddleware):
    def __init__(self, stt_service: BaseSTTTranscriber):
        self.stt_service = stt_service

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with AsyncSessionLocal() as session:
            audio_repo = AudioRepository(session)
            user_repo = UserRepository(session)
            audio_service = AudioService(transcribot, audio_repo, self.stt_service)
            user_service = UserService(user_repo)
            data.update({
                "audio_service": audio_service,
                "user_service": user_service,
            })
            return await handler(event, data)
