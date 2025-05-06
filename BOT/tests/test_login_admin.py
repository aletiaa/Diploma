import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.fsm.context import FSMContext
from BOT.handlers.login.login_admin import (
    start_admin_login, process_admin_phone, process_admin_password,
    AdminLogin
)


@pytest.mark.asyncio
async def test_start_admin_login():
    message = AsyncMock()
    state = AsyncMock()

    await start_admin_login(message, state)

    state.update_data.assert_called_once_with(attempts=3)
    message.answer.assert_called_once_with("📲 Введіть ваш номер телефону для входу:")
    state.set_state.assert_called_once_with(AdminLogin.phone_number)


@pytest.mark.asyncio
async def test_process_admin_phone_invalid():
    message = AsyncMock()
    message.text = "notaphone"
    state = AsyncMock()

    with patch("BOT.handlers.login.login_admin.is_valid_phone", return_value=False):
        await process_admin_phone(message, state)

    message.answer.assert_called_once_with("❌ Неправильний номер телефону. Введіть ще раз:")


@pytest.mark.asyncio
async def test_process_admin_phone_valid():
    message = AsyncMock()
    message.text = "+380501234567"
    state = AsyncMock()

    with patch("BOT.handlers.login.login_admin.is_valid_phone", return_value=True):
        await process_admin_phone(message, state)

    state.update_data.assert_called_once_with(phone_number="+380501234567")
    message.answer.assert_called_once_with("🔐 Введіть ваш пароль:")
    state.set_state.assert_called_once_with(AdminLogin.password)


@pytest.mark.asyncio
async def test_process_admin_password_success():
    message = AsyncMock()
    message.text = "correct_password"
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"phone_number": "123", "attempts": 3})

    with patch("BOT.handlers.login.login_admin.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, "Admin Name", "correct_password")
        mock_conn.return_value.cursor.return_value = mock_cursor

        await process_admin_password(message, state)

    message.answer.assert_called_once()
    state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_process_admin_password_failure_retry():
    message = AsyncMock()
    message.text = "wrong_password"
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"phone_number": "123", "attempts": 2})

    with patch("BOT.handlers.login.login_admin.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, "Admin Name", "correct_password")
        mock_conn.return_value.cursor.return_value = mock_cursor

        await process_admin_password(message, state)

    message.answer.assert_called()
    state.update_data.assert_called_with(attempts=1)
    state.set_state.assert_called_with(AdminLogin.phone_number)


@pytest.mark.asyncio
async def test_process_admin_password_failure_final():
    message = AsyncMock()
    message.text = "wrong_password"
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"phone_number": "123", "attempts": 1})

    with patch("BOT.handlers.login.login_admin.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, "Admin Name", "correct_password")
        mock_conn.return_value.cursor.return_value = mock_cursor

        await process_admin_password(message, state)

    message.answer.assert_called_with("❌ Вичерпано кількість спроб. Спробуйте пізніше.")
    state.clear.assert_called_once()

@pytest.mark.asyncio
async def test_process_admin_password_no_admin_found():
    message = AsyncMock()
    message.text = "any_password"
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"phone_number": "000", "attempts": 2})

    with patch("BOT.handlers.login.login_admin.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # admin not found
        mock_conn.return_value.cursor.return_value = mock_cursor

        await process_admin_password(message, state)

    message.answer.assert_called()
    state.update_data.assert_called_with(attempts=1)
    state.set_state.assert_called_with(AdminLogin.phone_number)


@pytest.mark.asyncio
async def test_process_admin_password_no_admin_final_attempt():
    message = AsyncMock()
    message.text = "some_password"
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"phone_number": "000", "attempts": 1})

    with patch("BOT.handlers.login.login_admin.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.return_value.cursor.return_value = mock_cursor

        await process_admin_password(message, state)

    message.answer.assert_called_with("❌ Вичерпано кількість спроб. Спробуйте пізніше.")
    state.clear.assert_called_once()
