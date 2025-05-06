import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from aiogram.types import Message, CallbackQuery
from datetime import datetime
from BOT.handlers.file_work.user_upload import (
    receive_photo, receive_video, receive_document,
    handle_upload_choice, view_my_files,
    UploadPhotoStates, UploadVideoStates, UploadDocumentStates
)


@pytest.mark.asyncio
async def test_receive_photo_valid():
    message = AsyncMock()
    message.photo = [MagicMock(file_id="photo123")]
    message.from_user.id = 123
    state = AsyncMock()

    with patch("BOT.handlers.file_work.user_upload.get_connection") as mock_conn:
        mock_conn.return_value.cursor.return_value = MagicMock()
        await receive_photo(message, state)

    message.answer.assert_called_once()
    state.set_state.assert_called_with(UploadPhotoStates.confirming_more)


@pytest.mark.asyncio
async def test_receive_photo_invalid():
    message = AsyncMock()
    message.photo = None
    state = AsyncMock()

    await receive_photo(message, state)
    message.answer.assert_called_once_with("❗ Надішліть саме фотографію.")


@pytest.mark.asyncio
async def test_receive_video_valid():
    message = AsyncMock()
    message.video = MagicMock(file_id="video123")
    message.from_user.id = 456
    state = AsyncMock()

    with patch("BOT.handlers.file_work.user_upload.get_connection") as mock_conn:
        mock_conn.return_value.cursor.return_value = MagicMock()
        await receive_video(message, state)

    message.answer.assert_called_once()
    state.set_state.assert_called_with(UploadVideoStates.confirming_more)


@pytest.mark.asyncio
async def test_receive_document_valid():
    message = AsyncMock()
    message.document = MagicMock(file_id="doc123")
    message.from_user.id = 789
    state = AsyncMock()

    with patch("BOT.handlers.file_work.user_upload.get_connection") as mock_conn:
        mock_conn.return_value.cursor.return_value = MagicMock()
        await receive_document(message, state)

    message.answer.assert_called_once()
    state.set_state.assert_called_with(UploadDocumentStates.confirming_more)


@pytest.mark.asyncio
@pytest.mark.parametrize("current_state, expected_text", [
    (UploadPhotoStates.confirming_more.state, "📸 Надішліть ще одне фото:"),
    (UploadVideoStates.confirming_more.state, "🎬 Надішліть ще одне відео:"),
    (UploadDocumentStates.confirming_more.state, "📎 Надішліть ще один документ:")
])
async def test_handle_upload_choice_yes(current_state, expected_text):
    callback = AsyncMock()
    state = AsyncMock()
    state.get_state = AsyncMock(return_value=current_state)
    callback.data = "upload_yes"

    await handle_upload_choice(callback, state)
    callback.message.answer.assert_called_once_with(expected_text)
    assert state.set_state.called


@pytest.mark.asyncio
async def test_view_my_files_with_files():
    callback = AsyncMock()
    callback.from_user.id = 111
    bot = AsyncMock()
    callback.message.bot = bot
    files = [
        ("photo", "file1", "2024-01-01"),
        ("video", "file2", "2024-01-02"),
        ("document", "file3", "2024-01-03"),
    ]

    with patch("BOT.handlers.file_work.user_upload.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = files
        mock_conn.return_value.cursor.return_value = mock_cursor
        await view_my_files(callback)

    bot.send_photo.assert_called_once()
    bot.send_video.assert_called_once()
    bot.send_document.assert_called_once()
    callback.message.answer.assert_called()

@pytest.mark.asyncio
async def test_receive_video_invalid():
    message = AsyncMock()
    message.video = None
    state = AsyncMock()

    await receive_video(message, state)
    message.answer.assert_called_once_with("❗ Надішліть саме відео.")


@pytest.mark.asyncio
async def test_receive_document_invalid():
    message = AsyncMock()
    message.document = None
    state = AsyncMock()

    await receive_document(message, state)
    message.answer.assert_called_once_with("❗ Надішліть саме документ.")


@pytest.mark.asyncio
@pytest.mark.parametrize("current_state", [
    UploadPhotoStates.confirming_more.state,
    UploadVideoStates.confirming_more.state,
    UploadDocumentStates.confirming_more.state
])
async def test_handle_upload_choice_no(current_state):
    callback = AsyncMock()
    callback.data = "upload_no"
    state = AsyncMock()
    state.get_state = AsyncMock(return_value=current_state)

    await handle_upload_choice(callback, state)

    callback.message.answer.assert_called_once()
    state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_view_my_files_empty():
    callback = AsyncMock()
    callback.from_user.id = 111

    with patch("BOT.handlers.file_work.user_upload.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.return_value.cursor.return_value = mock_cursor
        await view_my_files(callback)

    callback.message.answer.assert_called_once_with("📂 Ви ще не надсилали файлів.")
