from aiogram.fsm.state import State, StatesGroup


class UserForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_confirm_name = State()

    waiting_for_timezone = State()
    waiting_for_confirm = State()
