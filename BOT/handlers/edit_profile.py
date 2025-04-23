from aiogram import Router, types
from aiogram.filters import Command
from ..utils.specialties import search_specialty
from ..utils.department_recogniser import normalize_department
from ..utils.phone_validator import is_valid_phone
from ..utils.keyboard import edit_profile_keyboard
import sqlite3
from datetime import datetime

router = Router()
edit_state = {}

@router.message(Command("edit_profile"))
async def edit_profile_command(message: types.Message):
    telegram_id = str(message.from_user.id)
    conn = sqlite3.connect("alumni.db")
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
    if not c.fetchone():
        await message.answer("❌ Ви ще не зареєстровані. Використайте /start для реєстрації.")
        conn.close()
        return
    conn.close()

    edit_state[message.chat.id] = {"step": "choose"}
    await message.answer("Що саме хочете змінити? 👇", reply_markup=edit_profile_keyboard())

@router.message(lambda m: m.text.lower().strip() == "редагувати профіль")
async def open_edit_profile(message: types.Message):
    await edit_profile_command(message)

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
        elif "кафедру" in text:
            state["field"] = "department"
            state["step"] = "edit"
            await message.answer("🏛 Введіть назву або скорочення кафедри:")
        elif "дата народження" in text:
            state["field"] = "birth_date"
            state["step"] = "edit"
            await message.answer("🎂 Введіть нову дату народження у форматі РРРР-ММ-ДД:")
        elif "рік випуску" in text:
            state["field"] = "graduation_year"
            state["step"] = "edit"
            await message.answer("📅 Введіть новий рік випуску (наприклад, 2020):")
        elif "вийти" in text.lower():
            del edit_state[chat_id]
            await message.answer("✅ Редагування скасовано.", reply_markup=types.ReplyKeyboardRemove())
        else:
            await message.answer("⚠️ Будь ласка, оберіть одну з кнопок.")

    elif state["step"] == "edit":
        telegram_id = str(message.from_user.id)
        conn = sqlite3.connect("alumni.db")
        c = conn.cursor()

        if state["field"] == "specialty":
            matches = search_specialty(text)
            if not matches:
                conn.close()
                await message.answer("❌ Спеціальність не знайдена. Спробуйте ще.")
                return
            elif len(matches) > 1:
                conn.close()
                options = "\n".join([f"{m['code']} – {m['name']}" for m in matches])
                await message.answer(f"🔍 Знайдено декілька:\n{options}\nВведіть точніше:")
                return
            specialty = matches[0]
            c.execute("SELECT id FROM specialties WHERE code=? AND name=?", (specialty["code"], specialty["name"]))
            row = c.fetchone()
            if not row:
                conn.close()
                await message.answer("❗ Не знайдено в базі.")
                return
            c.execute("UPDATE users SET specialty_id = ? WHERE telegram_id = ?", (row[0], telegram_id))
            await message.answer(f"✅ Спеціальність оновлено на: {specialty['name']} ({specialty['code']})")

        elif state["field"] == "department":
            department_name = normalize_department(text)
            if not department_name:
                conn.close()
                await message.answer("⚠️ Кафедра не розпізнана. Спробуйте ще раз.")
                return
            c.execute("SELECT id FROM departments WHERE name=?", (department_name,))
            row = c.fetchone()
            if not row:
                conn.close()
                await message.answer("❌ Кафедру не знайдено.")
                return
            c.execute("UPDATE users SET department_id = ? WHERE telegram_id = ?", (row[0], telegram_id))
            await message.answer(f"✅ Кафедру оновлено на: {department_name}")

        elif state["field"] == "group_name":
            try:
                c.execute("ALTER TABLE users ADD COLUMN group_name TEXT")
            except sqlite3.OperationalError:
                pass
            c.execute("UPDATE users SET group_name = ? WHERE telegram_id = ?", (text, telegram_id))
            await message.answer(f"✅ Групу оновлено на: {text}")

        elif state["field"] == "phone_number":
            if not is_valid_phone(text):
                conn.close()
                await message.answer("❗ Невірний формат номера телефону. Спробуйте ще раз.")
                return
            c.execute("UPDATE users SET phone_number = ? WHERE telegram_id = ?", (text, telegram_id))
            await message.answer("✅ Номер телефону оновлено.")

        elif state["field"] == "birth_date":
            try:
                birth_date = datetime.strptime(text, "%Y-%m-%d").date()
                c.execute("UPDATE users SET birth_date = ? WHERE telegram_id = ?", (str(birth_date), telegram_id))
                await message.answer(f"✅ Дата народження оновлена на: {birth_date}")
            except ValueError:
                conn.close()
                await message.answer("❗ Невірний формат дати. Спробуйте ще раз (РРРР-ММ-ДД).")
                return

        elif state["field"] == "graduation_year":
            if not text.isdigit():
                conn.close()
                await message.answer("❗ Введіть рік у числовому форматі.")
                return
            c.execute("UPDATE users SET graduation_year = ? WHERE telegram_id = ?", (int(text), telegram_id))
            await message.answer(f"✅ Рік випуску оновлено на: {text}")

        else:
            column = state["field"]
            c.execute(f"UPDATE users SET {column} = ? WHERE telegram_id = ?", (text, telegram_id))
            await message.answer("✅ Дані оновлено.")

        conn.commit()
        conn.close()

        # Запропонувати ще раз редагування
        edit_state[chat_id] = {"step": "choose"}
        await message.answer("✅ Зміни збережено. Бажаєте змінити ще щось?", reply_markup=edit_profile_keyboard())