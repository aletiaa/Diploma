import asyncio
import sqlite3
from datetime import datetime

async def birthday_greeter(bot):
    while True:
        today = datetime.now().strftime("%m-%d")
        conn = sqlite3.connect("alumni.db")
        c = conn.cursor()
        c.execute("SELECT telegram_id, full_name FROM users WHERE strftime('%m-%d', birth_date) = ?", (today,))
        birthday_users = c.fetchall()
        conn.close()

        for user_id, name in birthday_users:
            try:
                await bot.send_message(user_id, f"🥳 Вітаємо, {name}! Кафедра щиро бажає вам щастя, здоров’я та нових звершень!")
            except Exception as e:
                print(f"Не вдалося привітати {user_id}: {e}")

        await asyncio.sleep(86400)  # чекати 1 день
