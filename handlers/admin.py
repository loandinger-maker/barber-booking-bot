from math import ceil
from datetime import datetime

from states.admin_schedule_state import AdminScheduleState
from database.db import service_has_active_appointments
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.admin_master_state import AdminMasterState
from config import ADMIN_ID
from states.edit_service_state import EditServiceState
from states.admin_state import AdminServiceState
from states.edit_master_state import EditMasterState

from database.db import (
    get_appointment_by_id,
    cancel_appointment,
    complete_appointment,
    get_appointments_by_status,
    get_appointments_count_by_status,
    get_stats,
    create_service,
    delete_service,
    get_services_admin,
    create_master,
    delete_master,
    get_masters_admin,
    master_has_active_appointments,
    update_service,
    update_master,
    create_schedule
)

from keyboards.inline import (
    get_admin_keyboard,
    get_admin_filter_keyboard,
    get_admin_appointments_keyboard,
    get_admin_appointment_keyboard,
    get_services_admin_keyboard,
    get_delete_services_keyboard,
    get_masters_admin_keyboard,
    get_delete_masters_keyboard,
    get_edit_services_keyboard,
    get_edit_masters_keyboard,
    get_schedule_master_keyboard
)


router = Router()


def is_valid_time(value: str) -> bool:
    try:
        datetime.strptime(value, "%H:%M")
        return True
    except ValueError:
        return False


# ==========================
# Адмін-панель
# ==========================

@router.message(F.text == "👨‍💼 Адмін-панель")
async def admin_panel(message: Message):

    if str(message.from_user.id) != str(ADMIN_ID):
        return

    await message.answer(
        "👨‍💼 Адмін-панель\n\n"
        "Оберіть дію:",
        reply_markup=get_admin_keyboard()
    )


# ==========================
# Записи
# ==========================

@router.callback_query(F.data == "admin_all_appointments")
async def admin_all_appointments(callback: CallbackQuery):

    await callback.message.edit_text(
        "Оберіть фільтр:",
        reply_markup=get_admin_filter_keyboard()
    )

    await callback.answer()


@router.callback_query(F.data.startswith("filter_"))
async def filter_appointments(callback: CallbackQuery):

    status = callback.data.split("_")[1]

    page = 1
    limit = 5

    total = await get_appointments_count_by_status(status)

    total_pages = max(
        1,
        ceil(total / limit)
    )

    appointments = await get_appointments_by_status(
        status=status,
        limit=limit,
        offset=0
    )

    names = {
        "active": "🟢 Активні",
        "completed": "✅ Завершені",
        "cancelled": "❌ Скасовані"
    }

    await callback.message.edit_text(
        f"{names[status]} записи:",
        reply_markup=get_admin_appointments_keyboard(
            appointments,
            page,
            total_pages,
            status
        )
    )

    await callback.answer()


@router.callback_query(F.data.startswith("page_"))
async def admin_change_page(callback: CallbackQuery):

    _, status, page = callback.data.split("_")

    page = int(page)

    limit = 5

    offset = (page - 1) * limit

    total = await get_appointments_count_by_status(
        status
    )

    total_pages = max(
        1,
        ceil(total / limit)
    )

    appointments = await get_appointments_by_status(
        status=status,
        limit=limit,
        offset=offset
    )

    names = {
        "active": "🟢 Активні",
        "completed": "✅ Завершені",
        "cancelled": "❌ Скасовані"
    }

    await callback.message.edit_text(
        f"{names[status]} записи:",
        reply_markup=get_admin_appointments_keyboard(
            appointments,
            page,
            total_pages,
            status
        )
    )

    await callback.answer()


@router.callback_query(F.data.startswith("appointment_"))
async def admin_open_appointment(callback: CallbackQuery):

    appointment_id = int(
        callback.data.split("_")[1]
    )

    appointment = await get_appointment_by_id(
        appointment_id
    )

    statuses = {
        "active": "🟢 Активна",
        "completed": "✅ Завершена",
        "cancelled": "❌ Скасована"
    }

    status = statuses.get(
        appointment[7],
        "Невідомо"
    )

    await callback.message.edit_text(
        f"👤 Клієнт: {appointment[1]}\n\n"
        f"✂️ Послуга: {appointment[3]}\n"
        f"💈 Майстер: {appointment[4]}\n"
        f"📅 Дата: {appointment[5]}\n"
        f"🕒 Час: {appointment[6]}\n\n"
        f"Статус:\n{status}",
        reply_markup=get_admin_appointment_keyboard(
            appointment_id
        )
    )

    await callback.answer()


