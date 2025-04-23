from aiogram import Router, types
from aiogram.filters import Command
from ..handlers.edit_profile import edit_profile_command  # імпортуємо обробник
from ..utils.keyboard import main_menu_keyboard

router = Router()

@router.message(Command("menu"))
async def show_main_menu(message: types.Message):
    await message.answer("🧭 Оберіть дію з меню:", reply_markup=main_menu_keyboard())

@router.message(lambda msg: msg.text == "🔎 Пошук випускника")
async def handle_search(message: types.Message):
    await message.answer("🔍 Функція пошуку ще в розробці, але скоро з'явиться!")

@router.message(lambda msg: msg.text == "📰 Отримати новини")
async def handle_news(message: types.Message):
    await message.answer("🗞️ Тут будуть останні новини кафедри або випускників.")

@router.message(lambda msg: msg.text == "📅 Переглянути події")
async def handle_events(message: types.Message):
    await message.answer("📅 Тут з’явиться календар подій, зустрічей і вебінарів.")

@router.message(lambda msg: msg.text == "🛠 Редагувати профіль")
async def handle_edit_profile(message: types.Message):
    await edit_profile_command(message)