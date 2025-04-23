# handlers/administration/manage_access.py
from aiogram import Router, types
import sqlite3

router = Router()
access_state = {}

@router.message(lambda msg: msg.text == "🔐 Управління доступом")
async def start_access_management(message: types.Message):
    chat_id = message.chat.id
    access_state[chat_id] = {"step": "search"}
    await message.answer("🔎 Введіть прізвище або telegram_id користувача, щоб змінити рівень доступу:")

@router.message()
async def handle_access(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in access_state:
        return

    state = access_state[chat_id]

    if state["step"] == "search":
        conn = sqlite3.connect("alumni.db")
        c = conn.cursor()
        if text.isdigit():
            c.execute("SELECT id, telegram_id, full_name, role, admin_level FROM users WHERE telegram_id = ?", (text,))
        else:
            c.execute("SELECT id, telegram_id, full_name, role, admin_level FROM users WHERE full_name LIKE ?", (f"%{text}%",))
        user = c.fetchone()
        conn.close()

        if not user:
            await message.answer("❌ Користувача не знайдено. Спробуйте ще раз.")
            return

        state["user_id"] = user[0]
        state["telegram_id"] = user[1]
        state["full_name"] = user[2]
        state["step"] = "change"

        await message.answer(
            f"👤 <b>{user[2]}</b> (ID: {user[1]})\n"
            f"🔑 Роль: <b>{user[3]}</b>\n"
            f"⚙️ Рівень доступу: <b>{user[4] or 'N/A'}</b>\n\n"
            f"Оберіть новий рівень доступу:\n"
            f"🔹 user – Звичайний користувач\n"
            f"🔹 admin limited – Обмежений адмін\n"
            f"🔹 admin super – Супер-адмін",
            reply_markup=types.ReplyKeyboardMarkup(
                keyboard=[
                    [types.KeyboardButton(text="user"), types.KeyboardButton(text="admin limited"), types.KeyboardButton(text="admin super")],
                    [types.KeyboardButton(text="❌ Скасувати")]
                ],
                resize_keyboard=True
            )
        )

    elif state["step"] == "change":
        if text not in ["user", "admin limited", "admin super"]:
            if text == "❌ Скасувати":
                del access_state[chat_id]
                await message.answer("⚙️ Операцію скасовано.", reply_markup=types.ReplyKeyboardRemove())
                return
            await message.answer("❗ Виберіть один із запропонованих рівнів доступу.")
            return

        conn = sqlite3.connect("alumni.db")
        c = conn.cursor()
        if text == "user":
            c.execute("UPDATE users SET role = 'user', admin_level = NULL WHERE id = ?", (state["user_id"],))
        elif text == "admin limited":
            c.execute("UPDATE users SET role = 'admin', admin_level = 'limited' WHERE id = ?", (state["user_id"],))
        elif text == "admin super":
            c.execute("UPDATE users SET role = 'admin', admin_level = 'super' WHERE id = ?", (state["user_id"],))
        conn.commit()
        conn.close()

        await message.answer(f"✅ Рівень доступу для <b>{state['full_name']}</b> оновлено на: <b>{text}</b>",
                             reply_markup=types.ReplyKeyboardRemove())
        del access_state[chat_id]
