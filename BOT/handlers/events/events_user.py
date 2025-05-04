from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message, InputFile
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from datetime import datetime
from ics import Calendar, Event as IcsEvent
from io import BytesIO

from .utils.event_utils import load_events, reserve_seat
from ...database.queries import get_connection

router = Router()

@router.callback_query(lambda c: c.data == "view_events")
async def show_event_list(callback: CallbackQuery):
    await callback.answer()
    events = load_events()
    if not events:
        await callback.message.answer("📭 Немає доступних подій.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=e['title'], callback_data=f"event_{e['id']}")]
        for e in events
    ])
    await callback.message.answer("📅 Оберіть подію для перегляду:", reply_markup=keyboard)

@router.callback_query(lambda c: c.data.startswith("event_"))
async def view_event_details(callback: CallbackQuery):
    await callback.answer()
    event_id = int(callback.data.split("_")[-1])
    event = next((e for e in load_events() if e['id'] == event_id), None)
    if not event:
        await callback.message.answer("❌ Подію не знайдено.")
        return

    dt = datetime.fromisoformat(event['datetime'])
    text = (
        f"📌 <b>{event['title']}</b>\n\n"
        f"🗓 Дата та час: {dt.strftime('%Y-%m-%d %H:%M')}\n"
        f"🧾 Опис: {event['description']}\n"
        f"🎟 Місць доступно: {event['available_seats']} з {event['max_seats']}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Записатися", callback_data=f"register_{event['id']}")],
        [InlineKeyboardButton(text="📅 Додати в календар", callback_data=f"calendar_{event['id']}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="view_events")],
    ])
    await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)

@router.callback_query(lambda c: c.data.startswith("register_"))
async def register_for_event(callback: CallbackQuery):
    await callback.answer()
    telegram_id = str(callback.from_user.id)
    event_id = int(callback.data.split("_")[-1])

    if not reserve_seat(load_events(), event_id):
        await callback.message.answer("❌ Немає вільних місць або подія не знайдена.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO registrations (telegram_id, event_id) VALUES (?, ?)", (telegram_id, event_id))
        conn.commit()
        await callback.message.answer("✅ Ви успішно зареєструвались на подію!")
    except:
        await callback.message.answer("⚠️ Ви вже зареєстровані на цю подію.")
    finally:
        conn.close()

@router.callback_query(lambda c: c.data.startswith("calendar_"))
async def download_calendar(callback: CallbackQuery):
    await callback.answer()
    event_id = int(callback.data.split("_")[-1])
    event = next((e for e in load_events() if e['id'] == event_id), None)

    if not event:
        await callback.message.answer("❌ Подію не знайдено.")
        return

    c = Calendar()
    e = IcsEvent()
    e.name = event['title']
    e.begin = event['datetime']
    e.description = event['description']
    c.events.add(e)

    ics_file = BytesIO(str(c).encode("utf-8"))
    ics_file.name = f"{event['title'].replace(' ', '_')}.ics"

    await callback.message.answer_document(document=InputFile(ics_file, filename=ics_file.name), caption="📅 Файл події для календаря")
