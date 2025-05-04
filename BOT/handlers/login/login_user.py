import re
import sqlite3
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
from ...utils.phone_validator import is_valid_phone
from ...database.queries import get_connection
from ...utils.keyboard import user_main_menu_keyboard

router = Router()

# Стейти для логіну
class UserLogin(StatesGroup):
    phone_number = State()
    group_name = State()
    attempts = State()

# Старт логіну
@router.message(Command("login_user"))
async def start_user_login(message: Message, state: FSMContext):
    await state.update_data(attempts=3)  # 3 спроби
    await message.answer("Введіть ваш номер телефону для входу:")
    await state.set_state(UserLogin.phone_number)

# Обробка номера телефону
@router.message(UserLogin.phone_number)
async def process_login_phone(message: Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone = message.text.strip()
    else:
        await message.answer("Надішліть номер телефону як текст або контакт.")
        return

    if not is_valid_phone(phone):
        await message.answer("Неправильний номер телефону. Введіть ще раз:")
        return

    await state.update_data(phone_number=phone)
    await message.answer("🔢 Введіть вашу групу (наприклад: ТВ-12):")
    await state.set_state(UserLogin.group_name)

@router.message(UserLogin.group_name)
async def process_login_group(message: Message, state: FSMContext):
    group = message.text.strip().upper()

    if not re.match(r"^[А-ЯA-Z]{2}-\d{2}$", group):
        await message.answer("Група повинна бути у форматі: 2 літери, тире, 2 цифри (наприклад: ТВ-12). Введіть ще раз:")
        return

    data = await state.get_data()
    phone = data['phone_number']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id, full_name, failed_attempts, last_failed_login_time FROM users WHERE phone_number = ? AND group_name = ?', (phone, group))
    user = cursor.fetchone()

    if user:
        user_id, full_name, attempts, last_failed = user

        # Перевірка часу блокування
        if attempts >= 3 and last_failed:
            last_dt = datetime.strptime(last_failed, "%Y-%m-%d %H:%M:%S")
            if datetime.now() - last_dt < timedelta(seconds=30):
                left = 30 - int((datetime.now() - last_dt).total_seconds())
                await message.answer(f"⏳ Ви тимчасово заблоковані. Спробуйте через {left} секунд.")
                return
            else:
                # Розблокування
                cursor.execute("UPDATE users SET failed_attempts = 0, last_failed_login_time = NULL WHERE id = ?", (user_id,))
                conn.commit()

        # Успішний вхід
        await message.answer(f"✅ Вхід успішний! Вітаю, {full_name}!", reply_markup=user_main_menu_keyboard)
        cursor.execute("UPDATE users SET failed_attempts = 0, last_failed_login_time = NULL WHERE id = ?", (user_id,))
        conn.commit()
        await state.clear()
    else:
        # Невдалий вхід – шукаємо користувача за номером телефону
        cursor.execute("SELECT id, failed_attempts FROM users WHERE phone_number = ?", (phone,))
        record = cursor.fetchone()
        if record:
            user_id, attempts = record
            attempts = attempts + 1
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE users SET failed_attempts = ?, last_failed_login_time = ? WHERE id = ?", (attempts, now, user_id))
            conn.commit()
        await message.answer("❌ Дані не знайдено або група не збігається. Спробуйте ще раз.")
        await state.set_state(UserLogin.phone_number)

    conn.close()
