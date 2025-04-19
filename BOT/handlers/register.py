from aiogram import Router, types
from aiogram.filters import Command
import sqlite3
from ..utils.specialties import search_specialty
from ..utils.department_recogniser import normalize_department
from ..utils.keyboard import main_menu_keyboard
from datetime import datetime

router = Router()
user_state = {}

ADMIN_PASSWORD = "051220044"

@router.message(Command("start"))
async def start(message: types.Message):
    user_state[message.chat.id] = {"step": "role_choice"}
    await message.answer(
        "Вітаю! Ви хочете увійти як користувач чи адміністратор?"
        "Введіть <b>user</b> або <b>admin</b>:")

@router.message()
async def registration(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_state:
        return

    state = user_state[chat_id]
    step = state.get("step")

    if step == "role_choice":
        if text.lower() == "admin":
            state["step"] = "admin_password"
            await message.answer("🔐 Введіть пароль адміністратора:")
            return
        elif text.lower() == "user":
            state["role"] = "user"
            state["step"] = "name"
            await message.answer("👋 Почнемо реєстрацію.Вкажіть ваше ім’я та прізвище:")
            return
        else:
            await message.answer("❗ Введіть лише <b>user</b> або <b>admin</b>.")
            return

    if step == "admin_password":
        if text == ADMIN_PASSWORD:
            state["role"] = "admin"
            state["step"] = "name"
            await message.answer("✅ Пароль підтверджено. Вкажіть ваше ім’я та прізвище:")
        else:
            await message.answer("❌ Невірний пароль. Спробуйте ще раз або введіть <b>user</b> щоб увійти як користувач:")
        return

    if step == "name":
        state["name"] = text
        state["step"] = "birth_date"
        await message.answer("🎂 Вкажіть дату народження у форматі РРРР-ММ-ДД:")

    elif step == "birth_date":
        try:
            birth_date = datetime.strptime(text, "%Y-%m-%d").date()
            state["birth_date"] = str(birth_date)
            state["step"] = "year"
            await message.answer("📅 Вкажіть рік випуску (наприклад, 2022):")
        except ValueError:
            await message.answer("❗ Невірний формат. Введіть дату у форматі РРРР-ММ-ДД.")
        return
    
    elif step == "year":
        if not text.isdigit():
            await message.answer("❗ Введіть рік у числовому форматі.")
            return
        state["year"] = int(text)
        state["step"] = "department"
        await message.answer("🏫 Введіть назву або скорочення кафедри (наприклад, ТЕФ):")

    elif step == "department":
        department_name = normalize_department(text)
        if not department_name:
            await message.answer("⚠️ Не вдалося розпізнати кафедру. Спробуйте ще раз.")
            return

        conn = sqlite3.connect("alumni.db")
        c = conn.cursor()
        c.execute("SELECT id FROM departments WHERE name = ?", (department_name,))
        row = c.fetchone()
        conn.close()

        if not row:
            await message.answer("📛 Кафедра не знайдена в базі.")
            return

        state["department_id"] = row[0]
        state["step"] = "specialty"
        await message.answer("📘 Введіть код або частину назви спеціальності:")

    elif step == "specialty":
        matches = search_specialty(text)
        if not matches:
            await message.answer("❌ Спеціальність не знайдена. Спробуйте ще раз.")
            return
        elif len(matches) > 1:
            options = "".join([f"{m['code']} – {m['name']}" for m in matches])
            await message.answer(f"🔍 Знайдено декілька:{options}\nВведіть точніше:")
            return

        specialty = matches[0]
        conn = sqlite3.connect("alumni.db")
        c = conn.cursor()
        c.execute("SELECT id FROM specialties WHERE code = ? AND name = ?", (specialty['code'], specialty['name']))
        row = c.fetchone()
        if not row:
            await message.answer("❗ Не знайдено спеціальність у базі.")
            return


        specialty_id = row[0]
        c.execute('''
            INSERT OR IGNORE INTO users (telegram_id, full_name, graduation_year, department_id, specialty_id, role, birth_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(message.from_user.id),
            state['name'],
            state['year'],
            state['department_id'],
            specialty_id,
            state['role'],
            state['birth_date']
        ))
        conn.commit()
        conn.close()

        await message.answer(
            f"📝 Ви зареєстровані як:"
            f"👤 Ім’я: <b>{state['name']}</b>"
            f"📅 Рік випуску: <b>{state['year']}</b>"
            f"🏛 Кафедра ID: <b>{state['department_id']}</b>"
            f"📘 Спеціальність ID: <b>{specialty_id}</b>"
            f"🔐 Роль: <b>{state['role']}</b>"
            "❓ Бажаєте змінити ці дані? Введіть /start для повторної реєстрації або оберіть дію нижче ⬇️"
        )

        del user_state[chat_id]

        await message.answer(
            f"🎉 Дякуємо за реєстрацію, <b>{state['name']}</b>!"
            f"🔽 Оберіть, що бажаєте зробити далі:",
            reply_markup=main_menu_keyboard()
        )

        if state["role"] == "admin":
            await message.answer("🔧 Ви авторизовані як адміністратор. Введіть /admin_panel щоб відкрити панель керування.")

