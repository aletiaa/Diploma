import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from aiogram.types import Message, CallbackQuery
from datetime import datetime
from BOT.handlers.events.events_admin import (
    add_event_start, add_event_title, add_event_description,
    add_event_datetime, add_event_seats,
    edit_title, save_title,
    edit_datetime, save_datetime,
    edit_seats, save_seats,
    confirm_delete_event, delete_confirmed,
    sync_event, view_registered,
    EventState
)


@pytest.fixture
def mock_callback():
    cb = AsyncMock()
    cb.message.answer = AsyncMock()
    cb.answer = AsyncMock()
    cb.data = ""
    return cb


@pytest.fixture
def mock_message():
    msg = AsyncMock()
    msg.text = "Test Input"
    msg.answer = AsyncMock()
    msg.from_user.id = 123456
    return msg


@pytest.fixture
def mock_state():
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"event_id": 1})
    return state


# ------------------------ Add Event ------------------------

@pytest.mark.asyncio
async def test_add_event_start(mock_callback, mock_state):
    await add_event_start(mock_callback, mock_state)
    mock_callback.answer.assert_called_once()
    mock_callback.message.answer.assert_called_with("✏️ Введіть назву події:")
    mock_state.set_state.assert_called_with(EventState.waiting_for_title)


@pytest.mark.asyncio
async def test_add_event_title(mock_message, mock_state):
    mock_message.text = "Подія 1"
    await add_event_title(mock_message, mock_state)
    mock_state.update_data.assert_called_with(title="Подія 1")
    mock_message.answer.assert_called_with("📝 Введіть опис:")
    mock_state.set_state.assert_called_with(EventState.waiting_for_description)


@pytest.mark.asyncio
async def test_add_event_description(mock_message, mock_state):
    mock_message.text = "Це опис"
    await add_event_description(mock_message, mock_state)
    mock_state.update_data.assert_called_with(description="Це опис")
    mock_message.answer.assert_called_with("📅 Введіть дату та час (YYYY-MM-DD HH:MM):")
    mock_state.set_state.assert_called_with(EventState.waiting_for_datetime)


@pytest.mark.asyncio
async def test_add_event_datetime_valid(mock_message, mock_state):
    mock_message.text = "2025-12-25 18:00"
    await add_event_datetime(mock_message, mock_state)
    mock_state.update_data.assert_called()
    mock_message.answer.assert_called_with("🎟 Введіть максимальну кількість місць:")
    mock_state.set_state.assert_called_with(EventState.waiting_for_seats)


@pytest.mark.asyncio
async def test_add_event_datetime_invalid(mock_message, mock_state):
    mock_message.text = "25-12-2025"
    await add_event_datetime(mock_message, mock_state)
    mock_message.answer.assert_called_with("❗ Невірний формат. Спробуйте ще раз.")


@pytest.mark.asyncio
async def test_add_event_seats_valid(mock_message, mock_state):
    mock_message.text = "100"
    mock_state.get_data = AsyncMock(return_value={
        "title": "Подія",
        "description": "Опис",
        "datetime": datetime(2025, 12, 25, 18, 0)
    })

    with patch("BOT.handlers.events.events_admin.add_event") as mock_add:
        mock_add.return_value = {"title": "Подія"}
        await add_event_seats(mock_message, mock_state)
        mock_message.answer.assert_called_with("✅ Подію <b>Подія</b> додано!", parse_mode="HTML")
        mock_state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_add_event_seats_invalid(mock_message, mock_state):
    mock_message.text = "abc"
    await add_event_seats(mock_message, mock_state)
    mock_message.answer.assert_called_with("❗ Введіть ціле число.")


# ------------------------ Edit Title ------------------------

@pytest.mark.asyncio
async def test_edit_title_callback(mock_callback, mock_state):
    await edit_title(mock_callback, mock_state)
    mock_callback.message.answer.assert_called_with("✏️ Введіть нову назву:")
    mock_state.set_state.assert_called_with(EventState.editing_title)


@pytest.mark.asyncio
async def test_save_title(mock_message, mock_state):
    with patch("BOT.handlers.events.events_admin.update_event") as mock_update:
        await save_title(mock_message, mock_state)
        mock_update.assert_called_with(1, title="Test Input")
        mock_message.answer.assert_called_with("✅ Назву оновлено.")
        mock_state.clear.assert_called_once()


# ------------------------ Edit Datetime ------------------------

@pytest.mark.asyncio
async def test_edit_datetime_callback(mock_callback, mock_state):
    await edit_datetime(mock_callback, mock_state)
    mock_callback.message.answer.assert_called_with("📅 Введіть нову дату та час (YYYY-MM-DD HH:MM):")
    mock_state.set_state.assert_called_with(EventState.editing_datetime)


