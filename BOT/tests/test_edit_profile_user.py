import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from aiogram.types import Message
from datetime import datetime
from BOT.handlers.edit.edit_profile_user import (
    edit_full_name, edit_phone_number, edit_group_name,
    edit_specialty, edit_enrollment_year, edit_graduation_year,
    edit_birth_date, EditProfile, choose_field_to_edit, back_to_user_menu
)

# ---------- Загальні фікстури ----------
@pytest.fixture
def mock_message():
    msg = MagicMock(spec=Message)
    msg.text = "Тестове Повідомлення"
    from_user = MagicMock()
    from_user.id = 12345
    msg.from_user = from_user
    msg.answer = AsyncMock()
    return msg

@pytest.fixture
def mock_state():
    state = AsyncMock()
    return state

# ---------- Тест для зміни ПІБ ----------
@pytest.mark.asyncio
async def test_edit_full_name_valid(mock_message, mock_state):
    mock_message.text = "Іван Петренко"
    with patch("BOT.handlers.edit.edit_profile_user.get_connection") as mock_conn, \
         patch("BOT.handlers.edit.edit_profile_user.show_edit_profile_menu_message", new_callable=AsyncMock):

        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor

        await edit_full_name(mock_message, mock_state)

        mock_cursor.execute.assert_called_once()
        mock_message.answer.assert_called_with("✅ ПІБ оновлено!")

@pytest.mark.asyncio
async def test_edit_full_name_invalid(mock_message, mock_state):
    mock_message.text = "Іван123"
    await edit_full_name(mock_message, mock_state)
    mock_message.answer.assert_called_with("❌ Ім'я повинно містити тільки літери і складатися з двох слів. Спробуйте ще раз:")

# ---------- Тест для зміни телефону ----------
@pytest.mark.asyncio
async def test_edit_phone_number_valid(mock_message, mock_state):
    mock_message.text = "+380501112233"
    with patch("BOT.handlers.edit.edit_profile_user.is_valid_phone", return_value=True), \
         patch("BOT.handlers.edit.edit_profile_user.get_connection") as mock_conn, \
         patch("BOT.handlers.edit.edit_profile_user.show_edit_profile_menu_message", new_callable=AsyncMock):

        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor

        await edit_phone_number(mock_message, mock_state)
        mock_message.answer.assert_called_with("✅ Номер телефону оновлено!")

@pytest.mark.asyncio
async def test_edit_phone_number_invalid(mock_message, mock_state):
    mock_message.text = "123abc"
    with patch("BOT.handlers.edit.edit_profile_user.is_valid_phone", return_value=False):
        await edit_phone_number(mock_message, mock_state)
        mock_message.answer.assert_called_with("❌ Неправильний номер. Введіть ще раз:")

# ---------- Тест для групи ----------
@pytest.mark.asyncio
async def test_edit_group_name_valid(mock_message, mock_state):
    mock_message.text = "тв-12"
    with patch("BOT.handlers.edit.edit_profile_user.get_connection") as mock_conn, \
         patch("BOT.handlers.edit.edit_profile_user.show_edit_profile_menu_message", new_callable=AsyncMock):

        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor

        await edit_group_name(mock_message, mock_state)
        mock_message.answer.assert_called_with("✅ Групу оновлено!")

@pytest.mark.asyncio
async def test_edit_group_name_invalid(mock_message, mock_state):
    mock_message.text = "група1"
    await edit_group_name(mock_message, mock_state)
    mock_message.answer.assert_called_with("❌ Неправильний формат групи. Введіть ще раз (наприклад: ТВ-12):")

# ---------- Тест для дати народження ----------
@pytest.mark.asyncio
async def test_edit_birth_date_valid(mock_message, mock_state):
    mock_message.text = "01.01.2000"
    with patch("BOT.handlers.edit.edit_profile_user.get_connection") as mock_conn, \
         patch("BOT.handlers.edit.edit_profile_user.show_edit_profile_menu_message", new_callable=AsyncMock):

        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor

        await edit_birth_date(mock_message, mock_state)
        mock_message.answer.assert_called_with("✅ Дату народження оновлено!")

@pytest.mark.asyncio
async def test_edit_birth_date_invalid(mock_message, mock_state):
    mock_message.text = "2000-01-01"
    await edit_birth_date(mock_message, mock_state)
    mock_message.answer.assert_called_with("❌ Неправильний формат дати. Введіть ще раз (ДД.ММ.РРРР):")

# ---------- Тест року вступу ----------
@pytest.mark.asyncio
async def test_edit_enrollment_year_valid(mock_message, mock_state):
    mock_message.text = "2020"
    with patch("BOT.handlers.edit.edit_profile_user.get_connection") as mock_conn, \
         patch("BOT.handlers.edit.edit_profile_user.show_edit_profile_menu_message", new_callable=AsyncMock):

        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor

        await edit_enrollment_year(mock_message, mock_state)
        mock_message.answer.assert_called_with("✅ Рік вступу оновлено на: 2020")

