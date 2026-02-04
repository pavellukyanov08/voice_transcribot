from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.core.db import AsyncSessionLocal
from app.core import voice_transcribot
from app.crud import MessageRepository, UserRepository
from app.service import MessageService, UserService


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
                message_repo = MessageRepository(session)
                user_repo = UserRepository(session)
                message_service = MessageService(message_repo)
                user_service = UserService(user_repo)

                data.update({
                    "message_service": message_service,
                    "message_repo": message_repo,
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