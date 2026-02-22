import asyncio
import logging

from aiogram import Dispatcher

from .middlewares import DependencyMiddleware, ErrorHandlerMiddleware
from .core.bot import voice_transcribot
from .core.stt_factory import get_stt_service
from .handlers import start, audio
from .utils import setup_logging


dp = Dispatcher()

setup_logging()
logger = logging.getLogger(__name__)


async def main():
    stt_service = get_stt_service()

    dp.message.middleware(ErrorHandlerMiddleware())
    dp.message.middleware(DependencyMiddleware(stt_service))

    dp.include_router(start.router)
    dp.include_router(audio.router)

    logger.info("Бот запущен")
    try:
        await dp.start_polling(voice_transcribot)
    finally:
        stt_service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
