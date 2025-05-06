from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from .utils.event_utils import (
    load_events, save_events, get_next_event_id,
    add_event, update_event, delete_event, find_event_by_id
)
from ...database.queries import get_connection
from ...utils.keyboard import event_admin_menu_keyboard, event_edit_menu_keyboard
from .utils.event_utils import sync_db_to_json, sync_json_to_db

router = Router()

class EventState(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_datetime = State()
    waiting_for_seats = State()
    choosing_event_to_edit = State()
    choosing_event_to_delete = State()
    editing_title = State()
    editing_description = State()
    editing_datetime = State()
    editing_seats = State()
    confirming_deletion = State()

# ▸ Меню "Робота з подіями"
@router.callback_query(lambda c: c.data == "event_admin_menu")
async def event_admin_menu(callback: CallbackQuery):
    sync_db_to_json()
    await callback.answer()
    await callback.message.answer("📋 Меню роботи з подіями:", reply_markup=event_admin_menu_keyboard)

# ▸ Додавання події
@router.callback_query(lambda c: c.data == "add_event")
async def add_event_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("✏️ Введіть назву події:")
    await state.set_state(EventState.waiting_for_title)

@router.message(EventState.waiting_for_title)
async def add_event_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await message.answer("📝 Введіть опис:")
    await state.set_state(EventState.waiting_for_description)

@router.message(EventState.waiting_for_description)
async def add_event_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await message.answer("📅 Введіть дату та час (YYYY-MM-DD HH:MM):")
    await state.set_state(EventState.waiting_for_datetime)

@router.message(EventState.waiting_for_datetime)
async def add_event_datetime(message: Message, state: FSMContext):
    try:
        dt = datetime.strptime(message.text.strip(), "%Y-%m-%d %H:%M")
        await state.update_data(datetime=dt)
        await message.answer("🎟 Введіть максимальну кількість місць:")
        await state.set_state(EventState.waiting_for_seats)
    except ValueError:
        await message.answer("❗ Невірний формат. Спробуйте ще раз.")

@router.message(EventState.waiting_for_seats)
async def add_event_seats(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("❗ Введіть ціле число.")
        return
    data = await state.get_data()
    seats = int(message.text.strip())
    new_event = add_event(
        title=data['title'],
        description=data['description'],
        event_datetime=data['datetime'],
        max_seats=seats
    )
    await message.answer(f"✅ Подію <b>{new_event['title']}</b> додано!", parse_mode="HTML")
    await state.clear()

@router.message(lambda msg: msg.text == "/edit_event")
async def handle_edit_event_command(message: Message, state: FSMContext):
    events = load_events()
    if not events:
        await message.answer("📭 Немає подій для редагування.")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=e['title'], callback_data=f"event_edit_select_{e['id']}")] for e in events
    ])
    await message.answer("🔧 Оберіть подію:", reply_markup=keyboard)
    await state.set_state(EventState.choosing_event_to_edit)

# ▸ Редагування події
@router.callback_query(lambda c: c.data == "event_edit")
async def edit_event_list(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    events = load_events()
    if not events:
        await callback.message.answer("📭 Немає подій для редагування.")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=e['title'], callback_data=f"event_edit_select_{e['id']}")] for e in events
    ])
    await callback.message.answer("🔧 Оберіть подію:", reply_markup=keyboard)
    await state.set_state(EventState.choosing_event_to_edit)

@router.callback_query(lambda c: c.data.startswith("event_edit_select_"))
async def edit_event_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    event_id = int(callback.data.split("_")[-1])
    await state.update_data(event_id=event_id)
    await callback.message.answer("Що бажаєте редагувати?", reply_markup=event_edit_menu_keyboard)

