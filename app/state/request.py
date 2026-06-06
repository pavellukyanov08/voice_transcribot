from aiogram.filters.state import StatesGroup, State

class RequestState(StatesGroup):
    waiting_for_text = State()