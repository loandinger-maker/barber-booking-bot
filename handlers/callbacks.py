from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID

from database.db import (
    get_schedule_for_day,
    get_masters,
    get_service_by_id,
    get_master_by_id,
    add_appointment,
    get_busy_times,
    cancel_appointment,
    get_appointment_by_id,
    is_time_available,
)

from keyboards.inline import (
    get_masters_keyboard,
    get_dates_keyboard,
    get_time_keyboard,
    get_confirm_keyboard,
)

from states.booking_state import BookingState

router = Router()


# ============================================================
# ВИБІР ПОСЛУГИ
# ============================================================

@router.callback_query(
    BookingState.choosing_service,
    F.data.startswith("service_")
)
async def choose_service(
    callback: CallbackQuery,
    state: FSMContext
):

    service_id = int(
        callback.data.split("_")[1]
    )

    await state.update_data(
        service_id=service_id
    )

    masters = await get_masters()

    await state.set_state(
        BookingState.choosing_master
    )

    await callback.message.edit_text(
        "💈 Оберіть майстра:",
        reply_markup=get_masters_keyboard(
            masters
        )
    )

    await callback.answer()


# ============================================================
# ВИБІР МАЙСТРА
# ============================================================

@router.callback_query(
    BookingState.choosing_master,
    F.data.startswith("master_")
)
async def choose_master(
    callback: CallbackQuery,
    state: FSMContext
):

    master_id = int(
        callback.data.split("_")[1]
    )

    await state.update_data(
        master_id=master_id
    )

    await state.set_state(
        BookingState.choosing_date
    )

    await callback.message.edit_text(
        "📅 Оберіть дату:",
        reply_markup=get_dates_keyboard()
    )

    await callback.answer()


# ============================================================
# ВИБІР ДАТИ
# ============================================================

@router.callback_query(
    BookingState.choosing_date,
    F.data.startswith("date_")
)
async def choose_date(
    callback: CallbackQuery,
    state: FSMContext
):

    date = callback.data.split(
        "_",
        1
    )[1]

    await state.update_data(
        date=date
    )

    data = await state.get_data()

    weekday = datetime.strptime(
        date,
        "%Y-%m-%d"
    ).weekday()

    schedule = await get_schedule_for_day(
        data["master_id"],
        weekday
    )

    if schedule is None:

        await callback.answer(
            "У цей день майстер не працює.",
            show_alert=True
        )

        return

    busy_times = await get_busy_times(
        data["master_id"],
        date
    )

    service = await get_service_by_id(
        data["service_id"]
    )

    if service is None:

        await callback.answer(
            "Послугу не знайдено.",
            show_alert=True
        )

        await state.clear()

        return

    duration = service[3]

    await state.set_state(
        BookingState.choosing_time
    )

    await callback.message.edit_text(
        "🕒 Оберіть час:",
        reply_markup=get_time_keyboard(
            schedule,
            busy_times,
            duration
        )
    )

    await callback.answer()


# ============================================================
# ВИБІР ЧАСУ
# ============================================================

@router.callback_query(
    BookingState.choosing_time,
    F.data.startswith("time_")
)
async def choose_time(
    callback: CallbackQuery,
    state: FSMContext
):

    time = callback.data.split(
        "_",
        1
    )[1]

    await state.update_data(
        time=time
    )

    data = await state.get_data()

    service = await get_service_by_id(
        data["service_id"]
    )

    master = await get_master_by_id(
        data["master_id"]
    )

    if service is None or master is None:

        await callback.answer(
            "Помилка: послугу або майстра не знайдено.",
            show_alert=True
        )

        await state.clear()

        return

    await state.set_state(
        BookingState.confirmation
    )

    await callback.message.edit_text(
        f"📋 Підтвердіть запис\n\n"
        f"✂️ Послуга: {service[1]}\n"
        f"💰 Ціна: {service[2]} грн\n"
        f"⏱ Тривалість: {service[3]} хв.\n\n"
        f"💈 Майстер: {master[1]}\n"
        f"📅 Дата: {data['date']}\n"
        f"🕒 Час: {data['time']}",
        reply_markup=get_confirm_keyboard()
    )

    await callback.answer()


