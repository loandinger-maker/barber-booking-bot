from datetime import datetime, timedelta

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


# ==========================
# Запис клієнта
# ==========================

def get_services_keyboard(services):
    keyboard = []

    for service in services:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{service[1]} • {service[2]}₴",
                    callback_data=f"service_{service[0]}"
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def get_masters_keyboard(masters):
    keyboard = []

    for master in masters:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=master[1],
                    callback_data=f"master_{master[0]}"
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def get_dates_keyboard():
    keyboard = []

    today = datetime.now()

    for i in range(7):
        date = today + timedelta(days=i)

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=date.strftime("%d.%m"),
                    callback_data=f"date_{date.strftime('%Y-%m-%d')}"
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def get_time_keyboard(
    schedule,
    busy_times,
    duration
):

    start_time, end_time, break_start, break_end = schedule

    keyboard = []

    current = datetime.strptime(
        start_time,
        "%H:%M"
    )

    end = datetime.strptime(
        end_time,
        "%H:%M"
    )

    break_start = datetime.strptime(
        break_start,
        "%H:%M"
    )

    break_end = datetime.strptime(
        break_end,
        "%H:%M"
    )

    while current < end:

        time = current.strftime("%H:%M")

        service_end = current + timedelta(
            minutes=duration
        )

        # Послуга не повинна виходити за межі робочого дня
        if service_end > end:
            current += timedelta(minutes=30)
            continue

        # Послуга не повинна перетинати обід
        if current < break_end and service_end > break_start:
            current += timedelta(minutes=30)
            continue

        is_busy = False

        for busy_time, busy_duration in busy_times:

            busy_start = datetime.strptime(
                busy_time,
                "%H:%M"
            )

            busy_end = busy_start + timedelta(
                minutes=busy_duration
            )

            # Перевіряємо перетин інтервалів
            if current < busy_end and service_end > busy_start:
                is_busy = True
                break

        if is_busy:

            text = f"❌ {time}"
            callback = "busy"

        else:

            text = f"✅ {time}"
            callback = f"time_{time}"

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=callback
                )
            ]
        )

        current += timedelta(minutes=30)

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def get_confirm_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Підтвердити",
                    callback_data="confirm_booking"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Скасувати",
                    callback_data="cancel_booking"
                )
            ]
        ]
    )


def get_cancel_keyboard(appointment_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Скасувати запис",
                    callback_data=f"cancel_{appointment_id}"
                )
            ]
        ]
    )


# ==========================
# Адмін-панель
# ==========================

def get_admin_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Записи",
                    callback_data="admin_all_appointments"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="admin_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✂️ Керування послугами",
                    callback_data="admin_services"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💈 Керування майстрами",
                    callback_data="admin_masters"
                )
            ]
        ]
    )


def get_admin_filter_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🟢 Активні",
                    callback_data="filter_active"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Завершені",
                    callback_data="filter_completed"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Скасовані",
                    callback_data="filter_cancelled"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="admin_back"
                )
            ]
        ]
    )


def get_admin_appointments_keyboard(
    appointments,
    page,
    total_pages,
    status
):
    keyboard = []

    for appointment in appointments:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"👤 {appointment[1]} | "
                         f"{appointment[4]} {appointment[5]}",
                    callback_data=f"appointment_{appointment[0]}"
                )
            ]
        )

    navigation = []

    if page > 1:
        navigation.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f"page_{status}_{page-1}"
            )
        )

    navigation.append(
        InlineKeyboardButton(
            text=f"{page}/{total_pages}",
            callback_data="ignore"
        )
    )

    if page < total_pages:
        navigation.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f"page_{status}_{page+1}"
            )
        )

    keyboard.append(navigation)

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 До фільтрів",
                callback_data="admin_all_appointments"
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def get_admin_appointment_keyboard(appointment_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Завершити",
                    callback_data=f"admin_complete_{appointment_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Скасувати",
                    callback_data=f"admin_cancel_{appointment_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 До фільтрів",
                    callback_data="admin_all_appointments"
                )
            ]
        ]
    )


def get_services_admin_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Додати",
                    callback_data="admin_service_add"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Редагувати",
                    callback_data="admin_service_edit"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Видалити",
                    callback_data="admin_service_delete"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="admin_back"
                )
            ]
        ]
    )


def get_delete_services_keyboard(services):

    keyboard = []

    for service in services:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"🗑 {service[1]} ({service[2]}₴)",
                    callback_data=f"delete_service_{service[0]}"
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="admin_services"
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def get_masters_admin_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Додати майстра",
                    callback_data="admin_master_add"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Змінити майстра",
                    callback_data="admin_master_edit"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Видалити майстра",
                    callback_data="admin_master_delete"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📅 Розклад",
                    callback_data="admin_master_schedule"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="admin_back"
                )
            ]
        ]
    )


def get_delete_masters_keyboard(masters):

    keyboard = []

    for master in masters:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=master[1],
                    callback_data=f"delete_master_{master[0]}"
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="admin_masters"
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def get_edit_services_keyboard(services):

    keyboard = []

    for service in services:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=service[1],
                    callback_data=f"edit_service_{service[0]}"
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="admin_services"
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def get_edit_masters_keyboard(masters):

    keyboard = []

    for master in masters:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=master[1],
                    callback_data=f"edit_master_{master[0]}"
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="admin_masters"
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def get_schedule_master_keyboard(masters):

    keyboard = []

    for master in masters:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=master[1],
                    callback_data=f"schedule_master_{master[0]}"
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="admin_masters"
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def get_my_appointments_keyboard(appointments):

    keyboard = []

    for appointment in appointments:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"❌ {appointment[1]} • "
                         f"{appointment[3]} {appointment[4]}",
                    callback_data=f"cancel_{appointment[0]}"
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )