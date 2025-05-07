import json
import sqlite3
from datetime import datetime
from typing import Union

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import nltk

from ...database.queries import get_connection
from ...utils.keyboard import news_admin_menu_keyboard
from .services.news_utils import generate_short_title, is_valid_url, save_news_to_db, save_news_to_json

nltk.download('stopwords')

router = Router()
tokenizer = AutoTokenizer.from_pretrained("d0p3/O3ap-sm")
model = AutoModelForSeq2SeqLM.from_pretrained("d0p3/O3ap-sm")

# Файл для збереження новин у JSON
JSON_FILE = "news_backup.json"

# Стан машини для новин
class NewsStates(StatesGroup):
    waiting_full_desc = State()
    waiting_link = State()
    waiting_date = State()
    waiting_news_id_to_edit = State()
    waiting_new_short_desc = State()
    waiting_news_id_to_delete = State()
    waiting_news_id_to_view = State()


@router.callback_query(lambda c: c.data == "news_menu")
async def show_news_menu(event: Union[CallbackQuery, Message], state: FSMContext):
    text = "📰 <b>Меню роботи з новинами:</b>\nОберіть дію:"
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=news_admin_menu_keyboard, parse_mode="HTML")
    else:
        await event.answer(text, reply_markup=news_admin_menu_keyboard, parse_mode="HTML")
    await state.clear()


@router.callback_query(lambda c: c.data == "add_news")
async def add_news_start(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("✏️ Введіть повний опис новини:")
    await state.set_state(NewsStates.waiting_full_desc)


@router.message(NewsStates.waiting_full_desc)
async def handle_full_desc(message: Message, state: FSMContext):
    full_desc = message.text.strip()
    await state.update_data(full_desc=full_desc)

    # Генеруємо короткий опис за допомогою моделі Hugging Face
    short_desc = generate_short_title(full_desc)

    await state.update_data(short_desc=short_desc)

    await message.answer(f"Згенеровано короткий опис:\n<code>{short_desc}</code>", parse_mode="HTML")
    await message.answer("🔗 Введіть офіційне посилання на новину:")
    await state.set_state(NewsStates.waiting_link)


@router.message(NewsStates.waiting_link)
async def handle_link(message: Message, state: FSMContext):
    await state.update_data(link=message.text.strip())
    await message.answer("📅 Введіть дату новини (ДД.ММ.РРРР):")
    await state.set_state(NewsStates.waiting_date)


@router.message(NewsStates.waiting_date)
async def save_news(message: Message, state: FSMContext):
    date_str = message.text.strip()
    try:
        news_date = datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        await message.answer("❌ Невірний формат дати. Введіть у форматі ДД.ММ.РРРР:")
        return

    if news_date > datetime.today().date():
        await message.answer("❌ Дата не може бути у майбутньому.")
        return

    iso_date = news_date.isoformat() 

    if news_date > datetime.today().date():
        await message.answer("❌ Дата не може бути у майбутньому.")
        return

    data = await state.get_data()

    if not is_valid_url(data['link']):
        await message.answer("❌ Невалідне посилання. Введіть коректне:")
        return

    # Викликаємо окремі функції
    save_news_to_db(data['short_desc'], data['full_desc'], date_str, data['link'])
    save_news_to_json(data['short_desc'], data['full_desc'], date_str, data['link'])

    await message.answer("✅ Новину додано!")
    await show_news_menu(message, state)

@router.callback_query(lambda c: c.data == "list_news")
async def list_news(callback_query: CallbackQuery, state: FSMContext):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, short_description, date FROM news ORDER BY date DESC")
    news = cursor.fetchall()
    conn.close()

    text = "\n\n".join([f"🆔 {n[0]} | 📅 {n[2]}\n{n[1]}" for n in news]) if news else "❌ Немає новин."

    await callback_query.message.answer(f"📋 <b>Список новин:</b>\n\n{text}",
                                        parse_mode="HTML", reply_markup=news_admin_menu_keyboard)


@router.callback_query(lambda c: c.data == "view_news")
async def view_news_prompt(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("🔍 Введіть ID новини для перегляду:")
    await state.set_state(NewsStates.waiting_news_id_to_view)


@router.message(NewsStates.waiting_news_id_to_view)
async def view_news_detail(message: Message, state: FSMContext):
    news_id = message.text.strip()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT short_description, full_description, date, link FROM news WHERE id = ?", (news_id,))
    news = cursor.fetchone()
    conn.close()

    if news:
        text = (
            f"📰 <b>Новина #{news_id}</b>\n"
            f"📅 Дата: {news[2]}\n"
            f"✏️ Коротко: {news[0]}\n\n"
            f"{news[1]}\n\n"
            f"🔗 Посилання: {news[3]}"
        )
    else:
        text = "❌ Новину не знайдено."

    await message.answer(text, parse_mode="HTML")
    await show_news_menu(message, state)


@router.callback_query(lambda c: c.data == "delete_news")
async def delete_news_prompt(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("❌ Введіть ID новини для видалення:")
    await state.set_state(NewsStates.waiting_news_id_to_delete)


@router.message(NewsStates.waiting_news_id_to_delete)
async def delete_news_confirm(message: Message, state: FSMContext):
    news_id = message.text.strip()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM news WHERE id = ?", (news_id,))
    conn.commit()
    conn.close()

    await message.answer(f"✅ Новину з ID {news_id} видалено.")
    await show_news_menu(message, state)


@router.callback_query(lambda c: c.data == "news_edit")
async def edit_news_prompt(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.answer("✏️ Введіть ID новини для редагування:")
    await state.set_state(NewsStates.waiting_news_id_to_edit)


@router.message(NewsStates.waiting_news_id_to_edit)
async def edit_news_short_desc(message: Message, state: FSMContext):
    news_id = message.text.strip()
    await state.update_data(news_id=news_id)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT short_description FROM news WHERE id = ?", (news_id,))
    news = cursor.fetchone()
    conn.close()

    if news:
        await message.answer(f"Поточний короткий опис:\n{news[0]}\n\nВведіть новий короткий опис:")
        await state.set_state(NewsStates.waiting_new_short_desc)
    else:
        await message.answer("❌ Новину не знайдено.")
        await show_news_menu(message, state)


@router.message(NewsStates.waiting_new_short_desc)
async def save_edited_news(message: Message, state: FSMContext):
    new_short_desc = message.text.strip()
    data = await state.get_data()
    news_id = data.get("news_id")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE news SET short_description = ? WHERE id = ?", (new_short_desc, news_id))
    conn.commit()
    conn.close()

    await message.answer(f"✅ Короткий опис новини #{news_id} оновлено.")
    await show_news_menu(message, state)
