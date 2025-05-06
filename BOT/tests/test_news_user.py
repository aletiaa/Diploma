import pytest
from unittest.mock import AsyncMock, patch, ANY
from datetime import datetime, timedelta

from BOT.handlers.news.news_user import (
    show_user_news_menu,
    show_weekly_news,
    back_to_user_menu,
    ask_for_news_date,
    show_news_for_date
)
from BOT.handlers.news.news_user import NewsUserStates

@pytest.mark.asyncio
async def test_show_user_news_menu():
    callback = AsyncMock()
    state = AsyncMock()

    await show_user_news_menu(callback, state)
    callback.message.edit_text.assert_called_once()


@pytest.mark.asyncio
async def test_show_weekly_news_with_results():
    callback = AsyncMock()
    state = AsyncMock()
    news_data = [(1, "Опис", (datetime.today().date()).isoformat(), "http://link")] 

    with patch("BOT.handlers.news.news_user.get_connection") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value
        mock_cursor.fetchall.return_value = news_data

        await show_weekly_news(callback, state)
        callback.message.answer.assert_any_call("⬅️ Повернутись:", reply_markup=ANY)


@pytest.mark.asyncio
async def test_show_weekly_news_no_results():
    callback = AsyncMock()
    state = AsyncMock()

    with patch("BOT.handlers.news.news_user.get_connection") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value
        mock_cursor.fetchall.return_value = []

        await show_weekly_news(callback, state)
        callback.message.answer.assert_any_call("❌ За останній тиждень новин немає.")


@pytest.mark.asyncio
async def test_back_to_user_menu():
    callback = AsyncMock()
    state = AsyncMock()
    await back_to_user_menu(callback, state)
    callback.message.edit_text.assert_called_once()


@pytest.mark.asyncio
async def test_ask_for_news_date():
    callback = AsyncMock()
    state = AsyncMock()
    await ask_for_news_date(callback, state)
    state.set_state.assert_called_with(NewsUserStates.waiting_for_news_date)


@pytest.mark.asyncio
async def test_show_news_for_valid_date():
    message = AsyncMock()
    state = AsyncMock()
    message.text = datetime.today().strftime("%d.%m.%Y")
    news_data = [("Опис", datetime.today().date().isoformat(), "http://link")]

    with patch("BOT.handlers.news.news_user.get_connection") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value
        mock_cursor.fetchall.return_value = news_data

        await show_news_for_date(message, state)
        message.answer.assert_any_call("⬅️ Повернутись:", reply_markup=ANY)


@pytest.mark.asyncio
async def test_show_news_for_invalid_date():
    message = AsyncMock()
    state = AsyncMock()
    message.text = "31-13-2025"

    await show_news_for_date(message, state)
    message.answer.assert_awaited_with("❌ Невірний формат дати. Спробуйте ще раз у форматі ДД.ММ.РРРР.")


@pytest.mark.asyncio
async def test_show_news_for_date_no_results():
    message = AsyncMock()
    state = AsyncMock()
    message.text = "01.01.2000"

    with patch("BOT.handlers.news.news_user.get_connection") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value
        mock_cursor.fetchall.return_value = []

        await show_news_for_date(message, state)
        message.answer.assert_any_call("❌ Новини за вказану дату не знайдено.")

@pytest.mark.asyncio
async def test_weekly_news_includes_7_day_old_news():
    callback = AsyncMock()
    callback.data = "weekly_news"
    callback.message.answer = AsyncMock()
    
    seven_days_ago = (datetime.today().date() - timedelta(days=7)).isoformat()

    with patch("BOT.handlers.news.news_user.get_connection") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value
        mock_cursor.fetchall.return_value = [
            (1, "Новина на межі", seven_days_ago, "https://example.com")
        ]

        await show_weekly_news(callback, state=AsyncMock())

        callback.message.answer.assert_any_call(
            "📅 <b>{}</b>\n✏️ Новина на межі\n🔗 <a href='https://example.com'>Читати більше</a>".format(seven_days_ago),
            parse_mode="HTML"
        )


@pytest.mark.asyncio
async def test_multiple_news_same_day():   
    callback = AsyncMock()
    callback.data = "weekly_news"
    callback.message.answer = AsyncMock()
    
    today = datetime.today().date().isoformat()

    with patch("BOT.handlers.news.news_user.get_connection") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value
        mock_cursor.fetchall.return_value = [
            (3, "Третя новина", today, "https://example.com/3"),
            (2, "Друга новина", today, "https://example.com/2"),
            (1, "Перша новина", today, "https://example.com/1"),
        ]

        await show_weekly_news(callback, state=AsyncMock())

        # Перевірка, що кожна з трьох новин виведена
        assert callback.message.answer.call_count == 4  # 3 новини + кнопка "⬅️ Повернутись:"
        callback.message.answer.assert_any_call(
            f"📅 <b>{today}</b>\n✏️ Третя новина\n🔗 <a href='https://example.com/3'>Читати більше</a>", parse_mode="HTML"
        )
        callback.message.answer.assert_any_call(
            f"📅 <b>{today}</b>\n✏️ Друга новина\n🔗 <a href='https://example.com/2'>Читати більше</a>", parse_mode="HTML"
        )
        callback.message.answer.assert_any_call(
            f"📅 <b>{today}</b>\n✏️ Перша новина\n🔗 <a href='https://example.com/1'>Читати більше</a>", parse_mode="HTML"
        )
