from aiogram import Router, types
from ...utils.filters import IsSuspiciousMessage

router = Router()

@router.message(IsSuspiciousMessage())
async def suspicious_alert(message: types.Message):
    from config import ADMIN_TELEGRAM_IDS
    import sqlite3

    conn = sqlite3.connect("alumni.db")
    c = conn.cursor()
    c.execute("SELECT telegram_id FROM users WHERE role = 'admin'")
    db_admins = [row[0] for row in c.fetchall()]
    conn.close()

    all_admins = set(map(str, ADMIN_TELEGRAM_IDS)) | set(map(str, db_admins))

    warning = (
        f"🚨 ПІДОЗРА НА ВИКОРИСТАННЯ ЧУЖОГО НОМЕРА!\n"
        f"ID: {message.from_user.id}\n"
        f"Ім'я: {message.from_user.full_name}"
    )

    for admin_id in all_admins:
        try:
            await message.bot.send_message(admin_id, warning)
        except:
            pass

    await message.answer("🚨 Дякуємо! Повідомлення передано адміністраторам.")
