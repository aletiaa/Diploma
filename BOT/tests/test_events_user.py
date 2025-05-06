import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from aiogram.types import CallbackQuery
from BOT.handlers.events.events_user import (
    show_event_filter_options, filter_events, view_event_details,
    register_to_event, download_calendar
)

@pytest.fixture
def mock_callback():
    cb = AsyncMock()
    cb.message.answer = AsyncMock()
    cb.message.answer_document = AsyncMock()
    cb.answer = AsyncMock()
    cb.data = ""
    cb.from_user.id = 123456
    return cb

# --- 1. show_event_filter_options ---
@pytest.mark.asyncio
async def test_show_event_filter_options(mock_callback):
    mock_callback.data = "view_events"
    await show_event_filter_options(mock_callback)
    mock_callback.answer.assert_called_once()
    mock_callback.message.answer.assert_called()

# --- 2. filter_events ---

@pytest.mark.asyncio
async def test_filter_events_all(mock_callback):
    mock_callback.data = "event_filter_all"
    with patch("BOT.handlers.events.events_user.load_events", return_value=[{
        "id": 1, "title": "Test Event", "datetime": datetime.now().isoformat()
    }]):
        await filter_events(mock_callback)
        mock_callback.message.answer.assert_called()

@pytest.mark.asyncio
async def test_filter_events_day_valid(mock_callback):
    mock_callback.data = "event_filter_day_2"
    now = datetime.now()
    with patch("BOT.handlers.events.events_user.load_events", return_value=[
        {"id": 2, "title": "Soon", "datetime": (now + timedelta(days=1)).isoformat()}
    ]):
        await filter_events(mock_callback)
        mock_callback.message.answer.assert_called()

@pytest.mark.asyncio
async def test_filter_events_day_invalid(mock_callback):
    mock_callback.data = "event_filter_day_bad"
    await filter_events(mock_callback)
    mock_callback.message.answer.assert_called_with("❌ Невірний фільтр днів.")

# --- 3. view_event_details ---

@pytest.mark.asyncio
async def test_view_event_details_success(mock_callback):
    mock_callback.data = "event_5"
    now = datetime.now().isoformat()
    event_data = {
        "id": 5, "title": "Party", "description": "Fun", "datetime": now, "max_seats": 30, "available_seats": 10
    }
    with patch("BOT.handlers.events.events_user.load_events", return_value=[event_data]), \
         patch("BOT.handlers.events.events_user.find_event_by_id", return_value=event_data):
        await view_event_details(mock_callback)
        mock_callback.message.answer.assert_called()

@pytest.mark.asyncio
async def test_view_event_details_not_found(mock_callback):
    mock_callback.data = "event_404"
    with patch("BOT.handlers.events.events_user.load_events", return_value=[]), \
         patch("BOT.handlers.events.events_user.find_event_by_id", return_value=None):
        await view_event_details(mock_callback)
        mock_callback.message.answer.assert_called_with("❌ Подію не знайдено.")

# --- 4. register_to_event ---

@pytest.mark.asyncio
async def test_register_to_event_new(mock_callback):
    mock_callback.data = "register_event_7"
    with patch("BOT.handlers.events.events_user.get_connection") as mock_conn, \
         patch("BOT.handlers.events.events_user.register_user_to_event") as mock_reg:
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        mock_conn.return_value.cursor.return_value = cursor

        await register_to_event(mock_callback)
        mock_reg.assert_called_once()
        mock_callback.message.answer.assert_called_with("✅ Ви успішно зареєстровані на подію!")

@pytest.mark.asyncio
async def test_register_to_event_duplicate(mock_callback):
    mock_callback.data = "register_event_7"
    with patch("BOT.handlers.events.events_user.get_connection") as mock_conn:
        cursor = MagicMock()
        cursor.fetchone.return_value = True
        mock_conn.return_value.cursor.return_value = cursor

        await register_to_event(mock_callback)
        mock_callback.message.answer.assert_called_with("❗ Ви вже зареєстровані на цю подію.")

# --- 5. download_calendar ---

@pytest.mark.asyncio
async def test_download_calendar_success(mock_callback):
    now = datetime.now().isoformat()
    mock_callback.data = "calendar_9"
    event = {"id": 9, "title": "Test", "description": "Test event", "datetime": now}
    with patch("BOT.handlers.events.events_user.load_events", return_value=[event]), \
         patch("BOT.handlers.events.events_user.find_event_by_id", return_value=event):
        await download_calendar(mock_callback)
        mock_callback.message.answer_document.assert_called()

@pytest.mark.asyncio
async def test_download_calendar_not_found(mock_callback):
    mock_callback.data = "calendar_404"
    with patch("BOT.handlers.events.events_user.load_events", return_value=[]), \
         patch("BOT.handlers.events.events_user.find_event_by_id", return_value=None):
        await download_calendar(mock_callback)
        mock_callback.message.answer.assert_called_with("❌ Подію не знайдено.")

# --- Unsupported filter type ---
@pytest.mark.asyncio
async def test_filter_events_unsupported_type(mock_callback):
    mock_callback.data = "event_filter_week"
    await filter_events(mock_callback)
    mock_callback.message.answer.assert_called_with("❌ Невідомий тип фільтру.")


# --- Negative day filter ---
@pytest.mark.asyncio
async def test_filter_events_negative_days(mock_callback):
    mock_callback.data = "event_filter_day_-3"
    now = datetime.now()
    with patch("BOT.handlers.events.events_user.load_events", return_value=[
        {"id": 1, "title": "Future", "datetime": (now + timedelta(days=1)).isoformat()}
    ]):
        await filter_events(mock_callback)
        mock_callback.message.answer.assert_called()


# --- No events in filter range ---
@pytest.mark.asyncio
async def test_filter_events_no_matches(mock_callback):
    mock_callback.data = "event_filter_day_1"
    now = datetime.now()
    with patch("BOT.handlers.events.events_user.load_events", return_value=[
        {"id": 5, "title": "Too Far", "datetime": (now + timedelta(days=10)).isoformat()}
    ]):
        await filter_events(mock_callback)
        mock_callback.message.answer.assert_called_with("Подій за обраний період не знайдено.")


# --- Long description in event details ---
@pytest.mark.asyncio
async def test_view_event_details_long_description(mock_callback):
    mock_callback.data = "event_99"
    long_text = "Опис " * 500
    event = {
        "id": 99,
        "title": "Довга Подія",
        "description": long_text,
        "datetime": datetime.now().isoformat(),
        "max_seats": 100,
        "available_seats": 50
    }
    with patch("BOT.handlers.events.events_user.load_events", return_value=[event]), \
         patch("BOT.handlers.events.events_user.find_event_by_id", return_value=event):
        await view_event_details(mock_callback)
        mock_callback.message.answer.assert_called()


# --- Special characters in calendar file name ---
@pytest.mark.asyncio
async def test_download_calendar_special_characters(mock_callback):
    mock_callback.data = "calendar_12"
    event = {
        "id": 12,
        "title": "Назва з пробілами та !символами?",
        "description": "Test",
        "datetime": datetime.now().isoformat()
    }
    with patch("BOT.handlers.events.events_user.load_events", return_value=[event]), \
         patch("BOT.handlers.events.events_user.find_event_by_id", return_value=event):
        await download_calendar(mock_callback)
        mock_callback.message.answer_document.assert_called()
