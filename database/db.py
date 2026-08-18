import aiosqlite
from datetime import datetime, timedelta
DB_NAME = "booking.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:

        # Пользователи
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER UNIQUE,
                full_name TEXT
            )
        """)

        # Услуги
        await db.execute("""
            CREATE TABLE IF NOT EXISTS services(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                price INTEGER,
                duration INTEGER
            )
        """)

        # Мастера
        await db.execute("""
            CREATE TABLE IF NOT EXISTS masters(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        """)

        # Расписание мастеров
        await db.execute("""
            CREATE TABLE IF NOT EXISTS master_schedule(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                master_id INTEGER,
                weekday INTEGER,
                start_time TEXT,
                end_time TEXT,
                break_start TEXT,
                break_end TEXT
            )
        """)

        # Записи
        await db.execute("""
            CREATE TABLE IF NOT EXISTS appointments(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                service_id INTEGER,
                master_id INTEGER,
                date TEXT,
                time TEXT,
                status TEXT,

                day_notification INTEGER DEFAULT 0,
                hour_notification INTEGER DEFAULT 0
            )
        """)

        await db.commit()


# ---------------- Пользователи ----------------

async def add_user(tg_id: int, full_name: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO users(tg_id, full_name)
            VALUES (?, ?)
            """,
            (tg_id, full_name)
        )
        await db.commit()


# ---------------- Услуги ----------------

async def add_service(name: str, price: int, duration: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO services(name, price, duration)
            VALUES (?, ?, ?)
            """,
            (name, price, duration)
        )
        await db.commit()


async def get_services():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT id, name, price, duration
            FROM services
            """
        )
        return await cursor.fetchall()


async def get_service_by_id(service_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT id, name, price, duration
            FROM services
            WHERE id = ?
            """,
            (service_id,)
        )
        return await cursor.fetchone()


# ---------------- Мастера ----------------

async def add_master(name: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO masters(name)
            VALUES (?)
            """,
            (name,)
        )
        await db.commit()


async def get_masters():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT id, name
            FROM masters
            """
        )
        return await cursor.fetchall()


async def get_master_by_id(master_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT id, name
            FROM masters
            WHERE id = ?
            """,
            (master_id,)
        )
        return await cursor.fetchone()


# ---------------- Записи ----------------

async def add_appointment(
    user_id: int,
    service_id: int,
    master_id: int,
    date: str,
    time: str
):
    async with aiosqlite.connect(DB_NAME) as db:

        # ==========================================
        # Получаем длительность новой услуги
        # ==========================================

        cursor = await db.execute(
            """
            SELECT duration
            FROM services
            WHERE id = ?
            """,
            (service_id,)
        )

        service = await cursor.fetchone()

        if service is None:
            raise ValueError("Послугу не знайдено.")

        new_duration = service[0]

        # ==========================================
        # Получаем все активные записи мастера
        # ==========================================

        cursor = await db.execute(
            """
            SELECT
                time,
                service_id
            FROM appointments
            WHERE master_id = ?
            AND date = ?
            AND status = 'active'
            """,
            (
                master_id,
                date
            )
        )

        appointments = await cursor.fetchall()

        # ==========================================
        # Проверяем пересечение времени
        # ==========================================

        new_start = datetime.strptime(
            time,
            "%H:%M"
        )

        new_end = new_start + timedelta(
            minutes=new_duration
        )

        for appointment_time, appointment_service_id in appointments:

            cursor = await db.execute(
                """
                SELECT duration
                FROM services
                WHERE id = ?
                """,
                (appointment_service_id,)
            )

            service_data = await cursor.fetchone()

            if service_data is None:
                continue

            old_duration = service_data[0]

            old_start = datetime.strptime(
                appointment_time,
                "%H:%M"
            )

            old_end = old_start + timedelta(
                minutes=old_duration
            )

            # Пересечение интервалов
            if (
                new_start < old_end
                and new_end > old_start
            ):
                raise ValueError(
                    "Цей час уже зайнятий."
                )

        # ==========================================
        # Создаём запись
        # ==========================================

        await db.execute(
            """
            INSERT INTO appointments(
                user_id,
                service_id,
                master_id,
                date,
                time,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                service_id,
                master_id,
                date,
                time,
                "active"
            )
        )

        await db.commit()


async def get_user_appointments(tg_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT
                appointments.id,
                services.name,
                masters.name,
                appointments.date,
                appointments.time
            FROM appointments
            JOIN services
                ON appointments.service_id = services.id
            JOIN masters
                ON appointments.master_id = masters.id
            JOIN users
                ON appointments.user_id = users.tg_id
            WHERE
                users.tg_id = ?
                AND appointments.status = 'active'
            ORDER BY appointments.date, appointments.time
            """,
            (tg_id,)
        )

        return await cursor.fetchall()

