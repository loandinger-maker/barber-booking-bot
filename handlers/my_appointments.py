from aiogram import Router, F
from aiogram.types import Message

from database.db import get_user_appointments
from keyboards.inline import get_my_appointments_keyboard

router = Router()


@router.message(F.text == "📖 Мої записи")
async def my_appointments(message: Message):

    appointments = await get_user_appointments(
        message.from_user.id
    )

    if not appointments:
        await message.answer(
            "У вас поки немає активних записів."
        )
        return

    text = "📖 Ваші записи\n\n"

    for i, appointment in enumerate(
        appointments,
        start=1
    ):

        text += (
            f"{i}. ✂️ {appointment[1]}\n"
            f"   💈 {appointment[2]}\n"
            f"   📅 {appointment[3]}\n"
            f"   🕒 {appointment[4]}\n\n"
        )

    text += "👇 Оберіть запис для скасування:"

    await message.answer(
        text,
        reply_markup=get_my_appointments_keyboard(
            appointments
        )
    )