@router.callback_query(F.data.startswith("admin_cancel_"))
async def admin_cancel(
    callback: CallbackQuery,
    bot: Bot
):

    appointment_id = int(
        callback.data.split("_")[2]
    )

    appointment = await get_appointment_by_id(
        appointment_id
    )

    if appointment[7] == "cancelled":

        await callback.answer(
            "Запис уже скасовано.",
            show_alert=True
        )

        return

    await cancel_appointment(
        appointment_id
    )

    try:

        await bot.send_message(
            appointment[2],
            "❌ Ваш запис було скасовано адміністратором."
        )

    except Exception:
        pass

    await callback.message.edit_text(
        "✅ Запис скасовано."
    )

    await callback.answer()


@router.callback_query(F.data.startswith("admin_complete_"))
async def admin_complete(
    callback: CallbackQuery,
    bot: Bot
):

    appointment_id = int(
        callback.data.split("_")[2]
    )

    appointment = await get_appointment_by_id(
        appointment_id
    )

    if appointment[7] == "completed":

        await callback.answer(
            "Запис уже завершено.",
            show_alert=True
        )

        return

    if appointment[7] == "cancelled":

        await callback.answer(
            "Не можна завершити скасований запис.",
            show_alert=True
        )

        return

    await complete_appointment(
        appointment_id
    )

    try:

        await bot.send_message(
            appointment[2],
            (
                "✅ Ваш запис успішно завершено.\n\n"
                "Дякуємо за візит!"
            )
        )

    except Exception:
        pass

    await callback.message.edit_text(
        "✅ Запис позначено як завершений."
    )

    await callback.answer()


# ==========================
# Статистика
# ==========================

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):

    stats = await get_stats()

    await callback.message.edit_text(
        "📊 Статистика\n\n"
        f"📋 Всього записів: {stats['total']}\n"
        f"🟢 Активних: {stats['active']}\n"
        f"✅ Завершених: {stats['completed']}\n"
        f"❌ Скасованих: {stats['cancelled']}",
        reply_markup=get_admin_keyboard()
    )

    await callback.answer()


# ==========================
# Керування послугами
# ==========================

@router.callback_query(F.data == "admin_services")
async def admin_services(callback: CallbackQuery):

    await callback.message.edit_text(
        "✂️ Керування послугами",
        reply_markup=get_services_admin_keyboard()
    )

    await callback.answer()


@router.callback_query(F.data == "admin_masters")
async def admin_masters(callback: CallbackQuery):

    await callback.message.edit_text(
        "💈 Керування майстрами",
        reply_markup=get_masters_admin_keyboard()
    )

    await callback.answer()