@pytest.mark.asyncio
async def test_save_datetime_valid(mock_message, mock_state):
    mock_message.text = "2025-12-12 18:30"
    with patch("BOT.handlers.events.events_admin.update_event") as mock_update:
        await save_datetime(mock_message, mock_state)
        mock_update.assert_called_with(1, datetime="2025-12-12T18:30:00")
        mock_message.answer.assert_called_with("✅ Дата та час оновлені.")
        mock_state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_save_datetime_invalid(mock_message, mock_state):
    mock_message.text = "12/12/2025"
    await save_datetime(mock_message, mock_state)
    mock_message.answer.assert_called_with("❗ Невірний формат.")


# ------------------------ Edit Seats ------------------------

@pytest.mark.asyncio
async def test_edit_seats_callback(mock_callback, mock_state):
    await edit_seats(mock_callback, mock_state)
    mock_callback.message.answer.assert_called_with("🎟 Введіть нову кількість місць:")
    mock_state.set_state.assert_called_with(EventState.editing_seats)


@pytest.mark.asyncio
async def test_save_seats_valid(mock_message, mock_state):
    mock_message.text = "150"
    with patch("BOT.handlers.events.events_admin.load_events") as mock_load, \
         patch("BOT.handlers.events.events_admin.update_event") as mock_update:
        mock_load.return_value = [{"id": 1, "max_seats": 100, "available_seats": 20}]
        await save_seats(mock_message, mock_state)
        mock_update.assert_called_with(1, max_seats=150, available_seats=70)
        mock_message.answer.assert_called_with("✅ Кількість місць оновлено.")
        mock_state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_save_seats_invalid(mock_message, mock_state):
    mock_message.text = "abc"
    await save_seats(mock_message, mock_state)
    mock_message.answer.assert_called_with("❗ Введіть ціле число.")


# ------------------------ Delete Event ------------------------

@pytest.mark.asyncio
async def test_confirm_delete_event(mock_callback, mock_state):
    mock_callback.data = "delete_event_3"
    await confirm_delete_event(mock_callback, mock_state)
    mock_state.update_data.assert_called_with(event_id=3)
    mock_callback.message.answer.assert_called_once()


@pytest.mark.asyncio
async def test_delete_confirmed(mock_callback, mock_state):
    mock_state.get_data = AsyncMock(return_value={"event_id": 5})
    with patch("BOT.handlers.events.events_admin.delete_event") as mock_delete:
        await delete_confirmed(mock_callback, mock_state)
        mock_delete.assert_called_with(5)
        mock_callback.message.answer.assert_called_with("🗑 Подію видалено.")
        mock_state.clear.assert_called_once()


# ------------------------ Sync Event ------------------------

@pytest.mark.asyncio
async def test_sync_event_valid(mock_callback, mock_state):
    mock_state.get_data = AsyncMock(return_value={"event_id": 7})
    test_event = {
        "id": 7, "title": "SyncPodia", "description": "desc",
        "datetime": "2025-01-01T10:00:00",
        "max_seats": 100, "available_seats": 50
    }

    with patch("BOT.handlers.events.events_admin.sync_db_to_json"), \
         patch("BOT.handlers.events.events_admin.load_events", return_value=[test_event]), \
         patch("BOT.handlers.events.events_admin.get_connection") as mock_conn, \
         patch("BOT.handlers.events.events_admin.find_event_by_id", return_value=test_event):

        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor

        await sync_event(mock_callback, mock_state)
        mock_cursor.execute.assert_called_once()
        mock_callback.message.answer.assert_called_with("✅ Синхронізовано з базою даних.")


# ------------------------ View Registered ------------------------

@pytest.mark.asyncio
async def test_view_registered_users_exist(mock_callback, mock_state):
    mock_state.get_data = AsyncMock(return_value={"event_id": 1})
    with patch("BOT.handlers.events.events_admin.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("User1",), ("User2",)]
        mock_conn.return_value.cursor.return_value = mock_cursor

        await view_registered(mock_callback, mock_state)
        mock_callback.message.answer.assert_called_with("👥 Зареєстровані:\nUser1\nUser2")


@pytest.mark.asyncio
async def test_view_registered_no_users(mock_callback, mock_state):
    mock_state.get_data = AsyncMock(return_value={"event_id": 1})
    with patch("BOT.handlers.events.events_admin.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.return_value.cursor.return_value = mock_cursor

        await view_registered(mock_callback, mock_state)
        mock_callback.message.answer.assert_called_with("📭 Немає зареєстрованих.")


@pytest.mark.asyncio
async def test_view_registered_no_event_selected(mock_callback, mock_state):
    mock_state.get_data = AsyncMock(return_value={})
    await view_registered(mock_callback, mock_state)
    mock_callback.message.answer.assert_called_with("❗ Спочатку оберіть подію для перегляду.")
