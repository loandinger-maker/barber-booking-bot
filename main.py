import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database.db import init_db
from handlers import router
from utils.auto_complete import auto_complete_appointments


dp = Dispatcher()


async def auto_complete_task():
    while True:
        await auto_complete_appointments()
        await asyncio.sleep(60)


async def main():
    # Создаем базу данных
    await init_db()

    # Запускаем фоновую проверку записей
    asyncio.create_task(
        auto_complete_task()
    )

    bot = Bot(token=BOT_TOKEN)

    # Подключаем роутеры
    dp.include_router(router)

    print("Бот запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())