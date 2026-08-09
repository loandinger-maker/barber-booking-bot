from datetime import datetime
import aiosqlite

from database.db import DB_NAME


async def auto_complete_appointments():

    now = datetime.now()

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
            SELECT id, date, time
            FROM appointments
            WHERE status = 'active'
        """)

        appointments = await cursor.fetchall()

        for appointment in appointments:

            appointment_id = appointment[0]

            appointment_datetime = datetime.strptime(
                f"{appointment[1]} {appointment[2]}",
                "%Y-%m-%d %H:%M"
            )

            if appointment_datetime < now:

                await db.execute(
                    """
                    UPDATE appointments
                    SET status='completed'
                    WHERE id=?
                    """,
                    (appointment_id,)
                )

        await db.commit()