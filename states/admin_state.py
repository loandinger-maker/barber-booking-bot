from aiogram.fsm.state import State, StatesGroup


class AdminServiceState(StatesGroup):
    waiting_name = State()
    waiting_price = State()
    waiting_duration = State()