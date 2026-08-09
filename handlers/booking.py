from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database.db import get_services
from keyboards.inline import get_services_keyboard
from states.booking_state import BookingState


router = Router()


@router.message(F.text == "📅 Записатися")
async def booking(message: Message, state: FSMContext):

    services = await get_services()

    await state.set_state(
        BookingState.choosing_service
    )

    await message.answer(
        "✂️ Оберіть послугу:",
        reply_markup=get_services_keyboard(services)
    )