from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from .utils.event_utils import load_events, save_events, get_next_event_id, update_event, delete_event
from ...utils.keyboard import admin_main_menu_keyboard, event_edit_menu_keyboard
from ...database.queries import get_connection

router = Router()

class EventEditState(StatesGroup):
    choosing_event = State()
    editing_title = State()
    editing_description = State()
    editing_datetime = State()
    editing_seats = State()

@router.callback_query(lambda c: c.data == "edit_event")
async def list_events_for_edit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    events = load_events()
    if not events:
        await callback.message.answer("📭 Немає доступних подій для редагування.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=event['title'], callback_data=f"edit_event_{event['id']}")]
        for event in events
    ] + [[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin_menu")]])

    await callback.message.answer("🛠 Оберіть подію для редагування:", reply_markup=keyboard)
    await state.set_state(EventEditState.choosing_event)

@router.callback_query(lambda c: c.data.startswith("edit_event_"))
async def start_edit(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    event_id = int(callback.data.split("_")[-1])
    await state.update_data(event_id=event_id)
    keyboard = event_edit_menu_keyboard(event_id)
    await callback.message.answer("Що саме редагувати?", reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "edit_title")
async def edit_title(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("✏️ Введіть нову назву події:")
    await state.set_state(EventEditState.editing_title)

@router.message(EventEditState.editing_title)
async def save_new_title(message: Message, state: FSMContext):
    data = await state.get_data()
    update_event(data['event_id'], title=message.text.strip())
    await message.answer("✅ Назву оновлено.")
    await state.clear()

@router.callback_query(lambda c: c.data == "edit_description")
async def edit_description(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("📝 Введіть новий опис події:")
    await state.set_state(EventEditState.editing_description)

@router.message(EventEditState.editing_description)
async def save_new_description(message: Message, state: FSMContext):
    data = await state.get_data()
    update_event(data['event_id'], description=message.text.strip())
    await message.answer("✅ Опис оновлено.")
    await state.clear()

@router.callback_query(lambda c: c.data == "edit_datetime")
async def edit_datetime(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("📅 Введіть нову дату та час у форматі YYYY-MM-DD HH:MM:")
    await state.set_state(EventEditState.editing_datetime)

@router.message(EventEditState.editing_datetime)
async def save_new_datetime(message: Message, state: FSMContext):
    from datetime import datetime
    try:
        new_dt = datetime.strptime(message.text.strip(), "%Y-%m-%d %H:%M").isoformat()
        data = await state.get_data()
        update_event(data['event_id'], datetime=new_dt)
        await message.answer("✅ Дата та час оновлені.")
    except ValueError:
        await message.answer("❗ Невірний формат. Спробуйте знову у форматі YYYY-MM-DD HH:MM")
        return
    await state.clear()

@router.callback_query(lambda c: c.data == "edit_seats")
async def edit_seats(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("🎟 Введіть нову максимальну кількість місць:")
    await state.set_state(EventEditState.editing_seats)

@router.message(EventEditState.editing_seats)
async def save_new_seats(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("❗ Введіть число.")
        return
    new_seats = int(message.text.strip())
    data = await state.get_data()
    update_event(data['event_id'], max_seats=new_seats, available_seats=new_seats)
    await message.answer("✅ Кількість місць оновлено.")
    await state.clear()

@router.callback_query(lambda c: c.data == "confirm_delete_event")
async def confirm_delete_event(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Так, видалити", callback_data="delete_event")],
        [InlineKeyboardButton(text="❌ Скасувати", callback_data="edit_event")]
    ])
    await callback.message.answer("❗ Ви впевнені, що хочете видалити цю подію?", reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "delete_event")
async def delete_selected_event(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    delete_event(data['event_id'])
    await callback.message.answer("🗑 Подію видалено.")
    await state.clear()

@router.callback_query(lambda c: c.data == "view_registered")
async def view_registered_users(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    event_id = data['event_id']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name FROM registrations JOIN users ON registrations.telegram_id = users.telegram_id WHERE registrations.event_id = ?", (event_id,))
    users = [row[0] for row in cursor.fetchall()]
    conn.close()

    if users:
        await callback.message.answer(f"👥 Зареєстровано користувачів: {len(users)}\n\n" + "\n".join(users))
    else:
        await callback.message.answer("📭 Ще ніхто не зареєструвався на цю подію.")

@router.callback_query(lambda c: c.data == "sync_event")
async def sync_event_to_db(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    event_id = data['event_id']

    event = next((e for e in load_events() if e['id'] == event_id), None)
    if not event:
        await callback.message.answer("❌ Подію не знайдено у JSON.")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO events (id, title, description, event_datetime, max_seats, available_seats)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        event['id'],
        event['title'],
        event['description'],
        event['datetime'],
        event['max_seats'],
        event['available_seats']
    ))
    conn.commit()
    conn.close()

    await callback.message.answer("✅ Подію синхронізовано з базою даних.")