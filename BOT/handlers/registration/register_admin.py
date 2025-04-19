from aiogram import Router, types
from aiogram.filters import Command
from ...utils.keyboard import contact_request_keyboard, main_menu_keyboard
from ...utils.phone_validator import is_valid_phone
from .state import user_state
from .shared_registration_steps import (
    handle_contact,
    ask_for_phone_number,
    ask_about_old_number,
    ask_old_number_directly,
    ask_birth_date,
    ask_graduation_year,
    ask_department,
    ask_specialty,
    finalize_registration
)

import sqlite3
import json
from ...config import ADMIN_PASSWORD, ADMIN_TELEGRAM_IDS

router = Router()

@router.message(Command("start"))
async def start_admin(message: types.Message):
    chat_id = message.chat.id
    user_state[chat_id] = {"step": "start_choice"}
    await message.answer(
        "🔐 Вітаємо! Оберіть дію:\n"
        "<b>Реєстрація</b> – якщо ви тут вперше\n"
        "<b>Вхід</b> – якщо ви вже зареєстровані\n\n"
        "Введіть <b>реєстрація</b> або <b>вхід</b>:"
    )


@router.message(lambda message: message.contact is not None)
async def contact_handler(message: types.Message):
    return await handle_contact(message, role="admin")


@router.message()
async def admin_registration(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_state.get(chat_id)

    if not state:
        return

    step = state.get("step")

    if step == "start_choice":
        if text.lower() in ["реєстрація", "р"]:
            state["step"] = "admin_password"
            await message.answer("🔐 Введіть пароль адміністратора:")
        elif text.lower() in ["вхід", "в"]:
            state["step"] = "login_name"
            await message.answer("Введіть ваше прізвище:")
        else:
            await message.answer("❗ Введіть лише <b>реєстрація</b> або <b>вхід</b>.")

    elif step == "login_name":
        state["login_surname"] = text
        state["step"] = "login_phone"
        await message.answer("Введіть номер телефону, який ви вказували при реєстрації:")

    elif step == "login_phone":
        phone = text
        conn = sqlite3.connect("alumni.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE full_name LIKE ? AND phone_number = ?", (f"%{state['login_surname']}%", phone))
        user = c.fetchone()
        conn.close()

        if not user or user[-3] != "admin":
            await message.answer("❌ Адміністратора не знайдено або це не адміністратор.")
            return

        state["step"] = "admin_password_login"
        state["login_user"] = user
        await message.answer("🔐 Введіть пароль адміністратора:")

    elif step == "admin_password_login":
        if text != ADMIN_PASSWORD:
            await message.answer("❌ Невірний пароль адміністратора.")
            return

        await message.answer("✅ Вхід підтверджено. Ви увійшли як адміністратор.",
                             reply_markup=main_menu_keyboard())
        del user_state[chat_id]

    elif step == "admin_password":
        if text == ADMIN_PASSWORD:
            if chat_id not in ADMIN_TELEGRAM_IDS:
                ADMIN_TELEGRAM_IDS.append(chat_id)
                try:
                    with open("admin_log.json", "r", encoding="utf-8") as f:
                        current_data = json.load(f)
                except:
                    current_data = {"admins": []}
                current_data["admins"].append(chat_id)
                with open("admin_log.json", "w", encoding="utf-8") as f:
                    json.dump(current_data, f, ensure_ascii=False, indent=2)

            state["role"] = "admin"
            state["step"] = "name"
            await message.answer("✅ Пароль підтверджено. Вкажіть ваше ім’я та прізвище:")
        else:
            await message.answer("❌ Невірний пароль. Спробуйте ще раз.")

    elif step == "name":
        state["name"] = text
        return await ask_for_phone_number(message)

    elif step == "phone_number":
        if not is_valid_phone(text):
            await message.answer("❗ Невірний формат номера телефону або невідомий код країни. Спробуйте ще раз.")
            return
        state["phone_number"] = text
        state["step"] = "ask_old_number"
        await message.answer("📲 Чи мали ви цей номер під час навчання? Введіть <b>так</b> або <b>ні</b>.")

    elif step == "ask_old_number":
        await ask_about_old_number(message)

    elif step == "enter_old_number":
        await ask_old_number_directly(message)

    elif step == "birth_date":
        await ask_birth_date(message)

    elif step == "year":
        await ask_graduation_year(message)

    elif step == "department":
        await ask_department(message)

    elif step == "specialty":
        await ask_specialty(message)

    elif step == "finalize":
        await finalize_registration(message)
