import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from aiogram.types import Message, CallbackQuery
from BOT.handlers.registration.register_admin import (
    start_admin_register, admin_full_name, admin_phone_number,
    approve_admin, reject_admin, generate_random_password, AdminRegistration
)

@pytest.mark.asyncio
async def test_start_admin_register_sets_state():
    message = AsyncMock()
    state = AsyncMock()
    await start_admin_register(message, state)
    message.answer.assert_called_once()
    state.set_state.assert_called_with(AdminRegistration.full_name)

@pytest.mark.asyncio
async def test_admin_full_name_invalid_format():
    message = AsyncMock(text="Іван")
    state = AsyncMock()
    await admin_full_name(message, state)
    message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_admin_full_name_valid():
    message = AsyncMock(text="Іван Петренко")
    state = AsyncMock()
    await admin_full_name(message, state)
    state.update_data.assert_called_once_with(full_name="Іван Петренко")

@pytest.mark.asyncio
async def test_admin_phone_number_invalid_format():
    message = AsyncMock()
    message.text = "invalid"
    message.contact = None
    state = AsyncMock()
    bot = AsyncMock()
    with patch("BOT.handlers.registration.register_admin.is_valid_phone", return_value=False):
        await admin_phone_number(message, state, bot)
        message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_reject_admin_logic():
    callback = AsyncMock()
    callback.data = "reject_admin_777"
    bot = AsyncMock()
    with patch("BOT.handlers.registration.register_admin.get_connection") as mock_conn:
        mock_conn.return_value.cursor.return_value = MagicMock()
        await reject_admin(callback, bot)
        callback.message.answer.assert_called_once()
        bot.send_message.assert_called_once()

@pytest.mark.asyncio
async def test_generate_random_password_length():
    password = generate_random_password(10)
    assert len(password) == 10
    assert any(c.isdigit() for c in password)
    assert any(c.isalpha() for c in password)

@pytest.mark.asyncio
async def test_admin_phone_number_duplicate_request():
    message = AsyncMock()
    message.text = "+380501234567"
    message.contact = None
    message.from_user.id = 12345
    state = AsyncMock()
    bot = AsyncMock()

    with patch("BOT.handlers.registration.register_admin.is_valid_phone", return_value=True), \
         patch("BOT.handlers.registration.register_admin.get_connection") as mock_conn, \
         patch("BOT.handlers.registration.register_admin.generate_random_password", return_value="abc12345"):
        cursor = mock_conn.return_value.cursor.return_value
        cursor.fetchone.return_value = True  # Уже є заявка

        await admin_phone_number(message, state, bot)
        message.answer.assert_called_with("🕓 Ваша заявка вже на розгляді.")

@pytest.mark.asyncio
async def test_approve_admin_already_exists():
    callback = AsyncMock()
    callback.data = "approve_admin_123"
    bot = AsyncMock()

    with patch("BOT.handlers.registration.register_admin.get_connection") as mock_conn:
        cursor = mock_conn.return_value.cursor.return_value
        cursor.fetchone.side_effect = [("ПІБ", "+380501234567", "pass123"), True]  # user found + already in admins

        await approve_admin(callback, bot)
        callback.message.answer.assert_called_with("⚠️ Адміністратор вже існує.")

@pytest.mark.asyncio
async def test_approve_admin_successful():
    callback = AsyncMock()
    callback.data = "approve_admin_123"
    bot = AsyncMock()

    with patch("BOT.handlers.registration.register_admin.get_connection") as mock_conn:
        cursor = mock_conn.return_value.cursor.return_value
        cursor.fetchone.side_effect = [("Test Admin", "+380501234567", "pwd123"), None]  # found, not existing

        await approve_admin(callback, bot)

        callback.message.answer.assert_called_with("✅ Адміністратора підтверджено.")
        bot.send_message.assert_called_once()