async def get_busy_times(master_id, date):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT
                appointments.time,
                services.duration
            FROM appointments
            JOIN services
                ON appointments.service_id = services.id
            WHERE appointments.master_id = ?
            AND appointments.date = ?
            AND appointments.status = 'active'
            """,
            (
                master_id,
                date
            )
        )

        return await cursor.fetchall()


async def is_time_available(
    master_id: int,
    date: str,
    start_time: str,
    duration: int
):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT
                appointments.time,
                services.duration
            FROM appointments
            JOIN services
                ON appointments.service_id = services.id
            WHERE appointments.master_id = ?
            AND appointments.date = ?
            AND appointments.status = 'active'
            """,
            (
                master_id,
                date
            )
        )

        busy_times = await cursor.fetchall()

    new_start = datetime.strptime(
        start_time,
        "%H:%M"
    )

    new_end = new_start + timedelta(
        minutes=duration
    )

    for busy_time, busy_duration in busy_times:

        busy_start = datetime.strptime(
            busy_time,
            "%H:%M"
        )

        busy_end = busy_start + timedelta(
            minutes=busy_duration
        )

        # Проверка пересечения интервалов
        if new_start < busy_end and new_end > busy_start:
            return False

    return True

async def get_appointment_by_id(appointment_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT
                appointments.id,
                users.full_name,
                users.tg_id,
                services.name,
                masters.name,
                appointments.date,
                appointments.time,
                appointments.status
            FROM appointments
            JOIN users
                ON appointments.user_id = users.tg_id
            JOIN services
                ON appointments.service_id = services.id
            JOIN masters
                ON appointments.master_id = masters.id
            WHERE appointments.id = ?
            """,
            (appointment_id,)
        )

        return await cursor.fetchone()






async def cancel_appointment(appointment_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE appointments
            SET status = 'cancelled'
            WHERE id = ?
            """,
            (appointment_id,)
        )

        await db.commit()





async def get_appointments_by_status(status, limit=5, offset=0):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT
                appointments.id,
                users.full_name,
                services.name,
                masters.name,
                appointments.date,
                appointments.time,
                appointments.status
            FROM appointments
            JOIN users
                ON appointments.user_id = users.tg_id
            JOIN services
                ON appointments.service_id = services.id
            JOIN masters
                ON appointments.master_id = masters.id
            WHERE appointments.status = ?
            ORDER BY appointments.date, appointments.time
            LIMIT ? OFFSET ?
            """,
            (status, limit, offset)
        )

        return await cursor.fetchall()



async def get_appointments_count_by_status(status):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT COUNT(*)
            FROM appointments
            WHERE status = ?
            """,
            (status,)
        )

        result = await cursor.fetchone()

        return result[0]




