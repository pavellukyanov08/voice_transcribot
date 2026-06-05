import asyncio
import logging
from pathlib import Path

from aiogram import Dispatcher

from .core import settings
from .middlewares import DependencyMiddleware, ErrorHandlerMiddleware
from .core.bot import transcribot
from .core.llm_init import get_text_generator, get_stt_transcriber
from .handlers import start, audio, text
from .utils import setup_logging


dp = Dispatcher()

setup_logging()
logger = logging.getLogger(__name__)


async def main():
    Path(settings.AUDIO_DIR).mkdir(exist_ok=True)
    stt_transcriber = get_stt_transcriber()
    text_generator = get_text_generator()

    dp.message.middleware(DependencyMiddleware(stt_transcriber, text_generator))
    dp.message.middleware(ErrorHandlerMiddleware())

    dp.include_router(start.router)
    dp.include_router(audio.router)
    dp.include_router(text.router)

    logger.info("Бот запущен")
    await dp.start_polling(transcribot)


if __name__ == "__main__":
    asyncio.run(main())
