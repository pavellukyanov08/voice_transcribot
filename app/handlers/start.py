from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


router = Router()


@router.message(F.text == "/start")
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Я, Voice Transcriber, бот для расшифровки голосовых сообщений.\n"
            # "Мой создатель @Lukianov08 \n\n"
        "Пришли мне голосовое сообщение или перешли чужое — я верну текст."
    )
