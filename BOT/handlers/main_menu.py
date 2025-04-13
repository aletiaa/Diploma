from aiogram import Router, types

router = Router()

@router.message(lambda msg: msg.text == "🔎 Пошук випускника")
async def handle_search(message: types.Message):
    await message.answer("🔍 Функція пошуку ще в розробці, але скоро з'явиться!")

@router.message(lambda msg: msg.text == "📰 Отримати новини")
async def handle_news(message: types.Message):
    await message.answer("🗞️ Тут будуть останні новини кафедри або випускників.")

@router.message(lambda msg: msg.text == "📅 Переглянути події")
async def handle_events(message: types.Message):
    await message.answer("📅 Тут з’явиться календар подій, зустрічей і вебінарів.")
