# 💈 Barber Booking Bot

Telegram-бот для автоматизации записи клиентов в барбершоп.

## Возможности

### Для клиентов

- 📅 Запись на услугу
- 💈 Выбор мастера
- 📆 Выбор даты
- 🕒 Выбор свободного времени
- 💰 Просмотр цены услуги
- ⏱ Просмотр длительности услуги
- 📖 Просмотр своих записей
- ❌ Отмена записи
- 🔔 Напоминание о записи
- 🇺🇦 Украинский интерфейс

### Для администратора

- 👨‍💼 Админ-панель
- ✂️ Добавление услуг
- ✏️ Редактирование услуг
- 🗑 Удаление услуг
- 💈 Добавление мастеров
- ✏️ Редактирование мастеров
- 🗑 Удаление мастеров
- 📅 Настройка расписания мастеров
- 📋 Просмотр записей
- 🟢 Фильтрация активных записей
- ✅ Просмотр завершённых записей
- ❌ Просмотр отменённых записей
- 📊 Статистика
- 🔔 Уведомления администратора о новых и отменённых записях

## Технологии

- Python
- aiogram
- SQLite
- aiosqlite
- python-dotenv

## Структура проекта

```text
barber-booking-bot/
│
├── database/
│   └── db.py
│
├── handlers/
│   ├── admin.py
│   ├── booking.py
│   ├── callbacks.py
│   ├── help.py
│   ├── my_appointments.py
│   ├── my_bookings.py
│   └── start.py
│
├── keyboards/
│   ├── inline.py
│   └── reply.py
│
├── services/
│   └── booking_service.py
│
├── states/
│   ├── booking_state.py
│   ├── admin_state.py
│   ├── admin_master_state.py
│   ├── admin_schedule_state.py
│   ├── edit_master_state.py
│   └── edit_service_state.py
│
├── utils/
│   ├── auto_complete.py
│   ├── formatter.py
│   └── notifier.py
│
├── config.py
├── main.py
├── requirements.txt
├── .env
└── booking.db