# ============================================================
# ПІДТВЕРДЖЕННЯ ЗАПИСУ
# ============================================================

@router.callback_query(
    BookingState.confirmation,
    F.data == "confirm_booking"
)
async def confirm_booking(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot
):
    data = await state.get_data()

    # ==========================================
    # Проверка, что выбранное время ещё не прошло
    # ==========================================

    selected_datetime = datetime.strptime(
        f"{data['date']} {data['time']}",
        "%Y-%m-%d %H:%M"
    )

    now = datetime.now()

    if selected_datetime <= now:

        await callback.answer(
            "❌ Це час уже минув. Оберіть інший час.",
            show_alert=True
        )

        return

    # ==========================================
    # Создание записи
    # ==========================================

    try:

        await add_appointment(
            callback.from_user.id,
            data["service_id"],
            data["master_id"],
            data["date"],
            data["time"]
        )

    except ValueError as e:

        await callback.answer(
            str(e),
            show_alert=True
        )

        return

    # ==========================================
    # Получаем информацию о записи
    # ==========================================

    service = await get_service_by_id(
        data["service_id"]
    )

    master = await get_master_by_id(
        data["master_id"]
    )

    if service is None or master is None:

        await callback.answer(
            "❌ Помилка: послугу або майстра не знайдено.",
            show_alert=True
        )

        return

    username = callback.from_user.username

    # ==========================================
    # Уведомление администратора
    # ==========================================

    await bot.send_message(
        ADMIN_ID,
        f"🔔 Новий запис!\n\n"
        f"👤 Клієнт: {callback.from_user.full_name}\n"
        f"🆔 ID: {callback.from_user.id}\n"
        f"📨 Username: @{username if username else 'немає'}\n\n"
        f"✂️ Послуга: {service[1]}\n"
        f"💰 Ціна: {service[2]} грн\n"
        f"⏱ Тривалість: {service[3]} хв.\n"
        f"💈 Майстер: {master[1]}\n"
        f"📅 Дата: {data['date']}\n"
        f"🕒 Час: {data['time']}"
    )

    # ==========================================
    # Успешное создание
    # ==========================================

    await callback.message.edit_text(
        "✅ Запис успішно створено!"
    )

    await state.clear()

    await callback.answer()


# ============================================================
# СКАСУВАННЯ ЗАПИСУ НА ЕТАПІ ПІДТВЕРДЖЕННЯ
# ============================================================

@router.callback_query(
    BookingState.confirmation,
    F.data == "cancel_booking"
)
async def cancel_booking(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.clear()

    await callback.message.edit_text(
        "❌ Запис скасовано."
    )

    await callback.answer()


# ============================================================
# СКАСУВАННЯ ВЖЕ СТВОРЕНОГО ЗАПИСУ
# ============================================================

@router.callback_query(
    F.data.regexp(r"^cancel_\d+$")
)
async def cancel_appointment_handler(
    callback: CallbackQuery,
    bot: Bot
):

    appointment_id = int(
        callback.data.split("_")[1]
    )

    appointment = await get_appointment_by_id(
        appointment_id
    )

    if appointment is None:

        await callback.answer(
            "Запис не знайдено.",
            show_alert=True
        )

        return

    await cancel_appointment(
        appointment_id
    )

    username = callback.from_user.username

    try:

        await bot.send_message(
            ADMIN_ID,
            f"❌ Користувач скасував запис\n\n"
            f"👤 {callback.from_user.full_name}\n"
            f"🆔 {callback.from_user.id}\n"
            f"📨 @{username if username else 'немає'}\n\n"
            f"✂️ {appointment[3]}\n"
            f"💈 {appointment[4]}\n"
            f"📅 {appointment[5]}\n"
            f"🕒 {appointment[6]}"
        )

    except Exception:
        pass

    await callback.message.edit_text(
        "❌ Запис скасовано."
    )

    await callback.answer(
        "Запис успішно скасовано!"
    )


# ============================================================
# ЗАЙНЯТИЙ ЧАС
# ============================================================

@router.callback_query(
    F.data == "busy"
)
async def busy_time(
    callback: CallbackQuery
):

    await callback.answer(
        "Цей час уже зайнятий.",
        show_alert=True
    )