
# ✅ FILE: bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from .config import BOT_TOKEN
from .database.db import init_db

# Import routers
from .handlers import register, edit_profile, main_menu

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

async def main():
    init_db()
    dp.include_routers(
        register.router,
        edit_profile.router,
        main_menu.router
    )
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())