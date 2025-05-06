
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, Contact

from BOT.handlers.registration.register_user import (
    callback_register_user, callback_register_admin, callback_help,
    cmd_start, process_full_name, process_phone_number, process_old_phone_check,
    process_old_phone_number, process_enrollment_year, process_graduation_year,
    process_department, process_specialty_input, process_specialty_selection,
    process_group_name, process_birth_date, handle_survey_response, user_main_menu_keyboard, Registration
)

@pytest.mark.asyncio
async def test_callback_register_user_sets_state():
    callback = AsyncMock()
    callback.message.answer = AsyncMock()
    state = AsyncMock()
    await callback_register_user(callback, state)
    callback.message.answer.assert_called_once()
    state.set_state.assert_called_with(Registration.full_name)

@pytest.mark.asyncio
async def test_callback_register_admin_response():
    callback = AsyncMock()
    callback.message.answer = AsyncMock()
    await callback_register_admin(callback)
    callback.message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_callback_help_response():
    callback = AsyncMock()
    callback.message.answer = AsyncMock()
    await callback_help(callback)
    callback.message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_cmd_start():
    message = AsyncMock()
    message.answer = AsyncMock()
    state = AsyncMock()
    await cmd_start(message, state)
    message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_process_full_name_valid():
    message = AsyncMock()
    message.text = "Іван Петренко"
    state = AsyncMock()
    await process_full_name(message, state)
    state.update_data.assert_called_once_with(full_name="Іван Петренко")
    state.set_state.assert_called_once_with(Registration.phone_number)

@pytest.mark.asyncio
async def test_process_full_name_invalid():
    message = AsyncMock()
    message.text = "Іван123"
    state = AsyncMock()
    await process_full_name(message, state)
    message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_process_phone_valid_text():
    message = AsyncMock()
    message.text = "+380991112233"
    message.contact = None
    state = AsyncMock()
    with patch("BOT.handlers.registration.register_user.is_valid_phone", return_value=True):
        await process_phone_number(message, state)
        state.update_data.assert_called_once_with(phone_number="+380991112233")
        state.set_state.assert_called_with(Registration.old_phone_number_check)

@pytest.mark.asyncio
async def test_process_old_phone_check_yes():
    message = AsyncMock()
    message.text = "так"
    state = AsyncMock()
    await process_old_phone_check(message, state)
    state.set_state.assert_called_with(Registration.old_phone_number)

@pytest.mark.asyncio
async def test_process_old_phone_check_no():
    message = AsyncMock()
    message.text = "ні"
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"phone_number": "+380991112233"})
    await process_old_phone_check(message, state)
    state.set_state.assert_called_with(Registration.enrollment_year)

@pytest.mark.asyncio
async def test_process_enrollment_year_valid():
    message = AsyncMock()
    message.text = "2020"
    state = AsyncMock()
    await process_enrollment_year(message, state)
    state.set_state.assert_called_with(Registration.graduation_year)

@pytest.mark.asyncio
async def test_process_graduation_year_less_than_enrollment():
    message = AsyncMock()
    message.text = "2019"
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"enrollment_year": 2020})
    await process_graduation_year(message, state)
    message.answer.assert_called()

@pytest.mark.asyncio
async def test_process_department_invalid():
    message = AsyncMock()
    message.text = "Unknown"
    state = AsyncMock()
    with patch("BOT.handlers.registration.register_user.normalize_department", return_value=None):
        await process_department(message, state)
        message.answer.assert_called_once()

@pytest.mark.asyncio
async def test_process_specialty_input_multiple_matches():
    message = AsyncMock()
    message.text = "12"
    state = AsyncMock()
    with patch("BOT.handlers.registration.register_user.search_specialty", return_value=[
        {"id": 1, "code": "121", "name": "Software Eng"},
        {"id": 2, "code": "122", "name": "CS"}
    ]):
        await process_specialty_input(message, state)
        state.set_state.assert_called_with(Registration.specialty_select)

@pytest.mark.asyncio
async def test_process_group_name_valid():
    message = AsyncMock()
    message.text = "ТВ-12"
    state = AsyncMock()
    await process_group_name(message, state)
    state.set_state.assert_called_with(Registration.birth_date)

@pytest.mark.asyncio
async def test_process_birth_date_invalid_format():
    message = AsyncMock()
    message.text = "31-12-2000"
    state = AsyncMock()
    await process_birth_date(message, state)
    message.answer.assert_called()

