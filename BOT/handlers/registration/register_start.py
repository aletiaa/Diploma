from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from ...utils.keyboard import main_menu_keyboard
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from ...handlers.login.login_user import UserLogin
from ...handlers.login.login_admin import AdminLogin

router = Router()

@router.message(Command("start", "menu"))
async def show_main_menu(message: Message):
    text = (
        "👋 Вітаю! Я бот для реєстрації випускників кафедри цифрових технологій в енергетиці.\n\n"
        "Оберіть дію з меню нижче або використовуйте команди:\n"
        "/register_user – Зареєструватися як користувач\n"
        "/register_admin – Зареєструватися як адміністратор\n"
        "/help – Допомога та інформація\n"
        "/login_user - Увійти як користувач\n"
        "/login_admin - Увійти як адміністратор\n"
    )
    await message.answer(text, reply_markup=main_menu_keyboard)

@router.message(Command("help"))
async def show_help(message: Message):
    help_text = (
        "ℹ️ Допомога:\n"
        "- Якщо ви студент або випускник – використовуйте /register_user, /login_user або кнопку.\n"
        "- Якщо ви адміністрація – використовуйте /register_admin, /login_admin або кнопку.\n"
        "- Для повернення до меню – /menu.\n\n"
        "Підтримка: alina.seikauskaite3@gmail.com"
    )
    await message.answer(help_text)
    
    
from aiogram.types import CallbackQuery

@router.callback_query(lambda c: c.data == 'login_user')
async def callback_login_user(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Ви обрали вхід як користувач.\nВведіть ваш номер телефону:")
    await state.set_state(UserLogin.phone_number)

@router.callback_query(lambda c: c.data == 'login_admin')
async def callback_login_admin(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Ви обрали вхід як адміністратор.\nВведіть ваш номер телефону:")
    await state.set_state(AdminLogin.phone_number)

