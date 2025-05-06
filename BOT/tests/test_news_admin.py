import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from BOT.handlers.news.news_admin import (
    handle_full_desc, handle_link, save_news, view_news_detail,
    delete_news_confirm, edit_news_short_desc, save_edited_news
)
from BOT.handlers.news.news_admin import NewsStates
from datetime import timedelta


@pytest.mark.asyncio
async def test_handle_full_desc_generates_short_desc():
    message = AsyncMock()
    message.text = "Це дуже довгий опис новини."
    state = AsyncMock()

    with patch("BOT.handlers.news.news_admin.generate_short_title", return_value="Короткий опис"):
        await handle_full_desc(message, state)

    state.update_data.assert_any_call(full_desc="Це дуже довгий опис новини.")
    state.update_data.assert_any_call(short_desc="Короткий опис")
    message.answer.assert_any_call("Згенеровано короткий опис:\n<code>Короткий опис</code>", parse_mode="HTML")


@pytest.mark.asyncio
async def test_save_news_valid_date():
    message = AsyncMock()
    message.text = "01.01.2024"
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={
        "short_desc": "Коротко",
        "full_desc": "Детально",
        "link": "https://example.com"
    })

    with patch("BOT.handlers.news.news_admin.is_valid_url", return_value=True), \
         patch("BOT.handlers.news.news_admin.save_news_to_db"), \
         patch("BOT.handlers.news.news_admin.save_news_to_json"), \
         patch("BOT.handlers.news.news_admin.show_news_menu", new=AsyncMock()):
        await save_news(message, state)

    message.answer.assert_any_call("✅ Новину додано!")


@pytest.mark.asyncio
async def test_save_news_invalid_date():
    message = AsyncMock()
    message.text = "32.13.2024"
    state = AsyncMock()

    await save_news(message, state)
    message.answer.assert_called_with("❌ Невірний формат дати. Введіть у форматі ДД.ММ.РРРР:")


@pytest.mark.asyncio
async def test_view_news_detail_found():
    message = AsyncMock()
    message.text = "1"
    state = AsyncMock()

    with patch("BOT.handlers.news.news_admin.get_connection") as mock_conn, \
         patch("BOT.handlers.news.news_admin.show_news_menu", new=AsyncMock()):
        cursor = MagicMock()
        cursor.fetchone.return_value = ("Коротко", "Детально", "2024-05-01", "https://example.com")
        mock_conn.return_value.cursor.return_value = cursor

        await view_news_detail(message, state)

    assert message.answer.call_args[0][0].startswith("📰 <b>Новина #1</b>")


@pytest.mark.asyncio
async def test_delete_news_confirm():
    message = AsyncMock()
    message.text = "1"
    state = AsyncMock()

    with patch("BOT.handlers.news.news_admin.get_connection") as mock_conn, \
         patch("BOT.handlers.news.news_admin.show_news_menu", new=AsyncMock()):
        cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = cursor

        await delete_news_confirm(message, state)

    message.answer.assert_called_with("✅ Новину з ID 1 видалено.")


@pytest.mark.asyncio
async def test_edit_news_short_desc_found():
    message = AsyncMock()
    message.text = "1"
    state = AsyncMock()

    with patch("BOT.handlers.news.news_admin.get_connection") as mock_conn:
        cursor = MagicMock()
        cursor.fetchone.return_value = ("Старий опис",)
        mock_conn.return_value.cursor.return_value = cursor

        await edit_news_short_desc(message, state)

    message.answer.assert_called_with("Поточний короткий опис:\nСтарий опис\n\nВведіть новий короткий опис:")


@pytest.mark.asyncio
async def test_save_edited_news():
    message = AsyncMock()
    message.text = "Новий опис"
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"news_id": "1"})

    with patch("BOT.handlers.news.news_admin.get_connection") as mock_conn, \
         patch("BOT.handlers.news.news_admin.show_news_menu", new=AsyncMock()):
        cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = cursor

        await save_edited_news(message, state)

    message.answer.assert_called_with("✅ Короткий опис новини #1 оновлено.")

@pytest.mark.asyncio
async def test_generate_short_desc_empty():
    message = AsyncMock()
    message.text = "   "
    state = AsyncMock()

    with patch("BOT.handlers.news.news_admin.generate_short_title", return_value="Без опису"):
        await handle_full_desc(message, state)
        message.answer.assert_any_call("Згенеровано короткий опис:\n<code>Без опису</code>", parse_mode="HTML")

@pytest.mark.asyncio
async def test_invalid_url():
    message = AsyncMock()
    message.text = "https://invalid-url"
    state = AsyncMock()
    state.update_data = AsyncMock()
    state.get_data = AsyncMock(return_value={
        'full_desc': 'Новина...',
        'short_desc': 'Новина',
        'link': 'invalid-url'
    })

    await handle_link(message, state)
    message.answer.assert_called_with("📅 Введіть дату новини (ДД.ММ.РРРР):")


@pytest.mark.asyncio
async def test_invalid_date_format():
    message = AsyncMock()
    message.text = "2024/01/01"
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={
        'link': 'https://example.com',
        'short_desc': 'Коротко',
        'full_desc': 'Повний опис'
    })

    await save_news(message, state)
    message.answer.assert_called_with("❌ Невірний формат дати. Введіть у форматі ДД.ММ.РРРР:")


@pytest.mark.asyncio
async def test_future_date():
    future_date = (datetime.today() + timedelta(days=1)).strftime("%d.%m.%Y")
    message = AsyncMock()
    message.text = future_date
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={
        'link': 'https://example.com',
        'short_desc': 'Коротко',
        'full_desc': 'Повний опис'
    })

    await save_news(message, state)
    message.answer.assert_called_with("❌ Дата не може бути у майбутньому.")


# ✅ Тест на перегляд неіснуючої новини
@pytest.mark.asyncio
async def test_view_nonexistent_news():
    message = AsyncMock()
    message.text = "999"
    state = AsyncMock()

    with patch("BOT.handlers.news.news_admin.get_connection") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = None

        await view_news_detail(message, state)

        message.answer.assert_any_call("❌ Новину не знайдено.", parse_mode="HTML")


# ✅ Тест на редагування неіснуючої новини
@pytest.mark.asyncio
async def test_edit_nonexistent_news():
    message = AsyncMock()
    message.text = "999"
    state = AsyncMock()

    with patch("BOT.handlers.news.news_admin.get_connection") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = None

        await edit_news_short_desc(message, state)

        message.answer.assert_any_call("❌ Новину не знайдено.")