@pytest.mark.asyncio
async def test_edit_enrollment_year_invalid_format(mock_message, mock_state):
    mock_message.text = "двадцять"
    await edit_enrollment_year(mock_message, mock_state)
    mock_message.answer.assert_called_with("❌ Рік вступу має бути числом. Введіть ще раз:")

# ---------- Тест року випуску ----------
@pytest.mark.asyncio
async def test_edit_graduation_year_valid(mock_message, mock_state):
    mock_message.text = "2023"
    with patch("BOT.handlers.edit.edit_profile_user.get_connection") as mock_conn, \
         patch("BOT.handlers.edit.edit_profile_user.show_edit_profile_menu_message", new_callable=AsyncMock):

        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor

        await edit_graduation_year(mock_message, mock_state)
        mock_message.answer.assert_called_with("✅ Рік випуску оновлено на: 2023")

@pytest.mark.asyncio
async def test_edit_graduation_year_invalid_format(mock_message, mock_state):
    mock_message.text = "двадцять"
    await edit_graduation_year(mock_message, mock_state)
    mock_message.answer.assert_called_with("❌ Рік випуску має бути числом. Введіть ще раз:")

@pytest.mark.asyncio
async def test_edit_specialty_no_match(mock_message, mock_state):
    mock_message.text = "Невідома спец"
    with patch("BOT.handlers.edit.edit_profile_user.search_specialty", return_value=[]):
        await edit_specialty(mock_message, mock_state)
        mock_message.answer.assert_called_with("❌ Спеціальність не знайдена. Спробуйте ще раз:")

@pytest.mark.asyncio
async def test_edit_specialty_multiple_matches(mock_message, mock_state):
    mock_message.text = "інженер"
    with patch("BOT.handlers.edit.edit_profile_user.search_specialty", return_value=[
        {"name": "Інженерія", "code": "121"}, {"name": "Інженерія ПЗ", "code": "122"}
    ]):
        await edit_specialty(mock_message, mock_state)
        assert mock_message.answer.call_args[0][0].startswith("🔍 Знайдено декілька варіантів:")

@pytest.mark.asyncio
async def test_edit_specialty_single_valid_match(mock_message, mock_state):
    mock_message.text = "ПЗ"
    specialty = {"name": "Програмне забезпечення", "code": "121"}
    with patch("BOT.handlers.edit.edit_profile_user.search_specialty", return_value=[specialty]), \
         patch("BOT.handlers.edit.edit_profile_user.get_connection") as mock_conn, \
         patch("BOT.handlers.edit.edit_profile_user.show_edit_profile_menu_message", new_callable=AsyncMock):

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (42,)
        mock_conn.return_value.cursor.return_value = mock_cursor

        await edit_specialty(mock_message, mock_state)
        mock_message.answer.assert_called_with("✅ Спеціальність оновлено на: Програмне забезпечення (121)")

from unittest.mock import patch, MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_edit_specialty_not_in_db(mock_message, mock_state):
    mock_message.text = "ПЗ"
    specialty = {"name": "Програмне забезпечення", "code": "121"}
    with patch("BOT.handlers.edit.edit_profile_user.search_specialty", return_value=[specialty]), \
         patch("BOT.handlers.edit.edit_profile_user.get_connection") as mock_conn, \
         patch("BOT.handlers.edit.edit_profile_user.show_edit_profile_menu_message", new_callable=AsyncMock):

        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.return_value.cursor.return_value = mock_cursor

        await edit_specialty(mock_message, mock_state)
        mock_message.answer.assert_called_with("❌ Не знайдено спеціальність в базі. Спробуйте ще.")



@pytest.mark.asyncio
async def test_show_edit_profile_menu_user_not_found(mock_message, mock_state):
    with patch("BOT.handlers.edit.edit_profile_user.get_connection") as mock_conn:
        mock_conn.return_value.cursor.return_value.fetchone.return_value = None
        from BOT.handlers.edit.edit_profile_user import show_edit_profile_menu_message
        await show_edit_profile_menu_message(mock_message, mock_state)
        mock_message.answer.assert_called_with("❌ Дані не знайдено.", reply_markup=ANY, parse_mode="HTML")


@pytest.mark.asyncio
async def test_back_to_user_menu():
    mock_callback = AsyncMock()
    mock_callback.data = "back_to_user_menu"
    mock_callback.message.edit_text = AsyncMock()
    mock_state = AsyncMock()

    await back_to_user_menu(mock_callback, mock_state)

    mock_callback.message.edit_text.assert_called_once()
    mock_state.clear.assert_called_once()

@pytest.mark.asyncio
async def test_choose_field_to_edit_full_name():
    callback = AsyncMock()
    callback.data = "edit_full_name"
    callback.message.answer = AsyncMock()
    state = AsyncMock()

    await choose_field_to_edit(callback, state)
    callback.message.answer.assert_called_with("Введіть нове ПІБ (2 слова, тільки літери):")
    state.set_state.assert_called_with(EditProfile.editing_full_name)
