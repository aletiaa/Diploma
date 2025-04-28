import re
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from ...utils.phone_validator import is_valid_phone
from ...database.queries import get_connection
from ...utils.keyboard import admin_main_menu_keyboard, edit_admin_profile_keyboard

router = Router()

# Стани для редагування профілю адміністратора
class EditAdminProfile(StatesGroup):
    choosing_field = State()
    editing_full_name = State()
    editing_phone_number = State()
    editing_password = State()

# 📋 Меню редагування адміністратора (CallbackQuery)
@router.callback_query(lambda c: c.data == "edit_admin")
async def show_edit_admin_profile_menu_callback(callback_query: CallbackQuery, state: FSMContext):
    telegram_id = str(callback_query.from_user.id)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT full_name, phone_number FROM admins WHERE telegram_id = ?', (telegram_id,))
    admin_data = cursor.fetchone()
    conn.close()

    if admin_data:
        full_name, phone = admin_data
        text = (
            f"📋 <b>Ваші дані (Адміністратор):</b>\n"
            f"👤 ПІБ: {full_name}\n"
            f"📱 Телефон: {phone}\n\n"
            f"Що саме ви хочете змінити?"
        )
    else:
        text = "❌ Дані адміністратора не знайдено."

    await callback_query.message.edit_text(text, reply_markup=edit_admin_profile_keyboard, parse_mode="HTML")
    await state.set_state(EditAdminProfile.choosing_field)

# 📋 Меню після змін (Message)
async def show_edit_admin_profile_menu_message(message: Message, state: FSMContext):
    telegram_id = str(message.from_user.id)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT full_name, phone_number FROM admins WHERE telegram_id = ?', (telegram_id,))
    admin_data = cursor.fetchone()
    conn.close()

    if admin_data:
        full_name, phone = admin_data
        text = (
            f"📋 <b>Ваші дані (Адміністратор):</b>\n"
            f"👤 ПІБ: {full_name}\n"
            f"📱 Телефон: {phone}\n\n"
            f"Що саме ви хочете змінити?"
        )
    else:
        text = "❌ Дані адміністратора не знайдено."

    await message.answer(text, reply_markup=edit_admin_profile_keyboard, parse_mode="HTML")
    await state.set_state(EditAdminProfile.choosing_field)

# ⬅️ Повернення до головного меню адміна
@router.callback_query(lambda c: c.data == "back_to_admin_menu")
async def back_to_admin_menu(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("⬅️ Повернулись до головного меню адміністратора.", reply_markup=admin_main_menu_keyboard)
    await state.clear()

# Обробка вибору поля редагування
@router.callback_query(lambda c: c.data.startswith("edit_admin_"))
async def choose_admin_field_to_edit(callback_query: CallbackQuery, state: FSMContext):
    action = callback_query.data

    if action == "edit_admin_full_name":
        await callback_query.message.answer("Введіть нове ПІБ (2 слова, тільки літери):")
        await state.set_state(EditAdminProfile.editing_full_name)

    elif action == "edit_admin_phone_number":
        await callback_query.message.answer("Введіть новий номер телефону:")
        await state.set_state(EditAdminProfile.editing_phone_number)

    elif action == "edit_admin_password":
        await callback_query.message.answer("Введіть новий пароль:")
        await state.set_state(EditAdminProfile.editing_password)

# ✏️ Зміна ПІБ
@router.message(EditAdminProfile.editing_full_name)
async def edit_admin_full_name(message: Message, state: FSMContext):
    new_name = message.text.strip()
    if not re.match(r"^[А-Яа-яІіЇїЄєҐґA-Za-z]+ [А-Яа-яІіЇїЄєҐґA-Za-z]+$", new_name):
        await message.answer("❌ Ім'я повинно містити тільки літери і складатися з двох слів. Спробуйте ще раз:")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE admins SET full_name = ? WHERE telegram_id = ?', (new_name, str(message.from_user.id)))
    conn.commit()
    conn.close()

    await message.answer("✅ ПІБ оновлено!")
    await show_edit_admin_profile_menu_message(message, state)

# 📱 Зміна телефону
@router.message(EditAdminProfile.editing_phone_number)
async def edit_admin_phone_number(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not is_valid_phone(phone):
        await message.answer("❌ Неправильний номер. Введіть ще раз:")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE admins SET phone_number = ? WHERE telegram_id = ?', (phone, str(message.from_user.id)))
    conn.commit()
    conn.close()

    await message.answer("✅ Номер телефону оновлено!")
    await show_edit_admin_profile_menu_message(message, state)

# 🔐 Зміна пароля
@router.message(EditAdminProfile.editing_password)
async def edit_admin_password(message: Message, state: FSMContext):
    new_password = message.text.strip()
    if len(new_password) < 4:
        await message.answer("❌ Пароль має бути щонайменше 4 символи. Введіть ще раз:")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE admins SET password = ? WHERE telegram_id = ?', (new_password, str(message.from_user.id)))
    conn.commit()
    conn.close()

    await message.answer("✅ Пароль оновлено!")
    await show_edit_admin_profile_menu_message(message, state)