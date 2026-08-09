from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.db import add_user
from keyboards.reply import get_main_keyboard


router = Router()


@router.message(Command("start"))
async def start(message: Message):

    await add_user(
        message.from_user.id,
        message.from_user.full_name
    )

    await message.answer(
        "👋 Вітаємо!\n\n"
        "Я допоможу вам записатися до барбера.\n\n"
        "Оберіть дію:",
        reply_markup=get_main_keyboard(
            message.from_user.id
        )
    )