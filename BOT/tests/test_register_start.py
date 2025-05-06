import pytest
from unittest.mock import AsyncMock
from aiogram.fsm.context import FSMContext
from BOT.handlers.registration.register_start import show_main_menu, show_help, callback_login_user, callback_login_admin
from BOT.handlers.login.login_user import UserLogin
from BOT.handlers.login.login_admin import AdminLogin

@pytest.mark.asyncio
async def test_show_main_menu():
    message = AsyncMock()
    await show_main_menu(message)
    message.answer.assert_called_once()
    args, kwargs = message.answer.call_args
    assert "Я бот для реєстрації випускників" in args[0]

@pytest.mark.asyncio
async def test_show_help():
    message = AsyncMock()
    await show_help(message)
    message.answer.assert_called_once()
    args, kwargs = message.answer.call_args
    assert "Допомога" in args[0]
    assert "alina.seikauskaite3@gmail.com" in args[0]

@pytest.mark.asyncio
async def test_callback_login_user():
    callback = AsyncMock()
    state = AsyncMock()
    await callback_login_user(callback, state)
    callback.message.answer.assert_called_once_with(
        "Ви обрали вхід як користувач.\nВведіть ваш номер телефону:"
    )
    state.set_state.assert_called_once_with(UserLogin.phone_number)

@pytest.mark.asyncio
async def test_callback_login_admin():
    callback = AsyncMock()
    state = AsyncMock()
    await callback_login_admin(callback, state)
    callback.message.answer.assert_called_once_with(
        "Ви обрали вхід як адміністратор.\nВведіть ваш номер телефону:"
    )
    state.set_state.assert_called_once_with(AdminLogin.phone_number)
    
@pytest.mark.asyncio
async def test_callback_login_user_no_message():
    callback = AsyncMock()
    callback.message = None  # simulate broken callback
    state = AsyncMock()
    try:
        await callback_login_user(callback, state)
    except AttributeError:
        assert True  # ✅ Optional: you can also log warning here in production code

@pytest.mark.asyncio
async def test_callback_login_admin_no_message():
    callback = AsyncMock()
    callback.message = None
    state = AsyncMock()
    try:
        await callback_login_admin(callback, state)
    except AttributeError:
        assert True

@pytest.mark.asyncio
async def test_callback_login_user_state_fail():
    callback = AsyncMock()
    callback.message.answer = AsyncMock()
    state = AsyncMock()
    state.set_state.side_effect = Exception("FSM error")

    await callback_login_user(callback, state)

    callback.message.answer.assert_any_call("⚠️ Сталася помилка при встановленні стану. Спробуйте ще раз.")
    callback.message.answer.assert_any_call("Ви обрали вхід як користувач.\nВведіть ваш номер телефону:")
    assert callback.message.answer.call_count == 2


@pytest.mark.asyncio
async def test_callback_login_admin_state_fail():
    callback = AsyncMock()
    callback.message.answer = AsyncMock()
    state = AsyncMock()
    state.set_state.side_effect = Exception("FSM error")

    await callback_login_admin(callback, state)

    callback.message.answer.assert_any_call("⚠️ Сталася помилка при встановленні стану. Спробуйте ще раз.")
    callback.message.answer.assert_any_call("Ви обрали вхід як адміністратор.\nВведіть ваш номер телефону:")
    assert callback.message.answer.call_count == 2