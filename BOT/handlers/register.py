from aiogram import Router, types
from aiogram.filters import Command
import sqlite3
from ..utils.specialties import search_specialty
from ..utils.department_recogniser import normalize_department
from ..utils.keyboard import main_menu_keyboard

router = Router()
user_state = {}

@router.message(Command("start"))
async def start(message: types.Message):
    user_state[message.chat.id] = {"step": "name"}
    await message.answer("👋 Привіт! Почнемо реєстрацію.\n\nВкажіть ваше ім’я та прізвище:")

@router.message()
async def registration(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_state:
        return

    state = user_state[chat_id]
    step = state.get("step")

    if step == "name":
        state["name"] = text
        state["step"] = "year"
        await message.answer("📅 Вкажіть рік випуску (наприклад, 2022):")

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
            await message.answer(f"🔍 Знайдено декілька: {options} \n Введіть точніше:")
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
            INSERT OR IGNORE INTO users (telegram_id, full_name, graduation_year, department_id, specialty_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            str(message.from_user.id),
            state['name'],
            state['year'],
            state['department_id'],
            specialty_id
        ))
        conn.commit()
        conn.close()
        del user_state[chat_id]

        await message.answer(
            f"🎉 Дякуємо за реєстрацію, <b>{state['name']}</b>!"
            f"🔽 Оберіть, що бажаєте зробити далі:",
            reply_markup=main_menu_keyboard()
        )