import json
import sqlite3
from aiogram import Router, types
from aiogram.filters import Command
from ...config import ADMIN_TELEGRAM_IDS, ADMIN_PASSWORD, SUPER_ADMIN_ID
from ...utils.keyboard import contact_request_keyboard, main_menu_keyboard
from .state import user_state
from .shared_registration_steps import (
    handle_contact, ask_for_phone_number, ask_about_old_number, ask_old_number_directly,
    ask_birth_date, ask_graduation_year, ask_department, ask_specialty, finalize_registration
)

router = Router()

@router.message(Command("start"))
async def start_admin_registration(message: types.Message):
    chat_id = message.chat.id
    user_state[chat_id] = {"step": "start_choice"}
    await message.answer(
        "🔰 Вітаємо! Оберіть дію:\n\n<b>Реєстрація</b> – якщо ви тут вперше\n<b>Вхід</b> – якщо ви вже зареєстровані\n\n"
        "Введіть <b>Реєстрація</b> або <b>Вхід</b>:"
    )

@router.message(lambda message: message.contact is not None)
async def handle_admin_contact(message: types.Message):
    return await handle_contact(message, role="admin")

@router.message()
async def admin_registration_flow(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_state.get(chat_id)

    if not state:
        return

    step = state.get("step")

    # Стартова логіка
    if step == "start_choice":
        if text.lower() in ["реєстрація", "р"]:
            state["step"] = "role_choice"
            await message.answer("Ви хочете увійти як 👤 Користувач чи 🔐 Адмін?\nВведіть <b>Користувач</b> або <b>Адмін</b>:")
        elif text.lower() in ["вхід", "в"]:
            state["step"] = "login_name"
            await message.answer("Введіть ваше прізвище:")
        else:
            await message.answer("❗ Введіть лише <b>Реєстрація</b> або <b>Вхід</b>.")

    elif step == "login_name":
        state["login_surname"] = text
        state["step"] = "login_phone"
        await message.answer("📱 Введіть номер телефону, який ви вказували при реєстрації:")

    elif step == "login_phone":
        phone = text
        conn = sqlite3.connect("alumni.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE full_name LIKE ? AND phone_number = ?", (f"%{state['login_surname']}%", phone))
        user = c.fetchone()
        conn.close()
        if not user:
            await message.answer("❌ Користувача не знайдено. Перевірте правильність даних або зареєструйтесь заново.")
            return
        if user[-3] == "admin":
            state["step"] = "admin_password_check"
            await message.answer("🔐 Введіть пароль адміністратора:")
        else:
            del user_state[chat_id]
            await message.answer("✅ Ви успішно увійшли як користувач!", reply_markup=main_menu_keyboard())

    # Обробка введення пароля для адмінів
    elif step in ["admin_password", "admin_password_check"]:
        if text != ADMIN_PASSWORD:
            await message.answer("❌ Невірний пароль. Спробуйте ще раз або введіть <b>Користувач</b> щоб увійти як звичайний користувач.")
            return

        if message.from_user.id not in ADMIN_TELEGRAM_IDS:
            ADMIN_TELEGRAM_IDS.append(message.from_user.id)
            try:
                with open("admin_log.json", "r", encoding="utf-8") as f:
                    current_data = json.load(f)
            except FileNotFoundError:
                current_data = {"admins": []}
            current_data["admins"].append(message.from_user.id)
            with open("admin_log.json", "w", encoding="utf-8") as f:
                json.dump(current_data, f, ensure_ascii=False, indent=2)

        state["role"] = "admin"
        # Уніфіковано присвоєння рівня
        state["admin_level"] = "super" if message.from_user.id == SUPER_ADMIN_ID else "limited"
        state["step"] = "name"
        await message.answer("✅ Пароль підтверджено. Вкажіть ваше ім’я та прізвище:")

    elif step == "role_choice":
        if text.lower() in ["admin", "адмін", "а"]:
            state["step"] = "admin_password"
            await message.answer("🔐 Введіть пароль адміністратора:")
        elif text.lower() in ["user", "користувач", "к"]:
            from . import register_user
            return await register_user.start(message)
        else:
            await message.answer("❗ Введіть лише <b>Користувач</b> або <b>Адмін</b>.")

    # Спільні кроки
    elif step == "name":
        state["name"] = text
        await ask_for_phone_number(message)

    elif step == "phone_number":
        from ...utils.phone_validator import is_valid_phone
        if not is_valid_phone(text):
            await message.answer("❗ Невірний формат номера телефону або невідомий код країни. Спробуйте ще раз.")
            return
        state["phone_number"] = text
        state["step"] = "ask_old_number"
        await message.answer("📲 Чи мали ви цей номер телефону ще під час навчання? Введіть <b>так</b> або <b>ні</b>.")

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
        await finalize_registration(message)