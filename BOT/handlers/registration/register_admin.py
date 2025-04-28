import sqlite3
import random
import string
import re
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from ...database.queries import get_connection

# Підключення до БД
conn = get_connection()
cursor = conn.cursor()

router = Router()

# Стани для реєстрації адміна
class AdminRegistration(StatesGroup):
    full_name = State()
    phone_number = State()

# Генерація рандомного паролю
def generate_random_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Старт реєстрації адміна
@router.message(Command('register_admin'))
async def start_admin_register(message: Message, state: FSMContext):
    await message.answer("Реєстрація адміністратора.\nВведіть ваше повне ім'я:")
    await state.set_state(AdminRegistration.full_name)

@router.message(AdminRegistration.full_name)
async def admin_full_name(message: Message, state: FSMContext):
    full_name = message.text.strip()

    if not re.match(r"^[А-Яа-яІіЇїЄєҐґA-Za-z]+ [А-Яа-яІіЇїЄєҐґA-Za-z]+$", full_name):
        await message.answer("❌ Ім'я повинно містити тільки літери і складатися з двох слів (наприклад: Іван Петренко). Введіть ще раз:")
        return

    await state.update_data(full_name=full_name)
    await message.answer("Введіть ваш номер телефону:")
    await state.set_state(AdminRegistration.phone_number)

@router.message(AdminRegistration.phone_number)
async def admin_phone_number(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    data = await state.get_data()

    # Генеруємо пароль
    password = generate_random_password()

    try:
        cursor.execute('''
            INSERT INTO admins (
                telegram_id, full_name, phone_number, password
            ) VALUES (?, ?, ?, ?)
        ''', (
            str(message.from_user.id),
            data['full_name'],
            data['phone_number'],
            password
        ))
        conn.commit()
        await message.answer(f"Адміністратор зареєстрований успішно!\nВаш пароль для входу: {password}")
    except sqlite3.IntegrityError:
        await message.answer("Ви вже зареєстровані як адміністратор.")
    await state.clear()