@pytest.mark.asyncio
async def test_handle_survey_response_yes():
    message = AsyncMock()
    message.text = "так"
    state = AsyncMock()
    await handle_survey_response(message, state)
    state.clear.assert_called_once()

@pytest.mark.asyncio
async def test_handle_survey_response_no():
    message = AsyncMock()
    message.text = "ні"
    state = AsyncMock()
    await handle_survey_response(message, state)
    state.clear.assert_called_once()

@pytest.mark.asyncio
async def test_process_birth_date_invalid_format():
    message = AsyncMock()
    message.text = "32.13.2022"
    state = AsyncMock()

    await process_birth_date(message, state)
    message.answer.assert_called_with("Неправильний формат дати. Введіть дату народження у форматі ДД.ММ.РРРР:")

@pytest.mark.asyncio
async def test_process_birth_date_too_young():
    message = AsyncMock()
    too_young = (datetime.today() - timedelta(days=10 * 365)).strftime("%d.%m.%Y")
    message.text = too_young
    state = AsyncMock()

    await process_birth_date(message, state)
    message.answer.assert_called_once()
    assert "Вам має бути щонайменше" in message.answer.call_args[0][0]

@pytest.mark.asyncio
async def test_process_birth_date_valid():
    message = AsyncMock()
    message.text = "01.01.2000"
    message.from_user.id = 12345
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={
        'full_name': 'Іван Петренко',
        'phone_number': '+380991112233',
        'old_phone_number': '+380991112233',
        'enrollment_year': 2018,
        'graduation_year': 2022,
        'department_id': 'ТЕФ',
        'specialty_id': 1,
        'group_name': 'ТВ-12',
        'birth_date': '01.01.2000' 
})


    with patch("BOT.handlers.registration.register_user.get_connection") as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor

        await process_birth_date(message, state)

        mock_cursor.execute.assert_called()
        message.answer.assert_any_call("✅ Реєстрація успішно завершена!")

@pytest.mark.asyncio
async def test_process_specialty_selection_invalid_choice():
    message = AsyncMock()
    message.text = "100"
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={'specialty_options': [{'id': 1}, {'id': 2}]})

    await process_specialty_selection(message, state)
    message.answer.assert_called_with("Некоректний вибір. Спробуйте ще раз:")

@pytest.mark.asyncio
async def test_process_group_name_invalid_format():
    message = AsyncMock()
    message.text = "1234"
    state = AsyncMock()

    await process_group_name(message, state)
    message.answer.assert_called_once()
    assert "Група повинна бути у форматі" in message.answer.call_args[0][0]

@pytest.mark.asyncio
async def test_process_old_phone_check_yes():
    message = AsyncMock()
    message.text = "так"
    state = AsyncMock()

    await process_old_phone_check(message, state)
    message.answer.assert_called_with("Введіть старий номер телефону:")

@pytest.mark.asyncio
async def test_process_old_phone_check_no():
    message = AsyncMock()
    message.text = "ні"
    state = AsyncMock()
    state.get_data = AsyncMock(return_value={"phone_number": "+380991112233"})

    await process_old_phone_check(message, state)
    state.update_data.assert_called_with(old_phone_number="+380991112233")
    message.answer.assert_called_with("Введіть рік вступу:")

@pytest.mark.asyncio
async def test_process_phone_number_invalid():
    message = AsyncMock()
    message.text = "123"
    message.contact = None
    state = AsyncMock()

    await process_phone_number(message, state)
    message.answer.assert_called()
    assert "Неправильний номер телефону" in message.answer.call_args[0][0]

@pytest.mark.asyncio
async def test_handle_survey_response_yes():
    message = AsyncMock()
    message.text = "так"
    state = AsyncMock()

    await handle_survey_response(message, state)
    message.answer.assert_any_call("🔗 Дякуємо! Перейдіть за посиланням на опитування:\nhttps://forms.gle/72mwaXVePPU5xVHK8")
    message.answer.assert_any_call("🏠 Ви в головному меню:", reply_markup=user_main_menu_keyboard)

@pytest.mark.asyncio
async def test_handle_survey_response_no():
    message = AsyncMock()
    message.text = "ні"
    state = AsyncMock()

    await handle_survey_response(message, state)
    message.answer.assert_any_call("🙌 Добре, можливо пізніше!")
    message.answer.assert_any_call("🏠 Ви в головному меню:", reply_markup=user_main_menu_keyboard)