@router.callback_query(lambda c: c.data == "event_edit_title")
async def edit_title(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("✏️ Введіть нову назву:")
    await state.set_state(EventState.editing_title)

@router.message(EventState.editing_title)
async def save_title(message: Message, state: FSMContext):
    data = await state.get_data()
    update_event(data['event_id'], title=message.text.strip())
    await message.answer("✅ Назву оновлено.")
    await state.clear()

@router.callback_query(lambda c: c.data == "event_edit_description")
async def edit_description(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("📝 Введіть новий опис:")
    await state.set_state(EventState.editing_description)

@router.message(EventState.editing_description)
async def save_description(message: Message, state: FSMContext):
    data = await state.get_data()
    update_event(data['event_id'], description=message.text.strip())
    await message.answer("✅ Опис оновлено.")
    await state.clear()

@router.callback_query(lambda c: c.data == "event_edit_datetime")
async def edit_datetime(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("📅 Введіть нову дату та час (YYYY-MM-DD HH:MM):")
    await state.set_state(EventState.editing_datetime)

@router.message(EventState.editing_datetime)
async def save_datetime(message: Message, state: FSMContext):
    try:
        new_dt = datetime.strptime(message.text.strip(), "%Y-%m-%d %H:%M").isoformat()
        data = await state.get_data()
        update_event(data['event_id'], datetime=new_dt)
        await message.answer("✅ Дата та час оновлені.")
        await state.clear()
    except ValueError:
        await message.answer("❗ Невірний формат.")

@router.callback_query(lambda c: c.data == "event_edit_seats")
async def edit_seats(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("🎟 Введіть нову кількість місць:")
    await state.set_state(EventState.editing_seats)

@router.message(EventState.editing_seats)
async def save_seats(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("❗ Введіть ціле число.")
        return
    data = await state.get_data()
    seats = int(message.text.strip())
    event = find_event_by_id(load_events(), data['event_id'])
    delta = seats - event['max_seats']
    new_available = max(0, event['available_seats'] + delta)
    update_event(data['event_id'], max_seats=seats, available_seats=new_available)
    await message.answer("✅ Кількість місць оновлено.")
    await state.clear()

# ▸ Видалення подій
@router.callback_query(lambda c: c.data == "delete_event_menu")
async def delete_event_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    events = load_events()
    if not events:
        await callback.message.answer("📭 Немає подій для видалення.")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=e['title'], callback_data=f"delete_event_{e['id']}")] for e in events
    ])
    await callback.message.answer("🗑 Оберіть подію для видалення:", reply_markup=keyboard)
    await state.set_state(EventState.choosing_event_to_delete)

@router.callback_query(lambda c: c.data.startswith("delete_event_"))
async def confirm_delete_event(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    event_id = int(callback.data.split("_")[-1])
    await state.update_data(event_id=event_id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Так, видалити", callback_data="delete_confirm")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="event_admin_menu")]
    ])
    await callback.message.answer("❗ Ви впевнені, що хочете видалити подію?", reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "delete_confirm")
async def delete_confirmed(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    delete_event(data['event_id'])
    await callback.message.answer("🗑 Подію видалено.")
    await state.clear()

# ▸ Перегляд зареєстрованих
@router.callback_query(lambda c: c.data == "view_registered")
async def view_registered(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    event_id = data.get("event_id")
    if not event_id:
        await callback.message.answer("❗ Спочатку оберіть подію для перегляду.")
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.full_name
        FROM registrations r
        JOIN users u ON r.telegram_id = u.telegram_id
        WHERE r.event_id = ?
    """, (event_id,))
    rows = cursor.fetchall()
    conn.close()

    if rows:
        users = "\n".join(row[0] for row in rows)
        await callback.message.answer(f"👥 Зареєстровані:\n{users}")
    else:
        await callback.message.answer("📭 Немає зареєстрованих.")

@router.callback_query(lambda c: c.data == "choose_for_sync")
async def choose_event_for_sync(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    events = load_events()
    if not events:
        await callback.message.answer("📭 Немає подій.")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=e['title'], callback_data=f"sync_select_{e['id']}")] for e in events
    ])
    await callback.message.answer("🔄 Оберіть подію для синхронізації:", reply_markup=keyboard)
    

@router.callback_query(lambda c: c.data.startswith("sync_select_"))
async def select_event_to_sync(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    event_id = int(callback.data.split("_")[-1])
    if not event_id:
        await callback.message.answer("❗ Спочатку оберіть подію через 'Обрати подію для синхронізації'.")
        return
    await state.update_data(event_id=event_id)
    await callback.message.answer("✅ Подію вибрано. Тепер натисніть 'Синхронізувати з базою'.")

# Синхронізація з базою
@router.callback_query(lambda c: c.data == "sync_event")
async def sync_event(callback: CallbackQuery, state: FSMContext):
    sync_db_to_json()
    await callback.answer()
    data = await state.get_data()
    event_id = data.get("event_id")
    event = find_event_by_id(load_events(), event_id)
    if event_id is None:
        await callback.message.answer("❌ Подію не знайдено.")
        return
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO events (id, title, description, event_datetime, max_seats, available_seats)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        event['id'], event['title'], event['description'],
        event['datetime'], event['max_seats'], event['available_seats']
    ))
    conn.commit()
    conn.close()
    await callback.message.answer("✅ Синхронізовано з базою даних.")
    
# ▸ Обрати подію для перегляду зареєстрованих
@router.callback_query(lambda c: c.data == "choose_event_for_viewing")
async def choose_event_for_viewing(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    events = load_events()
    if not events:
        await callback.message.answer("📭 Немає подій.")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=e["title"], callback_data=f"view_registered_{e['id']}")] for e in events
    ])
    await callback.message.answer("👥 Оберіть подію для перегляду зареєстрованих:", reply_markup=keyboard)

# ▸ Показати зареєстрованих користувачів для вибраної події
@router.callback_query(lambda c: c.data.startswith("view_registered_"))
async def show_registered(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    event_id = int(callback.data.split("_")[-1])
    await state.update_data(event_id=event_id)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.full_name
        FROM registrations r
        JOIN users u ON r.telegram_id = u.telegram_id
        WHERE r.event_id = ?
    """, (event_id,))
    rows = cursor.fetchall()
    conn.close()

    if rows:
        users = "\n".join(row[0] for row in rows)
        await callback.message.answer(f"👥 Зареєстровані:\n{users}")
    else:
        await callback.message.answer("📭 Немає зареєстрованих.")
