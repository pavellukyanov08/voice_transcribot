from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.core.db import AsyncSessionLocal
from app.core import voice_transcribot
from app.crud import AudioRepository, UserRepository
from app.service import AudioService, UserService


class DependencyMiddleware(BaseMiddleware):
    def __init__(self):
        self.bot = voice_transcribot
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async with AsyncSessionLocal() as session:
            try:
                audio_repo = AudioRepository(session)
                user_repo = UserRepository(session)
                audio_service = AudioService(audio_repo)
                user_service = UserService(user_repo)

                data.update({
                    "audio_service": audio_service,
                    "audio_repo": audio_repo,
                    "user_repo": user_repo,
                    "user_service": user_service,
                    "db_session": session,
                })
                
                return await handler(event, data)

            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error in DependencyMiddleware: {e}")
                raise