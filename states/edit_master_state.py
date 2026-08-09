from aiogram.fsm.state import StatesGroup, State


class EditMasterState(StatesGroup):
    waiting_name = State()