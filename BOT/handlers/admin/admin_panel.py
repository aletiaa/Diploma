import secrets
import sqlite3
import string
from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from ...utils.phone_validator import is_valid_phone
from ...utils.keyboard import admin_main_menu_keyboard, view_users_sort_keyboard, user_management_keyboard, limited_admin_menu_keyboard
from ...database.queries import get_connection

router = Router()

# Стани для адмін дій
class AdminPanelStates(StatesGroup):
    waiting_phone_to_delete = State()
    waiting_phone_to_block = State()
    waiting_phone_to_change_access = State()
    waiting_new_access_level = State()

def get_admin_access_level(telegram_id: str) -> str | None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT access_level FROM admins WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def super_admin_only(func):
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        access_level = get_admin_access_level(str(callback.from_user.id))
        if access_level != "admin_super":
            await callback.message.answer("🚫 У вас немає прав для цієї дії.")
            return
        return await func(callback, *args, **kwargs)
    return wrapper

@router.callback_query(lambda c: c.data == "user_management_menu")
async def open_user_management_menu(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(
        "👥 <b>Робота з користувачами:</b>\nОберіть дію нижче:",
        reply_markup=user_management_keyboard,
        parse_mode="HTML"
    )

# Після входу – показати адмін-панель
@router.callback_query(lambda c: c.data == "login_admin_menu")
async def show_admin_menu(callback: CallbackQuery, state: FSMContext):
    telegram_id = str(callback.from_user.id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT access_level FROM admins WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        access_level = result[0]
        if access_level == "admin_super":
            await callback.message.answer("🔧 Адмін-панель (повний доступ):", reply_markup=admin_main_menu_keyboard)
        else:
            await callback.message.answer("👮 Адмін-панель (обмежений доступ):", reply_markup=limited_admin_menu_keyboard)
    else:
        await callback.message.answer("❌ Ви не авторизовані як адміністратор.")

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

    await show_admin_menu(message, state)

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

    await show_admin_menu(message, state)


# 🔐 Змінити доступ
@router.callback_query(lambda c: c.data == "change_access")
@super_admin_only
async def change_access_prompt(callback_query: CallbackQuery, state: FSMContext, **kwargs):
    await callback_query.message.answer("📱 Введіть номер телефону користувача, чий доступ потрібно змінити:")
    await state.set_state(AdminPanelStates.waiting_phone_to_change_access)


@router.message(AdminPanelStates.waiting_phone_to_change_access)
@super_admin_only
async def change_access_level(message: Message, state: FSMContext, **kwargs):
    phone = message.text.strip()
    await state.update_data(phone=phone)
    if not user_exists_by_phone(phone):
        await message.answer("❌ Користувача не знайдено.")
        await show_admin_menu(message, state)
    else:
        await message.answer("🔐 Введіть новий рівень доступу ('user', 'admin_limited', 'admin_super'):")
        await state.set_state(AdminPanelStates.waiting_new_access_level)


def generate_password(length: int = 8) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


@router.message(AdminPanelStates.waiting_new_access_level)
@super_admin_only
async def confirm_access_change(message: Message, state: FSMContext, **kwargs):
    access = message.text.strip()
    data = await state.get_data()
    phone = data.get("phone")

    if access not in {"user", "admin_limited", "admin_super"}:
        await message.answer("❌ Недійсний рівень доступу. Спробуйте ще раз.")
        return

    conn = sqlite3.connect("alumni.db")
    cursor = conn.cursor()

    # Отримуємо telegram_id користувача за номером
    cursor.execute("SELECT telegram_id, full_name FROM users WHERE phone_number = ?", (phone,))
    user_row = cursor.fetchone()

    if not user_row:
        await message.answer("❌ Користувача не знайдено.")
        conn.close()
        return

    telegram_id, full_name = user_row

    # Оновлюємо рівень доступу
    cursor.execute("UPDATE users SET access_level = ? WHERE phone_number = ?", (access, phone))

    if access == "user":
        cursor.execute("DELETE FROM admins WHERE telegram_id = ?", (telegram_id,))
        await message.answer("👤 Користувача переведено до звичайних користувачів.")
    else:
        cursor.execute("SELECT 1 FROM admins WHERE telegram_id = ?", (telegram_id,))
        if cursor.fetchone() is None:
            password = generate_password()
            cursor.execute(
                "INSERT INTO admins (telegram_id, phone_number, full_name, password, access_level) VALUES (?, ?, ?, ?, ?)",
                (telegram_id, phone, full_name, password, access)
            )
            await message.bot.send_message(
                chat_id=telegram_id,
                text=f"🔐 Вас призначено адміністратором.\nВаш пароль для входу: <code>{password}</code>",
                parse_mode="HTML"
            )
        else:
            cursor.execute("UPDATE admins SET access_level = ? WHERE telegram_id = ?", (access, telegram_id))
        conn.commit()
        conn.close()

        await message.answer(f"✅ Доступ користувача оновлено до: {access}")
        await show_admin_menu(message, state)

# Перевірка існування користувача за телефоном
def user_exists_by_phone(phone_number: str) -> bool:
    conn = sqlite3.connect("alumni.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE phone_number = ?", (phone_number,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

@router.callback_query(lambda c: c.data == "view_uploaded_files")
@super_admin_only
async def view_uploaded_files(callback: CallbackQuery, state: FSMContext, **kwargs):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT telegram_id, file_id, file_type, upload_time
        FROM user_files
        ORDER BY upload_time DESC
        LIMIT 10
    ''')
    files = cursor.fetchall()
    conn.close()

    if not files:
        await callback.message.answer("❌ Жодного файлу ще не надіслано.")
        return

    for idx, (user_id, file_id, file_type, upload_time) in enumerate(files, start=1):
        caption = f"#{idx} 📅 {upload_time}\n👤 Користувач: <code>{user_id}</code>"

        try:
            if file_type == "photo":
                await callback.message.bot.send_photo(chat_id=callback.from_user.id, photo=file_id, caption=caption, parse_mode="HTML")
            else:
                await callback.message.bot.send_message(chat_id=callback.from_user.id, text=f"{caption}\n🔗 Файл: {file_id}", parse_mode="HTML")
        except TelegramBadRequest as e:
            await callback.message.answer(f"⚠️ Помилка при відправленні файлу #{idx}.")

    await callback.message.answer("⬅️ Повертаємось до адмін-панелі.", reply_markup=admin_main_menu_keyboard)