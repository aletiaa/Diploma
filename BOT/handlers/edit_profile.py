from aiogram import Router, types
import sqlite3
from ..utils.specialties import search_specialty
from aiogram.filters import Command

router = Router()
edit_state = {}

@router.message(Command("edit_profile"))
async def edit_profile_command(message: types.Message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🔤 Змінити ім’я", "📱 Змінити номер")
    kb.add("🎓 Змінити групу", "📘 Змінити спеціальність")
    kb.add("❌ Вийти")
    edit_state[message.chat.id] = {"step": "choose"}
    await message.answer("Що саме хочете змінити? 👇", reply_markup=kb)

@router.message()
async def handle_editing(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in edit_state:
        return

    state = edit_state[chat_id]

    if state.get("step") == "choose":
        if "ім’я" in text:
            state["field"] = "full_name"
            state["step"] = "edit"
            await message.answer("✏️ Введіть нове ім’я та прізвище:")
        elif "номер" in text:
            state["field"] = "phone_number"
            state["step"] = "edit"
            await message.answer("📞 Введіть новий номер телефону:")
        elif "групу" in text:
            state["field"] = "group_name"
            state["step"] = "edit"
            await message.answer("🎓 Введіть нову назву групи:")
        elif "спеціальність" in text:
            state["field"] = "specialty"
            state["step"] = "edit"
            await message.answer("📘 Введіть код або частину назви спеціальності:")
        elif "вийти" in text.lower():
            del edit_state[chat_id]
            await message.answer("✅ Редагування завершено.", reply_markup=types.ReplyKeyboardRemove())
        else:
            await message.answer("⚠️ Будь ласка, оберіть зі списку кнопок.")

    elif state["step"] == "edit":
        conn = sqlite3.connect("alumni.db")
        c = conn.cursor()
        telegram_id = str(message.from_user.id)

        if state["field"] == "specialty":
            matches = search_specialty(text)
            if not matches:
                await message.answer("❌ Спеціальність не знайдена. Спробуйте ще.")
                return
            elif len(matches) > 1:
                options = "\n".join([f"{m['code']} – {m['name']}" for m in matches])
                await message.answer(f"🔍 Знайдено декілька:\n{options}\nВведіть точніше:")
                return
            specialty = matches[0]
            c.execute("SELECT id FROM specialties WHERE code=? AND name=?", (specialty["code"], specialty["name"]))
            row = c.fetchone()
            if not row:
                await message.answer("❗ Не знайдено в базі.")
                return
            c.execute("UPDATE users SET specialty_id = ? WHERE telegram_id = ?", (row[0], telegram_id))
            await message.answer(f"✅ Спеціальність оновлено на: {specialty['name']} ({specialty['code']})")

        elif state["field"] == "group_name":
            try:
                c.execute("ALTER TABLE users ADD COLUMN group_name TEXT")  # додати, якщо ще немає
            except:
                pass
            c.execute("UPDATE users SET group_name = ? WHERE telegram_id = ?", (text, telegram_id))
            await message.answer(f"✅ Групу оновлено на: {text}")

        else:
            column = state["field"]
            c.execute(f"UPDATE users SET {column} = ? WHERE telegram_id = ?", (text, telegram_id))
            await message.answer("✅ Дані оновлено.")

        conn.commit()
        conn.close()
        del edit_state[chat_id]
        await message.answer("Бажаєте ще щось змінити?", reply_markup=types.ReplyKeyboardRemove())
