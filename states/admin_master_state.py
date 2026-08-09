from aiogram.fsm.state import StatesGroup, State


class AdminMasterState(StatesGroup):
    waiting_name = State()