from aiogram import Bot
from app.core.config import settings


if not settings.BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found.")


voice_transcribot = Bot(token=settings.BOT_TOKEN)