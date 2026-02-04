import asyncio
import logging
from aiogram import Dispatcher

from .middlewares import (
    DependencyMiddleware,
    ErrorHandlerMiddleware
)
from .core.bot import voice_transcribot
from .handlers import start, voice
from .utils import setup_logging


dp = Dispatcher()

setup_logging()
logger = logging.getLogger(__name__)

dp.message.middleware(DependencyMiddleware())
dp.message.middleware(ErrorHandlerMiddleware())

dp.include_router(start.router)
dp.include_router(voice.router)




async def main():
    logger.info("Бот запущен")
    await dp.start_polling(voice_transcribot)


if __name__ == "__main__":
    asyncio.run(main())
