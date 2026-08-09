from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message


router = Router()


@router.message(Command("help"))
async def help_command(message: Message):
    await send_help(message)


@router.message(
    F.text.in_(["Допомога", "❓ Допомога"])
)
async def help_button(message: Message):
    await send_help(message)


async def send_help(message: Message):

    await message.answer(
        "ℹ️ Допомога\n\n"
        "📅 Записатися — створити новий запис.\n"
        "📖 Мої записи — переглянути свої записи.\n\n"
        "Якщо виникли запитання — зверніться до адміністратора."
    )