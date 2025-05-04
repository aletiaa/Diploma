import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from .handlers.registration import register_admin, register_user, register_start  # Підключаємо обробники реєстрації
from .handlers.login import login_user, login_admin
from .handlers.edit import edit_profile_user, edit_profile_admin
from .handlers.news import news_admin, news_user
from .handlers.admin import admin_panel
from .handlers.communication import communication_admin, communication_user
from .handlers.file_work import user_upload, files_admin
from .handlers.events import events_admin, events_user
from .utils import notify
from .database.db import init_db                     # Ініціалізація БД
from .config import BOT_TOKEN                        # Токен бота
from .tasks.reminders import start_reminder_scheduler

# Налаштування логування
logging.basicConfig(level=logging.INFO)

# Ініціалізація бота
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

async def main():
    # Ініціалізація БД
    init_db()

    start_reminder_scheduler(bot)
    
    # Видалення попередніх вебхуків
    await bot.delete_webhook(drop_pending_updates=True)

    # Підключення обробників
    dp.include_router(register_user.router)
    dp.include_router(register_admin.router)
    dp.include_router(register_start.router)
    dp.include_router(login_user.router)
    dp.include_router(login_admin.router)
    dp.include_router(edit_profile_user.router)
    dp.include_router(edit_profile_admin.router)
    dp.include_router(admin_panel.router)
    dp.include_router(news_admin.router)
    dp.include_router(news_user.router)
    dp.include_router(communication_admin.router)
    dp.include_router(communication_user.router)
    dp.include_router(user_upload.router)
    dp.include_router(files_admin.router)
    dp.include_router(notify.router)
    dp.include_router(events_user.router)
    dp.include_router(events_admin.router)

    logging.info("🤖 Бот запущено!")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"❌ Помилка при запуску бота: {e}")

if __name__ == "__main__":
    asyncio.run(main())
