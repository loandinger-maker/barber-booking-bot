from aiogram.fsm.state import StatesGroup, State


class AdminScheduleState(StatesGroup):
    waiting_weekday = State()
    waiting_start = State()
    waiting_end = State()
    waiting_break_start = State()
    waiting_break_end = State()