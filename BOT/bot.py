import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from .handlers.administration import admin, manage_access, publish_events, publish_news, admin_panel, view_weekly
from .handlers.registration import register_admin, register_user
from .handlers.security import registration_security
from .handlers import edit_profile, main_menu
from .birthday.birthday_greeter import birthday_greeter 
from .config import BOT_TOKEN
from .database.db import init_db

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot=bot, storage=MemoryStorage())

async def main():
    init_db()
    await bot.delete_webhook(drop_pending_updates=True)

    dp.include_routers(
        register_admin.router,
        registration_security.router,
        register_user.router,
        edit_profile.router,
        main_menu.router,
        admin_panel.router,
        publish_news.router,
        publish_events.router,
        view_weekly.router, 
        manage_access.router
    )

    asyncio.create_task(birthday_greeter(bot))  # Запуск окремого модуля

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"❌ Помилка при запуску бота: {e}")

if __name__ == "__main__":
    asyncio.run(main())
