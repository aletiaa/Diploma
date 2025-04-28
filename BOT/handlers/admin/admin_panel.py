import sqlite3
from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from ...utils.phone_validator import is_valid_phone
from ...utils.keyboard import admin_main_menu_keyboard, view_users_sort_keyboard

router = Router()

# Стани для адмін дій
class AdminPanelStates(StatesGroup):
    waiting_phone_to_delete = State()
    waiting_phone_to_block = State()
    waiting_phone_to_change_access = State()
    waiting_new_access_level = State()

# Після входу – показати адмін-панель
async def show_admin_panel(message: Message | CallbackQuery, state: FSMContext):
    text = "🔧 <b>Адмін-панель:</b>\nОберіть дію нижче:"
    try:
        if isinstance(message, CallbackQuery):
            await message.message.edit_text(text, reply_markup=admin_main_menu_keyboard, parse_mode="HTML")
        else:
            await message.answer(text, reply_markup=admin_main_menu_keyboard, parse_mode="HTML")
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await state.clear()

# 📊 Показати варіанти сортування користувачів
@router.callback_query(lambda c: c.data == "view_users")
async def view_users_sort_menu(callback_query: CallbackQuery, state: FSMContext):
    try:
        await callback_query.message.edit_text("📊 Виберіть спосіб сортування користувачів:", reply_markup=view_users_sort_keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise

# 🎓 Сортування за групою
@router.callback_query(lambda c: c.data == "view_users_group")
async def view_users_by_group(callback_query: CallbackQuery, state: FSMContext):
    conn = sqlite3.connect("alumni.db")
    c = conn.cursor()
    c.execute("SELECT full_name, phone_number, group_name, role FROM users ORDER BY group_name ASC")
    users = c.fetchall()
    conn.close()

    text = format_user_list(users, "🎓 Користувачі за групами")

    try:
        await callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=view_users_sort_keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise

# 📅 Сортування за роком випуску
@router.callback_query(lambda c: c.data == "view_users_year")
async def view_users_by_year(callback_query: CallbackQuery, state: FSMContext):
    conn = sqlite3.connect("alumni.db")
    c = conn.cursor()
    c.execute("SELECT full_name, phone_number, graduation_year, role FROM users ORDER BY graduation_year DESC")
    users = c.fetchall()
    conn.close()

    if not users:
        text = "❌ Жодного користувача не знайдено."
    else:
        text = "\n".join([f"👤 {u[0]} | 📱 {u[1]} | 📅 {u[2]} | 🔑 {u[3]}" for u in users])
        text = f"📅 <b>Користувачі за роком випуску:</b>\n\n{text}"

    try:
        await callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=view_users_sort_keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise

# 📘 Сортування за спеціальністю + роком
@router.callback_query(lambda c: c.data == "view_users_specialty")
async def view_users_by_specialty(callback_query: CallbackQuery, state: FSMContext):
    conn = sqlite3.connect("alumni.db")
    c = conn.cursor()
    c.execute('''
        SELECT u.full_name, u.phone_number, s.name, u.graduation_year, u.role
        FROM users u
        JOIN specialties s ON u.specialty_id = s.id
        ORDER BY s.name ASC, u.graduation_year DESC
    ''')
    users = c.fetchall()
    conn.close()

    if not users:
        text = "❌ Жодного користувача не знайдено."
    else:
        text = "\n".join([f"👤 {u[0]} | 📱 {u[1]} | 📘 {u[2]} | 📅 {u[3]} | 🔑 {u[4]}" for u in users])
        text = f"📘 <b>Користувачі за спеціальністю:</b>\n\n{text}"

    try:
        await callback_query.message.edit_text(text, parse_mode="HTML", reply_markup=view_users_sort_keyboard)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise

# Форматування списку
def format_user_list(users, title):
    if not users:
        return "❌ Жодного користувача не знайдено."
    user_list = "\n".join([f"👤 {u[0]} | 📱 {u[1]} | 🎓 {u[2]} | 🔑 {u[3]}" for u in users])
    return f"👥 <b>{title}:</b>\n\n{user_list}"

# ❌ Видалити користувача
@router.callback_query(lambda c: c.data == "delete_user")
async def delete_user_prompt(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("📱 Введіть номер телефону користувача, якого потрібно видалити:")
    await state.set_state(AdminPanelStates.waiting_phone_to_delete)

@router.message(AdminPanelStates.waiting_phone_to_delete)
async def delete_user_confirm(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not is_valid_phone(phone):
        await message.answer("❌ Невірний формат телефону.")
        return

    if not user_exists_by_phone(phone):
        await message.answer("❌ Користувача з таким номером не знайдено.")
    else:
        conn = sqlite3.connect("alumni.db")
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE phone_number = ?", (phone,))
        conn.commit()
        conn.close()
        await message.answer("✅ Користувача успішно видалено.")

    await show_admin_panel(message, state)

# 🚫 Заблокувати
@router.callback_query(lambda c: c.data == "block_user")
async def block_user_prompt(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("📱 Введіть номер телефону користувача, якого потрібно заблокувати:")
    await state.set_state(AdminPanelStates.waiting_phone_to_block)

@router.message(AdminPanelStates.waiting_phone_to_block)
async def block_user_confirm(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not is_valid_phone(phone):
        await message.answer("❌ Невірний формат телефону.")
        return

    if not user_exists_by_phone(phone):
        await message.answer("❌ Користувача з таким номером не знайдено.")
    else:
        conn = sqlite3.connect("alumni.db")
        c = conn.cursor()
        c.execute("UPDATE users SET role = 'blocked' WHERE phone_number = ?", (phone,))
        conn.commit()
        conn.close()
        await message.answer("🚫 Користувача заблоковано.")

    await show_admin_panel(message, state)

# 🔐 Змінити доступ
@router.callback_query(lambda c: c.data == "change_access")
async def change_access_prompt(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("📱 Введіть номер телефону користувача, чий доступ потрібно змінити:")
    await state.set_state(AdminPanelStates.waiting_phone_to_change_access)

@router.message(AdminPanelStates.waiting_phone_to_change_access)
async def change_access_level(message: Message, state: FSMContext):
    phone = message.text.strip()
    await state.update_data(phone=phone)
    if not user_exists_by_phone(phone):
        await message.answer("❌ Користувача не знайдено.")
        await show_admin_panel(message, state)
    else:
        await message.answer("🔐 Введіть новий рівень доступу ('user', 'admin_limited', 'admin_super'):")
        await state.set_state(AdminPanelStates.waiting_new_access_level)

@router.message(AdminPanelStates.waiting_new_access_level)
async def confirm_access_change(message: Message, state: FSMContext):
    access = message.text.strip()
    data = await state.get_data()
    phone = data.get("phone")

    if access not in {"user", "admin_limited", "admin_super"}:
        await message.answer("❌ Недійсний рівень доступу. Спробуйте ще раз.")
        return

    conn = sqlite3.connect("alumni.db")
    c = conn.cursor()
    c.execute("UPDATE users SET access_level = ? WHERE phone_number = ?", (access, phone))
    conn.commit()
    conn.close()

    await message.answer(f"✅ Доступ користувача змінено на: {access}")
    await show_admin_panel(message, state)

# Перевірка існування користувача за телефоном
def user_exists_by_phone(phone_number: str) -> bool:
    conn = sqlite3.connect("alumni.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE phone_number = ?", (phone_number,))
    exists = c.fetchone() is not None
    conn.close()
    return exists
