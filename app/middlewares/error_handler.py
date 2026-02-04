import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message


logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseMiddleware):
    """Middleware для централизованной обработки ошибок"""
    
    def __init__(self):
        self.logger = logger

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            self.logger.exception("Необработанная ошибка в обработчике")
            
            if isinstance(event, Message):
                try:
                    await event.answer(
                        "Произошла неожиданная ошибка. Попробуйте еще раз или обратитесь к администратору."
                    )
                except Exception:
                    self.logger.exception("Не удалось отправить сообщение об ошибке пользователю")
            
            return None