import sqlite3
import re
from aiogram import Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ...utils.phone_validator import is_valid_phone
from ...utils.specialties import SPECIALTIES, search_specialty
from ...utils.department_recogniser import normalize_department
from ...utils.keyboard import request_phone_keyboard, main_menu_keyboard, user_main_menu_keyboard
from ...database.queries import get_connection

from datetime import datetime

# Підключення до БД
conn = get_connection()
cursor = conn.cursor()

router = Router()

# Стан машини для реєстрації
class Registration(StatesGroup):
    full_name = State()
    phone_number = State()
    old_phone_number_check = State()
    old_phone_number = State()
    enrollment_year = State()
    graduation_year = State()
    department_id = State()
    specialty_input = State()
    specialty_select = State()
    group_name = State()
    birth_date = State()
    ask_survey = State()

@router.callback_query(lambda c: c.data == 'register_user')
async def callback_register_user(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Ви обрали реєстрацію користувача.\nВведіть ваше повне ім'я:")
    await state.set_state(Registration.full_name)

@router.callback_query(lambda c: c.data == 'register_admin')
async def callback_register_admin(callback_query: CallbackQuery):
    await callback_query.message.answer("Використовуйте команду /register_admin для реєстрації адміністратора.")

@router.callback_query(lambda c: c.data == 'help_info')
async def callback_help(callback_query: CallbackQuery):
    help_text = (
        "👋 <b>Цей бот створений для випускників кафедри цифрових технологій в енергетиці</b>.\n\n"
        "Тут ви можете:\n"
        "🔹 Пройти реєстрацію або увійти в акаунт\n"
        "🔹 Редагувати свій профіль\n"
        "🔹 Отримувати актуальні новини\n"
        "🔹 Переглядати майбутні події та реєструватися на них\n"
        "🔹 Надсилати фото й відео (наприклад, з минулих подій)\n"
        "🔹 Знаходити чати для спілкування з одногрупниками або спеціальністю\n\n"
        "🔽 Використовуйте кнопки або команди меню для навігації.\n"
        "Допомога: alina.seikauskaite3@gmail.com"
    )
    await callback_query.message.answer(help_text)


@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    help_text = (
        "👋 Вітаю! Я бот для реєстрації випускників кафедри цифрових технологій в енергетиці.\n\n"
        "Оберіть дію з меню нижче або використовуйте команди:\n"
        "/menu – Головне меню\n"
        "/register_user – Зареєструватися як користувач\n"
        "/register_admin – Зареєструватися як адміністратор\n"
        "/help – Допомога та інформація\n"
    )
    await message.answer(help_text, reply_markup=main_menu_keyboard)


@router.message(Registration.full_name)
async def process_full_name(message: Message, state: FSMContext):
    full_name = message.text.strip()

    # Перевірка: тільки букви + один пробіл
    if not re.match(r"^[А-Яа-яЁёІіЇїЄєҐґA-Za-z]+ [А-Яа-яЁёІіЇїЄєҐґA-Za-z]+$", full_name):
        await message.answer("❌ Ім'я повинно містити тільки літери і складатися з двох слів (наприклад: Іван Петренко). Введіть ще раз:")
        return

    await state.update_data(full_name=full_name)
    await message.answer("Будь ласка, поділіться вашим номером телефону, натиснувши кнопку нижче:", reply_markup=request_phone_keyboard)
    await state.set_state(Registration.phone_number)


@router.message(Registration.phone_number)
async def process_phone_number(message: Message, state: FSMContext):
    contact = message.contact
    if contact:
        phone = contact.phone_number
    else:
        phone = message.text

    if not is_valid_phone(phone):
        await message.answer("Неправильний номер телефону. Введіть ще раз або натисніть кнопку:", reply_markup=request_phone_keyboard)
        return

    await state.update_data(phone_number=phone)
    await message.answer("Чи змінювався номер телефону з часу випуску? (так/ні)", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Registration.old_phone_number_check)

@router.message(Registration.old_phone_number_check)
async def process_old_phone_check(message: Message, state: FSMContext):
    if message.text.lower() == 'так':
        await message.answer("Введіть старий номер телефону:")
        await state.set_state(Registration.old_phone_number)
    else:
        data = await state.get_data()
        await state.update_data(old_phone_number=data['phone_number'])
        await message.answer("Введіть рік вступу:")
        await state.set_state(Registration.enrollment_year)

@router.message(Registration.old_phone_number)
async def process_old_phone_number(message: Message, state: FSMContext):
    await state.update_data(old_phone_number=message.text)
    await message.answer("Введіть рік вступу:")
    await state.set_state(Registration.enrollment_year)

@router.message(Registration.enrollment_year)
async def process_enrollment_year(message: Message, state: FSMContext):
    year_str = message.text.strip()
    if not year_str.isdigit():
        await message.answer("Рік вступу має бути числом. Введіть ще раз:")
        return

    year = int(year_str)
    current_year = datetime.today().year
    if year > current_year or year < 1975:
        await message.answer(f"Рік вступу має бути між 1975 та {current_year}. Введіть ще раз:")
        return

    await state.update_data(enrollment_year=year)
    await message.answer("Введіть рік випуску:")
    await state.set_state(Registration.graduation_year)
   

@router.message(Registration.graduation_year)
async def process_graduation_year(message: Message, state: FSMContext):
    year_str = message.text.strip()

    if not year_str.isdigit():
        await message.answer("Рік випуску має бути числом. Введіть ще раз:")
        return

    graduation_year = int(year_str)
    current_year = datetime.today().year
    if graduation_year > current_year or graduation_year < 1975:
        await message.answer(f"Рік випуску має бути між 1975 та {current_year}. Введіть ще раз:")
        return

    data = await state.get_data()
    enrollment_year = data.get("enrollment_year")

    if enrollment_year and graduation_year <= enrollment_year:
        await message.answer("Рік випуску не може бути меншим або рівним року вступу. Введіть ще раз:")
        return

    await state.update_data(graduation_year=graduation_year)
    await message.answer("Введіть назву вашого факультету (наприклад: ТЕФ, АПЕПС, ННІАТЕ):")
    await state.set_state(Registration.department_id)


@router.message(Registration.department_id)
async def process_department(message: Message, state: FSMContext):
    department = normalize_department(message.text)

    if not department:
        await message.answer(
            "На жаль, ми маємо інформацію лише для Теплоенергетичного факультету, кафедра цифрових технологій в енергетиці.\n"
            "Будь ласка, введіть назву вашого факультету ще раз (наприклад: ТЕФ, АПЕПС, ННІАТЕ):"
        )
        return  # Не змінюємо стан, даємо ще одну спробу

    await state.update_data(department_id=department)
    await message.answer("Введіть код або частину назви вашої спеціальності:")
    await state.set_state(Registration.specialty_input)


@router.message(Registration.specialty_input)
async def process_specialty_input(message: Message, state: FSMContext):
    user_input = message.text.strip()
    results = search_specialty(user_input)
    
    if not results:
        await message.answer("Не знайдено спеціальність. Спробуйте ще раз або уточніть код/назву:")
        return
    
    if len(results) == 1:
        specialty = results[0]
        await state.update_data(specialty_id=specialty['id'])
        await message.answer(f"Знайдено спеціальність: {specialty['code']} - {specialty['name']}")
        await message.answer("Введіть вашу групу:")
        await state.set_state(Registration.group_name)
    else:
        reply = "Знайдено кілька спеціальностей:\n"
        for idx, s in enumerate(results, start=1):
            reply += f"{idx}. {s['code']} - {s['name']}\n"
        reply += "\nНапишіть номер відповідної спеціальності:"
        await state.update_data(specialty_options=results)
        await message.answer(reply)
        await state.set_state(Registration.specialty_select)

@router.message(Registration.specialty_select)
async def process_specialty_selection(message: Message, state: FSMContext):
    data = await state.get_data()
    options = data.get('specialty_options', [])
    
    try:
        choice = int(message.text.strip()) - 1
        specialty = options[choice]
        await state.update_data(specialty_id=specialty['id'])
        await message.answer(f"Обрано: {specialty['code']} - {specialty['name']}")
        await message.answer("Введіть вашу групу:")
        await state.set_state(Registration.group_name)
    except (ValueError, IndexError):
        await message.answer("Некоректний вибір. Спробуйте ще раз:")

@router.message(Registration.group_name)
async def process_group_name(message: Message, state: FSMContext):
    group = message.text.strip().upper()

    if not re.match(r"^[А-ЯA-Z]{2}-\d{2}$", group):
        await message.answer("Група повинна бути у форматі: 2 літери, тире, 2 цифри (наприклад: ТВ-12). Введіть ще раз:")
        return

    await state.update_data(group_name=group)
    await message.answer("Введіть дату народження (ДД.ММ.РРРР):")
    await state.set_state(Registration.birth_date)

@router.message(Registration.ask_survey)
async def handle_survey_response(message: Message, state: FSMContext):
    text = message.text.lower().strip()

    if text in ["так", "тaк", "yes", "y", "ага", "да"]:
        await message.answer("🔗 Дякуємо! Перейдіть за посиланням на опитування:\nhttps://forms.gle/72mwaXVePPU5xVHK8")
    else:
        await message.answer("🙌 Добре, можливо пізніше!")

    # Завершення реєстраційного циклу
    await message.answer("🏠 Ви в головному меню:", reply_markup=user_main_menu_keyboard)
    await state.clear()

@router.message(Registration.birth_date)
async def process_birth_date(message: Message, state: FSMContext):
    birth_date_str = message.text.strip()

    try:
        # Перевірка формату та дійсності дати
        birth_date = datetime.strptime(birth_date_str, "%d.%m.%Y")
        
        # Перевірка віку: мінімум 16 років
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        if age < 16 or age > 95:
            await message.answer("Вам має бути щонайменше 16 років та, на жаль, не більше 95 для реєстрації. Введіть іншу дату народження:")
            return

    except ValueError:
        await message.answer("Неправильний формат дати. Введіть дату народження у форматі ДД.ММ.РРРР:")
        return

    await state.update_data(birth_date=birth_date_str)
    data = await state.get_data()

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO users (
                telegram_id, full_name, phone_number, old_phone_number, enrollment_year,
                graduation_year, department_id, specialty_id, group_name, birth_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(message.from_user.id),
            data['full_name'],
            data['phone_number'],
            data['old_phone_number'],
            data['enrollment_year'],
            data['graduation_year'],
            data['department_id'],
            data['specialty_id'],
            data['group_name'],
            data['birth_date']
        ))
        conn.commit()
        await message.answer("✅ Реєстрація успішно завершена!")
        await message.answer("📝 Хочете пройти коротке опитування? (так/ні)")
        await state.set_state(Registration.ask_survey)

    except sqlite3.IntegrityError:
        await message.answer("⚠️ Ви вже зареєстровані.")
    finally:
        conn.close()
