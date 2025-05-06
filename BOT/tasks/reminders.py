from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from aiogram import Bot
from ..database.queries import get_connection
from ..handlers.events.utils.event_utils import load_events
import asyncio


def start_reminder_scheduler(bot: Bot):
    """Запускає планувальник нагадувань кожні 5 хвилин"""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_event_reminders, trigger='interval', minutes=5, kwargs={"bot": bot})
    scheduler.start()


async def send_event_reminders(bot: Bot):
    """Надсилає нагадування про події, які відбудуться протягом години"""
    now = datetime.now()
    reminder_window = now + timedelta(minutes=60)

    events = [e for e in load_events()
              if now < datetime.fromisoformat(e['datetime']) <= reminder_window]

    if not events:
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        for event in events:
            cursor.execute("""
                SELECT users.telegram_id, users.full_name 
                FROM registrations
                JOIN users ON users.telegram_id = registrations.telegram_id
                WHERE event_id = ?
            """, (event["id"],))
            users = cursor.fetchall()

            for telegram_id, full_name in users:
                try:
                    await bot.send_message(
                        chat_id=telegram_id,
                        text=(
                            f"⏰ Привіт, {full_name}!\n"
                            f"Нагадуємо, що подія <b>{event['title']}</b> розпочнеться о {event['datetime']}.\n"
                            f"Не запізнюйтесь! 😉"
                        ),
                        parse_mode="HTML"
                    )
                except Exception as e:
                    print(f"❌ Не вдалося надіслати повідомлення до {telegram_id}: {e}")

    finally:
        conn.close()
