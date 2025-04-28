import re
import sqlite3
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
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
    await message.answer("📲 Введіть ваш номер телефону для входу:")
    await state.set_state(UserLogin.phone_number)

# Обробка номера телефону
@router.message(UserLogin.phone_number)
async def process_login_phone(message: Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    elif message.text:
        phone = message.text.strip()
    else:
        await message.answer("❌ Надішліть номер телефону як текст або контакт.")
        return

    if not is_valid_phone(phone):
        await message.answer("❌ Неправильний номер телефону. Введіть ще раз:")
        return

    await state.update_data(phone_number=phone)
    await message.answer("🔢 Введіть вашу групу (наприклад: ТВ-12):")
    await state.set_state(UserLogin.group_name)

# Обробка групи і перевірка логіну
@router.message(UserLogin.group_name)
async def process_login_group(message: Message, state: FSMContext):
    group = message.text.strip().upper()
    data = await state.get_data()
    attempts_left = data.get('attempts', 3)

    if not re.match(r"^[А-ЯA-Z]{2}-\d{2}$", group):
        await message.answer("❌ Група повинна бути у форматі: 2 літери, тире, 2 цифри (наприклад: ТВ-12). Введіть ще раз:")
        return

    phone = data['phone_number']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, full_name FROM users
        WHERE phone_number = ? AND group_name = ?
    ''', (phone, group))
    user = cursor.fetchone()
    conn.close()

    if user:
        await message.answer(f"✅ Вхід успішний! Вітаю, {user[1]}!", reply_markup=user_main_menu_keyboard)
        await state.clear()
    else:
        attempts_left -= 1
        if attempts_left <= 0:
            await message.answer("❌ Вичерпано кількість спроб. Спробуйте пізніше.")
            await state.clear()
        else:
            await state.update_data(attempts=attempts_left)
            await message.answer(f"❌ Дані не знайдено. Залишилось спроб: {attempts_left}.\n\nВведіть номер телефону ще раз:")
            await state.set_state(UserLogin.phone_number)
