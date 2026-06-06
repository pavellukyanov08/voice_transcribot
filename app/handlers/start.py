from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.api import OpenRouterClient
from app.core import settings
from app.service import UserService
from app.utils import check_user_admin


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
    if not check_user_admin(user_id):
        await message.answer(
            "У вас нет доступа к этой команде!"
        )
        return

    credits_data = await openrouter_client.get_remaining_credits()
    total_credits = credits_data["total_credits"]
    total_usage = credits_data["total_usage"]

    await message.answer(
        f"Кредитов всего = {int(total_credits)}\n"
        f"Кредитов осталось = {float(total_usage)}"
    )

# @router.message(F.text == "/add-user")
# async def allowed_users_handler(
#     message: Message,
#     user_service: UserService,
#     state: FSMContext
# ):
#     user_name = message.text
#     user = await user_service.get_user(user_name)
#
#
#     new_user = await user_service.create_user()
#     total_credits = credits_data["total_credits"]
#     total_usage = credits_data["total_usage"]
#
#     await message.answer(
#         f"Кредитов всего = {int(total_credits)}\n"
#         f"Кредитов осталось = {float(total_usage)}"
#     )
