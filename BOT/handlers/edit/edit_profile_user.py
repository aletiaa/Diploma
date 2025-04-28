import re
from datetime import datetime
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from ...utils.phone_validator import is_valid_phone
from ...utils.specialties import search_specialty
from ...database.queries import get_connection
from ...utils.keyboard import edit_profile_keyboard, user_main_menu_keyboard

router = Router()

# Стани
class EditProfile(StatesGroup):
    choosing_field = State()
    editing_full_name = State()
    editing_phone_number = State()
    editing_group_name = State()
    editing_specialty = State()
    editing_graduation_year = State()
    editing_birth_date = State()

# Меню після CallbackQuery
@router.callback_query(lambda c: c.data == "edit_profile")
async def show_edit_profile_menu_callback(callback_query: CallbackQuery, state: FSMContext):
    telegram_id = str(callback_query.from_user.id)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.full_name, u.phone_number, u.group_name, s.name, s.code, u.graduation_year, u.birth_date
        FROM users u
        LEFT JOIN specialties s ON u.specialty_id = s.id
        WHERE u.telegram_id = ?
    ''', (telegram_id,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        full_name, phone, group, specialty_name, specialty_code, grad_year, birth_date = user_data
        specialty_info = f"{specialty_name} ({specialty_code})" if specialty_name else "Не вказано"
        grad_year_info = grad_year if grad_year else "Не вказано"
        birth_date_info = birth_date if birth_date else "Не вказано"

        text = (
            f"📋 <b>Ваші дані:</b>\n"
            f"👤 ПІБ: {full_name}\n"
            f"📱 Телефон: {phone}\n"
            f"🎓 Група: {group}\n"
            f"📘 Спеціальність: {specialty_info}\n"
            f"📅 Рік випуску: {grad_year_info}\n"
            f"🎂 Дата народження: {birth_date_info}\n\n"
            f"Що саме ви хочете змінити?"
        )
    else:
        text = "❌ Дані не знайдено."

    await callback_query.message.edit_text(text, reply_markup=edit_profile_keyboard, parse_mode="HTML")
    await state.set_state(EditProfile.choosing_field)

# Меню після Message (після змін)
async def show_edit_profile_menu_message(message: Message, state: FSMContext):
    telegram_id = str(message.from_user.id)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.full_name, u.phone_number, u.group_name, s.name, s.code, u.graduation_year, u.birth_date
        FROM users u
        LEFT JOIN specialties s ON u.specialty_id = s.id
        WHERE u.telegram_id = ?
    ''', (telegram_id,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        full_name, phone, group, specialty_name, specialty_code, grad_year, birth_date = user_data
        specialty_info = f"{specialty_name} ({specialty_code})" if specialty_name else "Не вказано"
        grad_year_info = grad_year if grad_year else "Не вказано"
        birth_date_info = birth_date if birth_date else "Не вказано"

        text = (
            f"📋 <b>Ваші дані:</b>\n"
            f"👤 ПІБ: {full_name}\n"
            f"📱 Телефон: {phone}\n"
            f"🎓 Група: {group}\n"
            f"📘 Спеціальність: {specialty_info}\n"
            f"📅 Рік випуску: {grad_year_info}\n"
            f"🎂 Дата народження: {birth_date_info}\n\n"
            f"Що саме ви хочете змінити?"
        )
    else:
        text = "❌ Дані не знайдено."

    await message.answer(text, reply_markup=edit_profile_keyboard, parse_mode="HTML")
    await state.set_state(EditProfile.choosing_field)


# Повернення до головного меню користувача
@router.callback_query(lambda c: c.data == "back_to_user_menu")
async def back_to_user_menu(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("⬅️ Повернулись до головного меню.", reply_markup=user_main_menu_keyboard)
    await state.clear()

# Обробка натиснення кнопок редагування
@router.callback_query(lambda c: c.data.startswith("edit_"))
async def choose_field_to_edit(callback_query: CallbackQuery, state: FSMContext):
    action = callback_query.data

    if action == "edit_full_name":
        await callback_query.message.answer("Введіть нове ПІБ (2 слова, тільки літери):")
        await state.set_state(EditProfile.editing_full_name)

    elif action == "edit_phone_number":
        await callback_query.message.answer("Введіть новий номер телефону:")
        await state.set_state(EditProfile.editing_phone_number)

    elif action == "edit_group_name":
        await callback_query.message.answer("Введіть нову групу (наприклад: ТВ-12):")
        await state.set_state(EditProfile.editing_group_name)

    elif action == "edit_specialty":
        await callback_query.message.answer("Введіть код або частину назви спеціальності:")
        await state.set_state(EditProfile.editing_specialty)

    elif action == "edit_graduation_year":
        await callback_query.message.answer("Введіть новий рік випуску (наприклад: 2022):")
        await state.set_state(EditProfile.editing_graduation_year)

    elif action == "edit_birth_date":
        await callback_query.message.answer("Введіть нову дату народження (ДД.ММ.РРРР):")
        await state.set_state(EditProfile.editing_birth_date)

# Зміна ПІБ
@router.message(EditProfile.editing_full_name)
async def edit_full_name(message: Message, state: FSMContext):
    new_name = message.text.strip()
    if not re.match(r"^[А-Яа-яІіЇїЄєҐґA-Za-z]+ [А-Яа-яІіЇїЄєҐґA-Za-z]+$", new_name):
        await message.answer("❌ Ім'я повинно містити тільки літери і складатися з двох слів. Спробуйте ще раз:")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET full_name = ? WHERE telegram_id = ?', (new_name, str(message.from_user.id)))
    conn.commit()
    conn.close()

    await message.answer("✅ ПІБ оновлено!")
    await show_edit_profile_menu_message(message, state)

# Зміна телефону
@router.message(EditProfile.editing_phone_number)
async def edit_phone_number(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not is_valid_phone(phone):
        await message.answer("❌ Неправильний номер. Введіть ще раз:")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET phone_number = ? WHERE telegram_id = ?', (phone, str(message.from_user.id)))
    conn.commit()
    conn.close()

    await message.answer("✅ Номер телефону оновлено!")
    await show_edit_profile_menu_message(message, state)

# Зміна групи
@router.message(EditProfile.editing_group_name)
async def edit_group_name(message: Message, state: FSMContext):
    group = message.text.strip().upper()
    if not re.match(r"^[А-ЯA-Z]{2}-\d{2}$", group):
        await message.answer("❌ Неправильний формат групи. Введіть ще раз (наприклад: ТВ-12):")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET group_name = ? WHERE telegram_id = ?', (group, str(message.from_user.id)))
    conn.commit()
    conn.close()

    await message.answer("✅ Групу оновлено!")
    await show_edit_profile_menu_message(message, state)

# Зміна спеціальності
@router.message(EditProfile.editing_specialty)
async def edit_specialty(message: Message, state: FSMContext):
    user_input = message.text.strip()
    matches = search_specialty(user_input)

    if not matches:
        await message.answer("❌ Спеціальність не знайдена. Спробуйте ще раз:")
        return
    elif len(matches) > 1:
        options = "\n".join([f"{m['code']} – {m['name']}" for m in matches])
        await message.answer(f"🔍 Знайдено декілька варіантів:\n{options}\nВведіть точніше:")
        return

    specialty = matches[0]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM specialties WHERE code=? AND name=?", (specialty["code"], specialty["name"]))
    row = cursor.fetchone()

    if row:
        cursor.execute('UPDATE users SET specialty_id = ? WHERE telegram_id = ?', (row[0], str(message.from_user.id)))
        conn.commit()
        await message.answer(f"✅ Спеціальність оновлено на: {specialty['name']} ({specialty['code']})")
    else:
        await message.answer("❌ Не знайдено спеціальність в базі. Спробуйте ще.")

    conn.close()
    await show_edit_profile_menu_message(message, state)

# Зміна року випуску
@router.message(EditProfile.editing_graduation_year)
async def edit_graduation_year(message: Message, state: FSMContext):
    year_str = message.text.strip()
    if not year_str.isdigit():
        await message.answer("❌ Рік випуску має бути числом. Введіть ще раз:")
        return

    year = int(year_str)
    if year > 2025 or year < 1900:
        await message.answer("❌ Рік випуску має бути між 1900 та 2025. Введіть ще раз:")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET graduation_year = ? WHERE telegram_id = ?', (year, str(message.from_user.id)))
    conn.commit()
    conn.close()

    await message.answer(f"✅ Рік випуску оновлено на: {year}")
    await show_edit_profile_menu_message(message, state)

# Зміна дати народження
@router.message(EditProfile.editing_birth_date)
async def edit_birth_date(message: Message, state: FSMContext):
    birth_date_str = message.text.strip()
    try:
        birth_date = datetime.strptime(birth_date_str, "%d.%m.%Y")
    except ValueError:
        await message.answer("❌ Неправильний формат дати. Введіть ще раз (ДД.ММ.РРРР):")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET birth_date = ? WHERE telegram_id = ?', (birth_date_str, str(message.from_user.id)))
    conn.commit()
    conn.close()

    await message.answer("✅ Дату народження оновлено!")
    await show_edit_profile_menu_message(message, state)
