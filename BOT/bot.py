import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from .handlers.registration import register_admin, register_user, register_start
from .handlers.login import login_user, login_admin
from .handlers.edit import edit_profile_user, edit_profile_admin
from .handlers.news import news_admin, news_user
from .handlers.admin import admin_panel
from .handlers.communication import communication_admin, communication_user
from .handlers.file_work import user_upload, files_admin
from .handlers.events import events_admin, events_user
from .utils import notify
from .database.db import init_db
from .config import BOT_TOKEN
from .tasks.reminders import start_reminder_scheduler

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

async def main():
    # Ініціалізація БД
    init_db()

    # Ініціалізація бота
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Старт планувальника нагадувань
    start_reminder_scheduler(bot)

    # Скидання вебхука
    await bot.delete_webhook(drop_pending_updates=True)

    # Реєстрація всіх роутерів
    routers = [
        register_user.router, register_admin.router, register_start.router,
        login_user.router, login_admin.router,
        edit_profile_user.router, edit_profile_admin.router,
        admin_panel.router,
        news_admin.router, news_user.router,
        communication_admin.router, communication_user.router,
        user_upload.router, files_admin.router,
        notify.router,
        events_user.router, events_admin.router,
    ]
    for router in routers:
        dp.include_router(router)

    logging.info("✅ Бот запущено!")

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.exception(f"❌ Помилка під час запуску бота: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот зупинено вручну.")