@router.callback_query(F.data == "admin_master_schedule")
async def admin_master_schedule(
    callback: CallbackQuery
):

    masters = await get_masters_admin()

    await callback.message.edit_text(
        "Оберіть майстра:",
        reply_markup=get_schedule_master_keyboard(
            masters
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("schedule_master_")
)
async def choose_schedule_master(
    callback: CallbackQuery,
    state: FSMContext
):

    master_id = int(
        callback.data.split("_")[2]
    )

    await state.update_data(
        master_id=master_id
    )

    await state.set_state(
        AdminScheduleState.waiting_weekday
    )

    await callback.message.edit_text(
        "Введіть день тижня.\n\n"
        "0 - Понеділок\n"
        "1 - Вівторок\n"
        "2 - Середа\n"
        "3 - Четвер\n"
        "4 - П'ятниця\n"
        "5 - Субота\n"
        "6 - Неділя"
    )

    await callback.answer()


@router.callback_query(F.data == "admin_master_add")
async def admin_master_add(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.set_state(
        AdminMasterState.waiting_name
    )

    await callback.message.edit_text(
        "Введіть ім'я майстра:"
    )

    await callback.answer()


@router.message(AdminMasterState.waiting_name)
async def master_name(
    message: Message,
    state: FSMContext
):

    await create_master(
        message.text
    )

    await state.clear()

    await message.answer(
        "✅ Майстра успішно додано."
    )


@router.callback_query(F.data == "admin_master_delete")
async def admin_master_delete(
    callback: CallbackQuery
):

    masters = await get_masters_admin()

    await callback.message.edit_text(
        "Оберіть майстра:",
        reply_markup=get_delete_masters_keyboard(
            masters
        )
    )

    await callback.answer()


@router.callback_query(F.data == "admin_master_edit")
async def admin_master_edit(
    callback: CallbackQuery
):

    masters = await get_masters_admin()

    await callback.message.edit_text(
        "Оберіть майстра:",
        reply_markup=get_edit_masters_keyboard(
            masters
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("edit_master_")
)
async def edit_master(
    callback: CallbackQuery,
    state: FSMContext
):

    master_id = int(
        callback.data.split("_")[2]
    )

    await state.update_data(
        master_id=master_id
    )

    await state.set_state(
        EditMasterState.waiting_name
    )

    await callback.message.edit_text(
        "Введіть нове ім'я майстра:"
    )

    await callback.answer()


@router.callback_query(F.data == "admin_service_add")
async def admin_service_add(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.set_state(
        AdminServiceState.waiting_name
    )

    await callback.message.edit_text(
        "Введіть назву послуги:"
    )

    await callback.answer()


@router.message(AdminServiceState.waiting_name)
async def service_name(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        name=message.text
    )

    await state.set_state(
        AdminServiceState.waiting_price
    )

    await message.answer(
        "Введіть ціну:"
    )


@router.message(AdminServiceState.waiting_price)
async def service_price(
    message: Message,
    state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "Введіть число."
        )

        return

    await state.update_data(
        price=int(message.text)
    )

    await state.set_state(
        AdminServiceState.waiting_duration
    )

    await message.answer(
        "Введіть тривалість (хвилин):"
    )


@router.message(AdminServiceState.waiting_duration)
async def service_duration(
    message: Message,
    state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "Введіть число."
        )

        return

    data = await state.get_data()

    await create_service(
        data["name"],
        data["price"],
        int(message.text)
    )

    await state.clear()

    await message.answer(
        "✅ Послугу успішно додано."
    )


# ==========================
# Назад
# ==========================

@router.callback_query(F.data == "admin_back")
async def admin_back(
    callback: CallbackQuery
):

    await callback.message.edit_text(
        "👨‍💼 Адмін-панель\n\n"
        "Оберіть дію:",
        reply_markup=get_admin_keyboard()
    )

    await callback.answer()


@router.callback_query(F.data == "admin_service_delete")
async def admin_service_delete(
    callback: CallbackQuery
):

    services = await get_services_admin()

    await callback.message.edit_text(
        "Оберіть послугу для видалення:",
        reply_markup=get_delete_services_keyboard(
            services
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("delete_service_")
)
async def delete_service_handler(
    callback: CallbackQuery
):

    service_id = int(
        callback.data.split("_")[2]
    )

    if await service_has_active_appointments(
        service_id
    ):

        await callback.answer(
            "Не можна видалити послугу.\n"
            "Є активні записи.",
            show_alert=True
        )

        return

    await delete_service(
        service_id
    )

    services = await get_services_admin()

    if not services:

        await callback.message.edit_text(
            "✅ Усі послуги видалено."
        )

    else:

        await callback.message.edit_text(
            "✅ Послугу видалено.\n\n"
            "Оберіть наступну:",
            reply_markup=get_delete_services_keyboard(
                services
            )
        )

    await callback.answer()


@router.callback_query(
    F.data.startswith("delete_master_")
)
async def delete_master_handler(
    callback: CallbackQuery
):

    master_id = int(
        callback.data.split("_")[2]
    )

    if await master_has_active_appointments(
        master_id
    ):

        await callback.answer(
            "У майстра є активні записи.",
            show_alert=True
        )

        return

    await delete_master(
        master_id
    )

    masters = await get_masters_admin()

    if not masters:

        await callback.message.edit_text(
            "✅ Усіх майстрів видалено."
        )

    else:

        await callback.message.edit_text(
            "✅ Майстра видалено.\n\n"
            "Оберіть наступного:",
            reply_markup=get_delete_masters_keyboard(
                masters
            )
        )

    await callback.answer()


@router.callback_query(F.data == "admin_service_edit")
async def admin_service_edit(
    callback: CallbackQuery
):

    services = await get_services_admin()

    await callback.message.edit_text(
        "Оберіть послугу для редагування:",
        reply_markup=get_edit_services_keyboard(
            services
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("edit_service_")
)
async def edit_service(
    callback: CallbackQuery,
    state: FSMContext
):

    service_id = int(
        callback.data.split("_")[2]
    )

    await state.update_data(
        service_id=service_id
    )

    await state.set_state(
        EditServiceState.waiting_name
    )

    await callback.message.edit_text(
        "Введіть нову назву послуги:"
    )

    await callback.answer()


@router.message(EditServiceState.waiting_name)
async def edit_service_name(
    message: Message,
    state: FSMContext
):

    await state.update_data(
        name=message.text
    )

    await state.set_state(
        EditServiceState.waiting_price
    )

    await message.answer(
        "Введіть нову ціну:"
    )


@router.message(EditServiceState.waiting_price)
async def edit_service_price(
    message: Message,
    state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "Введіть число."
        )

        return

    await state.update_data(
        price=int(message.text)
    )

    await state.set_state(
        EditServiceState.waiting_duration
    )

    await message.answer(
        "Введіть нову тривалість:"
    )


@router.message(EditServiceState.waiting_duration)
async def edit_service_duration(
    message: Message,
    state: FSMContext
):

    if not message.text.isdigit():

        await message.answer(
            "Введіть число."
        )

        return

    data = await state.get_data()

    await update_service(
        data["service_id"],
        data["name"],
        data["price"],
        int(message.text)
    )

    await state.clear()

    await message.answer(
        "✅ Послугу успішно оновлено."
    )


@router.message(EditMasterState.waiting_name)
async def edit_master_name(
    message: Message,
    state: FSMContext
):

    data = await state.get_data()

    await update_master(
        data["master_id"],
        message.text
    )

    await state.clear()

    await message.answer(
        "✅ Майстра успішно оновлено."
    )


# ==========================
# Розклад
# ==========================

@router.message(
    AdminScheduleState.waiting_weekday
)
async def schedule_weekday(
    message: Message,
    state: FSMContext
):

    if message.text not in [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6"
    ]:

        await message.answer(
            "Введіть число від 0 до 6."
        )

        return

    await state.update_data(
        weekday=int(message.text)
    )

    await state.set_state(
        AdminScheduleState.waiting_start
    )

    await message.answer(
        "Введіть початок робочого дня.\n\n"
        "Наприклад:\n10:00"
    )


@router.message(
    AdminScheduleState.waiting_start
)
async def schedule_start(
    message: Message,
    state: FSMContext
):

    if not is_valid_time(message.text):

        await message.answer(
            "Введіть час у форматі HH:MM\n\n"
            "Наприклад: 10:00"
        )

        return

    await state.update_data(
        start_time=message.text
    )

    await state.set_state(
        AdminScheduleState.waiting_end
    )

    await message.answer(
        "Введіть кінець робочого дня.\n\n"
        "Наприклад:\n18:00"
    )


@router.message(
    AdminScheduleState.waiting_end
)
async def schedule_end(
    message: Message,
    state: FSMContext
):

    if not is_valid_time(message.text):

        await message.answer(
            "Введіть час у форматі HH:MM\n\n"
            "Наприклад: 18:00"
        )

        return

    await state.update_data(
        end_time=message.text
    )

    await state.set_state(
        AdminScheduleState.waiting_break_start
    )

    await message.answer(
        "Введіть початок обіду.\n\n"
        "Наприклад:\n13:00"
    )


@router.message(
    AdminScheduleState.waiting_break_start
)
async def schedule_break_start(
    message: Message,
    state: FSMContext
):

    if not is_valid_time(message.text):

        await message.answer(
            "Введіть час у форматі HH:MM\n\n"
            "Наприклад: 13:00"
        )

        return

    await state.update_data(
        break_start=message.text
    )

    await state.set_state(
        AdminScheduleState.waiting_break_end
    )

    await message.answer(
        "Введіть кінець обіду.\n\n"
        "Наприклад:\n14:00"
    )


@router.message(
    AdminScheduleState.waiting_break_end
)
async def schedule_break_end(
    message: Message,
    state: FSMContext
):

    if not is_valid_time(message.text):

        await message.answer(
            "Введіть час у форматі HH:MM\n\n"
            "Наприклад: 14:00"
        )

        return

    data = await state.get_data()

    start = datetime.strptime(
        data["start_time"],
        "%H:%M"
    )

    end = datetime.strptime(
        data["end_time"],
        "%H:%M"
    )

    break_start = datetime.strptime(
        data["break_start"],
        "%H:%M"
    )

    break_end = datetime.strptime(
        message.text,
        "%H:%M"
    )

    if end <= start:

        await message.answer(
            "❌ Кінець робочого дня має бути "
            "пізніше початку."
        )

        return

    if break_start >= break_end:

        await message.answer(
            "❌ Кінець обіду має бути "
            "пізніше початку."
        )

        return

    if break_start < start or break_end > end:

        await message.answer(
            "❌ Обід має бути в межах "
            "робочого часу."
        )

        return

    await create_schedule(
        master_id=data["master_id"],
        weekday=data["weekday"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        break_start=data["break_start"],
        break_end=message.text
    )

    await state.clear()

    await message.answer(
        "✅ Розклад успішно збережено."
    )