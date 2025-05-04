from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
from ...database.queries import get_connection
from ...utils.keyboard import user_news_menu_keyboard, user_main_menu_keyboard
from datetime import datetime, timedelta

router = Router()

class NewsUserStates(StatesGroup):
    waiting_for_news_date = State()


@router.callback_query(lambda c: c.data == "view_news_menu")
async def show_user_news_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📰 <b>Оберіть розділ новин:</b>",
        reply_markup=user_news_menu_keyboard,
        parse_mode="HTML"
    )

@router.callback_query(lambda c: c.data == "weekly_news")
async def show_weekly_news(callback: CallbackQuery, state: FSMContext):
    conn = get_connection()
    cursor = conn.cursor()

    week_ago = datetime.today().date() - timedelta(days=7)

    cursor.execute("""
        SELECT id, short_description, date, link
        FROM news
        WHERE date >= ?
        ORDER BY date DESC
    """, (week_ago.isoformat(),))

    news = cursor.fetchall()
    conn.close()

    if not news:
        await callback.message.answer("❌ За останній тиждень новин немає.")
    else:
        for news_id, short_desc, date, link in news:
            text = f"📅 <b>{date}</b>\n✏️ {short_desc}\n🔗 <a href='{link}'>Читати більше</a>"
            await callback.message.answer(text, parse_mode="HTML")

    await callback.message.answer("⬅️ Повернутись:", reply_markup=user_news_menu_keyboard)


@router.callback_query(lambda c: c.data == "back_to_user_menu")
async def back_to_user_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🏠 <b>Головне меню:</b>", reply_markup=user_main_menu_keyboard, parse_mode="HTML")

@router.callback_query(lambda c: c.data == "choose_news_date")
async def ask_for_news_date(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📅 Введіть дату для перегляду новин у форматі ДД.ММ.РРРР:")
    await state.set_state(NewsUserStates.waiting_for_news_date)


@router.message(NewsUserStates.waiting_for_news_date)
async def show_news_for_date(message: Message, state: FSMContext):
    date_str = message.text.strip()
    try:
        # Конвертуємо у формат YYYY-MM-DD
        date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
        iso_date = date_obj.isoformat()
    except ValueError:
        await message.answer("❌ Невірний формат дати. Спробуйте ще раз у форматі ДД.ММ.РРРР.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT short_description, date, link 
        FROM news 
        WHERE date(date) = ?
        ORDER BY id DESC
    """, (iso_date,))
    news = cursor.fetchall()
    conn.close()

    if not news:
        await message.answer("❌ Новини за вказану дату не знайдено.")
    else:
        for short_desc, date, link in news:
            text = f"📅 <b>{date}</b>\n✏️ {short_desc}\n🔗 <a href='{link}'>Читати більше</a>"
            await message.answer(text, parse_mode="HTML")

    await state.clear()
    await message.answer("⬅️ Повернутись:", reply_markup=user_news_menu_keyboard)