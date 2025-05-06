from types import SimpleNamespace
import pytest
from unittest.mock import AsyncMock, patch, MagicMock, ANY
from aiogram.exceptions import TelegramBadRequest
from BOT.handlers.file_work.files_admin import (
    choose_filter,
    set_filter,
    receive_user_id_filter,
    change_page,
    show_file_page,
    FileViewState
)

@pytest.fixture
def mock_callback():
    cb = AsyncMock()
    cb.message.answer = AsyncMock()
    cb.answer = AsyncMock()
    cb.data = ""
    cb.from_user.id = 12345
    cb.message.chat.id = 12345
    cb.bot = AsyncMock()
    return cb

@pytest.fixture
def mock_message():
    msg = AsyncMock()
    msg.chat.id = 12345
    msg.text = "12345"
    msg.bot = AsyncMock()
    return msg

@pytest.fixture
def mock_state():
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    state.update_data = AsyncMock()
    state.set_state = AsyncMock()
    return state

@pytest.mark.asyncio
async def test_choose_filter(mock_callback, mock_state):
    mock_callback.data = "view_uploaded_files"
    await choose_filter(mock_callback, mock_state)
    mock_callback.message.answer.assert_called()

@pytest.mark.asyncio
async def test_set_filter_known_type(mock_callback, mock_state):
    mock_callback.data = "filter_photo"
    await set_filter(mock_callback, mock_state)
    mock_state.update_data.assert_called_with(selected_file_type="photo", page=0, user_id_filter=None, expect_user_id_input=False)

@pytest.mark.asyncio
async def test_set_filter_by_user(mock_callback, mock_state):
    mock_callback.data = "filter_by_user"
    await set_filter(mock_callback, mock_state)
    mock_state.set_state.assert_called_with(FileViewState.viewing_files)
    mock_state.update_data.assert_called_with(expect_user_id_input=True)

@pytest.mark.asyncio
async def test_receive_user_id_filter_valid(mock_message, mock_state):
    mock_state.get_data = AsyncMock(return_value={"expect_user_id_input": True})
    with patch("BOT.handlers.file_work.files_admin.show_file_page") as mock_show:
        await receive_user_id_filter(mock_message, mock_state)
        mock_state.update_data.assert_called()
        mock_show.assert_called_once()

@pytest.mark.asyncio
async def test_change_page_next(mock_callback, mock_state):
    mock_callback.data = "next_page"
    mock_state.get_data = AsyncMock(return_value={"page": 0})
    with patch("BOT.handlers.file_work.files_admin.show_file_page") as mock_show:
        await change_page(mock_callback, mock_state)
        mock_state.update_data.assert_called_with(page=1)
        mock_show.assert_called_once()

@pytest.mark.asyncio
async def test_show_file_page_no_files(mock_message, mock_state):
    mock_state.get_data = AsyncMock(return_value={"page": 0, "selected_file_type": "all", "user_id_filter": None})
    with patch("BOT.handlers.file_work.files_admin.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.return_value.cursor.return_value = mock_cursor
        await show_file_page(mock_message, mock_state)
        mock_message.bot.send_message.assert_called_with(ANY, "❗️ Файлів за заданими умовами не знайдено.")
