from aiogram.fsm.state import StatesGroup, State


class BookingState(StatesGroup):
    choosing_service = State()
    choosing_master = State()
    choosing_date = State()
    choosing_time = State()
    confirmation = State()