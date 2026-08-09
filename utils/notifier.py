import asyncio
from datetime import datetime, timedelta

from database.db import (
    get_upcoming_appointments,
    mark_notification_sent
)


async def notifier(bot):

    while True:

        now = datetime.now()

        appointments = await get_upcoming_appointments()

        for appointment in appointments:

            appointment_id = appointment[0]
            tg_id = appointment[1]
            service = appointment[2]
            master = appointment[3]
            date = appointment[4]
            time = appointment[5]

            appointment_time = datetime.strptime(
                f"{date} {time}",
                "%Y-%m-%d %H:%M"
            )

            delta = appointment_time - now

            if timedelta(hours=23, minutes=59) <= delta <= timedelta(hours=24, minutes=1):

                try:
                    await bot.send_message(
                        tg_id,
                        (
                            "📅 Нагадування!\n\n"
                            "До вашого запису залишився 1 день.\n\n"
                            f"✂️ {service}\n"
                            f"💈 {master}\n"
                            f"📅 {date}\n"
                            f"🕒 {time}"
                        )
                    )

                    await mark_notification_sent(
                        appointment_id,
                        "day"
                    )

                except Exception:
                    pass

        await asyncio.sleep(60)