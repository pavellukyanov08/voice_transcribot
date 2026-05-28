from aiogram import Router, F
from aiogram.types import Message

from app.api import OpenRouterClient
from app.core import settings

router = Router()


@router.message(F.text == "/start")
async def start_handler(
    message: Message
):
    await message.answer(
        "Привет! Я, Voice Transcriber, бот для расшифровки голосовых сообщений.\n"
        "Мой создатель @Lukianov08 \n\n"
        "Пришли мне голосовое сообщение или перешли чужое — я верну текст."
    )


@router.message(F.text == "/credits")
async def get_remaining_credits_handler(
    message: Message,
    openrouter_client: OpenRouterClient
):
    user_id = message.from_user.id
    if user_id != settings.ADMIN_ID:
        await message.answer(
            "У вас нет доступа к этой команде!"
        )
        return

    credits_data = await openrouter_client.get_remaining_credits()
    total_credits = credits_data["total_credits"]
    total_usage = credits_data["total_usage"]

    await message.answer(
        f"Кредитов всего = {int(total_credits)}\n"
        f"Кредитов осталось = {int(total_usage)}"
    )
