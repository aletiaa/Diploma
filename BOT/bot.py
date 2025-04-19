import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from .handlers.administration import admin
from .handlers.registration import register_admin, register_user
from .handlers.security import registration_security
from .config import BOT_TOKEN
from .database.db import init_db
from datetime import datetime
import sqlite3

# Import routers
from .handlers import edit_profile, main_menu

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

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


async def main():
    init_db()
    dp.include_routers(
        register_admin.router,
        registration_security.router,
        register_user.router,
        edit_profile.router,
        main_menu.router,
        admin.router
    )
    asyncio.create_task(birthday_greeter(bot))
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"❌ Помилка при запуску бота: {e}")

if __name__ == "__main__":
    asyncio.run(main())