async def complete_appointment(appointment_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE appointments
            SET status = 'completed'
            WHERE id = ?
            """,
            (appointment_id,)
        )

        await db.commit()




async def get_stats():
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT COUNT(*) FROM appointments"
        )
        total = (await cursor.fetchone())[0]

        cursor = await db.execute(
            "SELECT COUNT(*) FROM appointments WHERE status='active'"
        )
        active = (await cursor.fetchone())[0]

        cursor = await db.execute(
            "SELECT COUNT(*) FROM appointments WHERE status='completed'"
        )
        completed = (await cursor.fetchone())[0]

        cursor = await db.execute(
            "SELECT COUNT(*) FROM appointments WHERE status='cancelled'"
        )
        cancelled = (await cursor.fetchone())[0]

        return {
            "total": total,
            "active": active,
            "completed": completed,
            "cancelled": cancelled
        }



async def create_service(name, price, duration):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO services(name, price, duration)
            VALUES (?, ?, ?)
            """,
            (name, price, duration)
        )
        await db.commit()






async def delete_service(service_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            DELETE FROM services
            WHERE id = ?
            """,
            (service_id,)
        )

        await db.commit()





async def get_services_admin():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT id, name, price
            FROM services
            ORDER BY id
            """
        )

        return await cursor.fetchall()



async def service_has_active_appointments(service_id):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT COUNT(*)
            FROM appointments
            WHERE service_id = ?
            AND status = 'active'
            """,
            (service_id,)
        )

        result = await cursor.fetchone()

        return result[0] > 0



async def create_master(name):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO masters(name)
            VALUES(?)
            """,
            (name,)
        )

        await db.commit()




async def get_masters_admin():
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT id, name
            FROM masters
            ORDER BY id
            """
        )

        return await cursor.fetchall()




async def delete_master(master_id):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            DELETE FROM masters
            WHERE id=?
            """,
            (master_id,)
        )

        await db.commit()




async def master_has_active_appointments(master_id):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT COUNT(*)
            FROM appointments
            WHERE master_id=?
            AND status='active'
            """,
            (master_id,)
        )

        result = await cursor.fetchone()

        return result[0] > 0



async def update_service(
    service_id,
    name,
    price,
    duration
):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE services
            SET
                name = ?,
                price = ?,
                duration = ?
            WHERE id = ?
            """,
            (
                name,
                price,
                duration,
                service_id
            )
        )

        await db.commit()



async def update_master(
    master_id,
    name
):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE masters
            SET name = ?
            WHERE id = ?
            """,
            (
                name,
                master_id
            )
        )

        await db.commit()


# ---------------- Расписание мастеров ----------------

# ---------------- Расписание мастеров ----------------

async def create_schedule(
    master_id: int,
    weekday: int,
    start_time: str,
    end_time: str,
    break_start: str,
    break_end: str
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO master_schedule(
                master_id,
                weekday,
                start_time,
                end_time,
                break_start,
                break_end
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                master_id,
                weekday,
                start_time,
                end_time,
                break_start,
                break_end
            )
        )

        await db.commit()


async def update_schedule(
    master_id: int,
    weekday: int,
    start_time: str,
    end_time: str,
    break_start: str,
    break_end: str
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE master_schedule
            SET
                start_time = ?,
                end_time = ?,
                break_start = ?,
                break_end = ?
            WHERE master_id = ?
            AND weekday = ?
            """,
            (
                start_time,
                end_time,
                break_start,
                break_end,
                master_id,
                weekday
            )
        )

        await db.commit()


async def get_schedule(master_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT
                weekday,
                start_time,
                end_time,
                break_start,
                break_end
            FROM master_schedule
            WHERE master_id = ?
            ORDER BY weekday
            """,
            (master_id,)
        )

        return await cursor.fetchall()



async def delete_schedule(master_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            DELETE FROM master_schedule
            WHERE master_id = ?
            """,
            (master_id,)
        )

        await db.commit()


async def delete_schedule_day(
    master_id: int,
    weekday: int
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            DELETE FROM master_schedule
            WHERE master_id = ?
            AND weekday = ?
            """,
            (
                master_id,
                weekday
            )
        )

        await db.commit()


async def get_schedule_for_day(
    master_id: int,
    weekday: int
):
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT
                start_time,
                end_time,
                break_start,
                break_end
            FROM master_schedule
            WHERE master_id = ?
            AND weekday = ?
            """,
            (
                master_id,
                weekday
            )
        )

        return await cursor.fetchone()




