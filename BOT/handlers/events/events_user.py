from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from ics import Calendar, Event as IcsEvent
from io import BytesIO
import tempfile

from ...database.queries import get_connection
from ...utils.keyboard import user_main_menu_keyboard, event_filter_menu_keyboard
from .utils.event_utils import load_events, reserve_seat, find_event_by_id, register_user_to_event

from babel.dates import format_datetime
from aiogram.types import FSInputFile

router = Router()

# --- Перегляд подій користувачем --- #
@router.callback_query(lambda c: c.data == "view_events")
async def show_event_filter_options(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Оберіть період для перегляду подій:", reply_markup=event_filter_menu_keyboard)

@router.callback_query(lambda c: c.data.startswith("event_filter_"))
async def filter_events(callback: CallbackQuery):
    await callback.answer()
    filter_type = callback.data.split("event_filter_")[-1]
    now = datetime.now()

    if filter_type == "all":
        filtered = load_events()
    elif filter_type.startswith("day_"):
        try:
            days = int(filter_type.split("day_")[-1])
            end_time = now + timedelta(days=days)
            filtered = [
                e for e in load_events()
                if now <= datetime.fromisoformat(e['datetime']) <= end_time
            ]
        except ValueError:
            await callback.message.answer("❌ Невірний фільтр днів.")
            return
    else:
        await callback.message.answer("❌ Невідомий тип фільтру.")
        return

    if not filtered:
        await callback.message.answer("Подій за обраний період не знайдено.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=e['title'], callback_data=f"event_{e['id']}")] for e in filtered
    ])
    await callback.message.answer("📅 Оберіть подію для перегляду:", reply_markup=keyboard)

@router.callback_query(lambda c: c.data.startswith("event_") and c.data.split("_")[-1].isdigit())
async def view_event_details(callback: CallbackQuery):
    await callback.answer()
    event_id = int(callback.data.split("_")[-1])
    event = find_event_by_id(load_events(), event_id)
    if not event:
        await callback.message.answer("❌ Подію не знайдено.")
        return

    dt = datetime.fromisoformat(event['datetime'])
    formatted_date = format_datetime(dt, "d MMMM (EEEE) 'о' HH:mm", locale='uk')
    text = (
        f"❤️ <b>Запрошення на {event['title']}</b>\n\n"
        f"🧾 {event['description']}\n\n"
        f"📅 <b>Коли:</b> {formatted_date}\n"
        f"🎟 <b>Місць доступно:</b> {event['available_seats']} з {event['max_seats']}\n"
        f"\n📍 Локація: Соцслужба КПІ, вул. Борщагівська, 144 (гуртожиток 20, вхід зліва)."
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Записатися", callback_data=f"register_event_{event['id']}")],
        [InlineKeyboardButton(text="📅 Додати в календар", callback_data=f"calendar_{event['id']}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="view_events")],
    ])
    await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)

@router.callback_query(lambda c: c.data.startswith("register_event_"))
async def register_to_event(callback: CallbackQuery):
    await callback.answer()
    event_id = int(callback.data.split("_")[-1])
    telegram_id = str(callback.from_user.id)

    # Запис у базу даних
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registrations WHERE event_id = ? AND telegram_id = ?", (event_id, telegram_id))
    if cursor.fetchone():
        await callback.message.answer("❗ Ви вже зареєстровані на цю подію.")
        return

    cursor.execute("INSERT INTO registrations (event_id, telegram_id) VALUES (?, ?)", (event_id, telegram_id))
    cursor.execute("UPDATE events SET available_seats = available_seats - 1 WHERE id = ? AND available_seats > 0", (event_id,))
    conn.commit()
    conn.close()

    # Запис у JSON
    register_user_to_event(event_id, telegram_id)

    await callback.message.answer("✅ Ви успішно зареєстровані на подію!")


@router.callback_query(lambda c: c.data.startswith("calendar_"))
async def download_calendar(callback: CallbackQuery):
    await callback.answer()
    event_id = int(callback.data.split("_")[-1])
    event = find_event_by_id(load_events(), event_id)

    if not event:
        await callback.message.answer("❌ Подію не знайдено.")
        return

    c = Calendar()
    e = IcsEvent()
    e.name = event['title']
    e.begin = event['datetime']
    e.description = event['description']
    c.events.add(e)

    with tempfile.NamedTemporaryFile("w+b", delete=False, suffix=".ics") as tmp:
        tmp.write(str(c.serialize()).encode("utf-8"))
        tmp.seek(0)
        file = FSInputFile(tmp.name, filename=f"{event['title'].replace(' ', '_')}.ics")
        await callback.message.answer_document(document=file, caption="📅 Файл події для календаря")
