import sqlite3
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from ...utils.phone_validator import is_valid_phone
from ...database.queries import get_connection
from ...utils.keyboard import admin_main_menu_keyboard

router = Router()

# Стейти для логіну адміна
class AdminLogin(StatesGroup):
    phone_number = State()
    password = State()
    attempts = State()

# Старт логіну адміна
@router.message(Command("login_admin"))
async def start_admin_login(message: Message, state: FSMContext):
    await state.update_data(attempts=3)
    await message.answer("📲 Введіть ваш номер телефону для входу:")
    await state.set_state(AdminLogin.phone_number)

# Обробка номера телефону
@router.message(AdminLogin.phone_number)
async def process_admin_phone(message: Message, state: FSMContext):
    phone = message.text.strip()

    if not is_valid_phone(phone):
        await message.answer("❌ Неправильний номер телефону. Введіть ще раз:")
        return

    await state.update_data(phone_number=phone)
    await message.answer("🔐 Введіть ваш пароль:")
    await state.set_state(AdminLogin.password)

# Обробка пароля
@router.message(AdminLogin.password)
async def process_admin_password(message: Message, state: FSMContext):
    password_input = message.text.strip()
    data = await state.get_data()
    phone = data['phone_number']
    attempts_left = data.get('attempts', 3)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, full_name, password FROM admins
        WHERE phone_number = ?
    ''', (phone,))
    admin = cursor.fetchone()
    conn.close()

    if admin and admin[2] == password_input:
        await message.answer(f"✅ Вхід успішний! Вітаю, {admin[1]} (адміністратор).", reply_markup=admin_main_menu_keyboard)
        await state.clear()
    else:
        attempts_left -= 1
        if attempts_left <= 0:
            await message.answer("❌ Вичерпано кількість спроб. Спробуйте пізніше.")
            await state.clear()
        else:
            await state.update_data(attempts=attempts_left)
            await message.answer(f"❌ Неправильний пароль або номер телефону.\nЗалишилось спроб: {attempts_left}.\n\nВведіть номер телефону ще раз:")
            await state.set_state(AdminLogin.phone_number)
