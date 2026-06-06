import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.service import UserService, TextService
from app.schemas import UserRequestText
from app.state.request import RequestState
from app.utils import check_user_allowed


router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == '/request')
async def handle_request(
    message: Message,
    user_service: UserService,
    state: FSMContext,
):
    user_id = message.from_user.id
    username = message.from_user.username

    if not check_user_allowed(user_id):
        await message.answer("У вас нет доступа к этой команде!")
        return

    await message.answer("Пришли мне запрос")

    await user_service.create_user(
        telegram_id=user_id,
        name=username if username else None,
    )

    await state.set_state(RequestState.waiting_for_text)


@router.message(RequestState.waiting_for_text)
async def handle_request_text(
    message: Message,
    text_service: TextService,
    state: FSMContext,
):
    telegram_id = message.from_user.id

    text_request = UserRequestText(
        text=message.text
    )

    try:
        result = await text_service.process_text(
            text_request=text_request,
            user_id=telegram_id
        )

        if result.success and result.generated_text:
            await message.answer(f"📝 {result.generated_text}")
        else:
            error_msg = result.error_message or "Ошибка генерации текста 😔"
            await message.answer(error_msg)

    except ValueError as e:
        logger.warning(f"Ошибка генерации текста: {e}")

    await state.clear()