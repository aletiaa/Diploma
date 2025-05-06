import sqlite3
import random
import string
import re
from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ...config import SUPER_ADMIN_ID
from ...database.queries import get_connection
from ...utils.phone_validator import is_valid_phone  
from ...utils.keyboard import request_phone_keyboard

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
        await message.answer("❌ Ім'я повинно містити лише літери і складатися з двох слів (наприклад: Іван Петренко). Спробуйте ще раз.")
        return
    await state.update_data(full_name=full_name)
    await message.answer("📞 Введіть номер телефону у міжнародному форматі (наприклад, +380501234567):", reply_markup=request_phone_keyboard)
    await state.set_state(AdminRegistration.phone_number)

@router.message(AdminRegistration.phone_number)
async def admin_phone_number(message: Message, state: FSMContext, bot: Bot):
    phone = message.contact.phone_number if message.contact else message.text.strip() if message.text else ""

    if not is_valid_phone(phone):
        await message.answer("❌ Невалідний номер. Введіть ще раз у форматі +380501234567:")
        return

    await message.answer("✅ Номер прийнято.", reply_markup=ReplyKeyboardRemove())
    
    await state.update_data(phone_number=phone)
    data = await state.get_data()
    password = generate_random_password()
    telegram_id = str(message.from_user.id)

    conn = get_connection()
    cursor = conn.cursor()

    # Чи вже є така заявка?
    cursor.execute("SELECT 1 FROM admin_requests WHERE telegram_id = ?", (telegram_id,))
    if cursor.fetchone():
        await message.answer("🕓 Ваша заявка вже на розгляді.")
        return

    try:
        cursor.execute("""
            INSERT INTO admin_requests (telegram_id, full_name, phone_number, password)
            VALUES (?, ?, ?, ?)
        """, (telegram_id, data["full_name"], phone, password))
        conn.commit()
    except sqlite3.IntegrityError:
        await message.answer("⚠️ Ви вже подали заявку або зареєстровані.")
        return

    await message.answer("✅ Заявку на реєстрацію адміністратора надіслано. Очікуйте підтвердження.")

    await bot.send_message(
        SUPER_ADMIN_ID,
        f"🛂 Нова заявка на адміністратора:\n"
        f"👤 Ім'я: {data['full_name']}\n📱 Телефон: {phone}\n🆔 Telegram ID: {telegram_id}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Прийняти", callback_data=f"approve_admin_{telegram_id}")],
            [InlineKeyboardButton(text="❌ Відхилити", callback_data=f"reject_admin_{telegram_id}")]
        ])
    )
    await state.clear()

# ✅ Схвалення суперадміністратором
@router.callback_query(lambda c: c.data.startswith("approve_admin_"))
async def approve_admin(callback: CallbackQuery, bot: Bot):
    telegram_id = callback.data.split("_")[-1]
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT full_name, phone_number, password FROM admin_requests WHERE telegram_id = ?", (telegram_id,))
    row = cursor.fetchone()
    if not row:
        await callback.message.answer("❌ Заявку не знайдено.")
        return

    full_name, phone_number, password = row

    cursor.execute("SELECT 1 FROM admins WHERE telegram_id = ?", (telegram_id,))
    if cursor.fetchone():
        await callback.message.answer("⚠️ Адміністратор вже існує.")
        return

    cursor.execute("""
        INSERT INTO admins (telegram_id, full_name, phone_number, password)
        VALUES (?, ?, ?, ?)
    """, (telegram_id, full_name, phone_number, password))
    cursor.execute("DELETE FROM admin_requests WHERE telegram_id = ?", (telegram_id,))
    conn.commit()

    await callback.message.answer("✅ Адміністратора підтверджено.")
    await bot.send_message(
        chat_id=telegram_id,
        text=(
            "🎉 Вас підтверджено як адміністратора!\n\n"
            f"👤 ПІБ: {full_name}\n📱 Телефон: {phone_number}\n"
            f"🔐 Ваш пароль: <code>{password}</code>\n\n"
            "Використовуйте цей пароль для авторизації.",
        ),
        parse_mode="HTML"
    )


# ❌ Відхилення заявки
@router.callback_query(lambda c: c.data.startswith("reject_admin_"))
async def reject_admin(callback: CallbackQuery, bot: Bot):
    telegram_id = callback.data.split("_")[-1]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admin_requests WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    await callback.message.answer("🚫 Заявку відхилено.")
    await bot.send_message(telegram_id, "❌ Ваша заявка на адміністратора була відхилена.")
