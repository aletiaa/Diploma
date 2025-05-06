import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.fsm.context import FSMContext
from BOT.handlers.login.login_user import (
    process_login_group, process_login_phone, start_user_login,user_main_menu_keyboard,
    UserLogin
)
from datetime import datetime, timedelta

@pytest.mark.asyncio
async def test_start_user_login():
    message = AsyncMock()
    state = AsyncMock()

    await start_user_login(message, state)

    state.update_data.assert_called_with(attempts=3)
    state.set_state.assert_called_with(UserLogin.phone_number)
    message.answer.assert_called_with("Введіть ваш номер телефону для входу:")


@pytest.mark.asyncio
async def test_process_login_phone_invalid():
    message = AsyncMock()
    message.text = "123abc"
    state = AsyncMock()

    with patch("BOT.handlers.login.login_user.is_valid_phone", return_value=False):
        await process_login_phone(message, state)

    message.answer.assert_called_with("Неправильний номер телефону. Введіть ще раз:")


@pytest.mark.asyncio
async def test_process_login_phone_valid():
    message = AsyncMock()
    message.text = "+380991112233"
    message.contact = None  # 🔑 Це ключ до правильного шляху
    state = AsyncMock()

    with patch("BOT.handlers.login.login_user.is_valid_phone", return_value=True):
        await process_login_phone(message, state)

    state.update_data.assert_called_with(phone_number="+380991112233")
    message.answer.assert_called_with("🔢 Введіть вашу групу (наприклад: ТВ-12):")
    state.set_state.assert_called_with(UserLogin.group_name)



@pytest.mark.asyncio
async def test_process_login_group_invalid_format():
    message = AsyncMock()
    message.text = "TV12"
    state = AsyncMock()

    await process_login_group(message, state)

    message.answer.assert_called_with(
        "Група повинна бути у форматі: 2 літери, тире, 2 цифри (наприклад: ТВ-12). Введіть ще раз:"
    )

@pytest.mark.asyncio
async def test_process_login_group_success():
    message = AsyncMock()
    message.text = "ТВ-12"
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"phone_number": "+380991112233"})

    with patch("BOT.handlers.login.login_user.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            (1, "Олена Тест", 0, None)  # Успішне співпадіння
        ]
        mock_conn.return_value.cursor.return_value = mock_cursor

        await process_login_group(message, state)

    message.answer.assert_any_call("✅ Вхід успішний! Вітаю, Олена Тест!", reply_markup=user_main_menu_keyboard)
    state.clear.assert_called_once()


@pytest.mark.asyncio
async def test_process_login_group_blocked():
    message = AsyncMock()
    message.text = "ТВ-12"
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"phone_number": "+380999999999"})

    recent_time = (datetime.now() - timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S")

    with patch("BOT.handlers.login.login_user.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            (1, "Blocked User", 3, recent_time)
        ]
        mock_conn.return_value.cursor.return_value = mock_cursor

        await process_login_group(message, state)

    assert "Спробуйте через" in message.answer.call_args[0][0]


@pytest.mark.asyncio
async def test_process_login_group_wrong_group():
    message = AsyncMock()
    message.text = "ТВ-12"
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"phone_number": "+380999999999"})

    with patch("BOT.handlers.login.login_user.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            None,  # перший запит повертає None (не знайдено за номером і групою)
            (2, 1)  # другий запит повертає існуючого користувача з 1 попередньою спробою
        ]
        mock_conn.return_value.cursor.return_value = mock_cursor

        await process_login_group(message, state)

    message.answer.assert_called_with("❌ Дані не знайдено або група не збігається. Спробуйте ще раз.")
    state.set_state.assert_called_with(UserLogin.phone_number)
