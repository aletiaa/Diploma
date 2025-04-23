import sqlite3
from aiogram import types
from datetime import datetime
from ...utils.specialties import search_specialty
from ...utils.department_recogniser import normalize_department
from ...utils.keyboard import contact_request_keyboard, main_menu_keyboard
from ...utils.phone_validator import is_valid_phone
from ..registration.state import user_state


async def handle_contact(message: types.Message, role: str):
    chat_id = message.chat.id
    contact = message.contact.phone_number

    if chat_id not in user_state:
        user_state[chat_id] = {"step": "ask_old_number", "role": role}

    state = user_state[chat_id]
    state["phone_number"] = contact
    state["step"] = "ask_old_number"

    await message.answer("📩 Дякуємо! Ваш номер отримано.\n"
                         "Чи мали ви цей номер під час навчання?\n"
                         "Введіть <b>так</b> або <b>ні</b>:",
                         reply_markup=types.ReplyKeyboardRemove())


async def ask_for_phone_number(message: types.Message):
    chat_id = message.chat.id
    user_state[chat_id]["step"] = "phone_number"
    await message.answer("📱 Вкажіть ваш номер телефону (або натисніть кнопку нижче):",
                         reply_markup=contact_request_keyboard())


async def ask_about_old_number(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip().lower()
    state = user_state[chat_id]

    if text not in ["так", "ні"]:
        await message.answer("❗ Введіть лише <b>так</b> або <b>ні</b>.")
        return

    if text == "так":
        state["old_phone_number"] = state["phone_number"]
        state["step"] = "birth_date"
        await message.answer("🎂 Вкажіть дату народження у форматі РРРР-ММ-ДД:")
    else:
        state["step"] = "enter_old_number"
        await message.answer("📞 Введіть ваш <b>старий</b> номер телефону, який ви використовували під час навчання:")


async def ask_old_number_directly(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_state[chat_id]

    if not is_valid_phone(text):
        await message.answer("❗ Невірний формат номера. Спробуйте ще раз.")
        return

    state["old_phone_number"] = text
    state["step"] = "birth_date"
    await message.answer("🎂 Вкажіть дату народження у форматі РРРР-ММ-ДД:")


async def ask_birth_date(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_state[chat_id]

    try:
        birth_date = datetime.strptime(text, "%Y-%m-%d").date()
        state["birth_date"] = str(birth_date)
        state["step"] = "year"
        await message.answer("📅 Вкажіть рік випуску (наприклад, 2022):")
    except ValueError:
        await message.answer("❗ Невірний формат. Спробуйте ще раз (РРРР-ММ-ДД):")


async def ask_graduation_year(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_state[chat_id]

    if not text.isdigit():
        await message.answer("❗ Введіть рік у числовому форматі.")
        return

    state["year"] = int(text)
    state["step"] = "department"
    await message.answer("🏫 Введіть назву або скорочення кафедри (наприклад, ТЕФ):")


async def ask_department(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_state[chat_id]

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


async def ask_specialty(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_state[chat_id]

    matches = search_specialty(text)
    if not matches:
        await message.answer("❌ Спеціальність не знайдена. Спробуйте ще раз.")
        return
    elif len(matches) > 1:
        options = "\n".join([f"{m['code']} – {m['name']}" for m in matches])
        await message.answer(f"🔍 Знайдено декілька:\n{options}\nВведіть точніше:")
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
    state["specialty_id"] = specialty_id
    state["step"] = "finalize"
    await finalize_registration(message)


async def finalize_registration(message: types.Message):
    chat_id = message.chat.id
    state = user_state[chat_id]

    conn = sqlite3.connect("alumni.db")
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO users 
        (telegram_id, full_name, phone_number, old_phone_number, graduation_year, department_id, specialty_id, role, birth_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        str(message.from_user.id),
        state["name"],
        state["phone_number"],
        state.get("old_phone_number", ""),
        state["year"],
        state["department_id"],
        state["specialty_id"],
        state["role"],
        state["birth_date"]
    ))
    conn.commit()
    conn.close()

    # Отримати назву кафедри
    conn = sqlite3.connect("alumni.db")
    c = conn.cursor()
    c.execute("SELECT name FROM departments WHERE id = ?", (state["department_id"],))
    department_name = c.fetchone()[0]

    # Отримати назву спеціальності
    c.execute("SELECT name FROM specialties WHERE id = ?", (state["specialty_id"],))
    specialty_name = c.fetchone()[0]
    conn.close()

    await message.answer(
        f"📝 Ви зареєстровані як:\n"
        f"👤 Ім’я: <b>{state['name']}</b>\n"
        f"📱 Телефон: <b>{state['phone_number']}</b>\n"
        f"📅 Рік випуску: <b>{state['year']}</b>\n"
        f"🏛 Кафедра: <b>{department_name}</b>\n"
        f"📘 Спеціальність: <b>{specialty_name}</b>\n"
        f"🔐 Роль: <b>{state['role']}</b>\n\n"
        "❓ Бажаєте змінити ці дані? Введіть /start для повторної реєстрації або оберіть дію нижче ⬇️"
    )

    del user_state[chat_id]

    await message.answer(
        f"🎉 Дякуємо за реєстрацію, <b>{state['name']}</b>!\n"
        f"🔽 Оберіть, що бажаєте зробити далі:",
        reply_markup=main_menu_keyboard()
    )

    if state["role"] == "admin":
        await message.answer("🔧 Ви авторизовані як адміністратор. Введіть /admin_panel щоб відкрити панель керування.")
