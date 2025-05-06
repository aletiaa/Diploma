import pytest
from types import SimpleNamespace
from aiogram.fsm.state import State
from BOT.handlers.edit.edit_profile_admin import (
    show_edit_admin_profile_menu_callback,
    show_edit_admin_profile_menu_message,
    choose_admin_field_to_edit,
    back_to_admin_menu,
    admin_data_edit_full_name,
    admin_data_edit_phone_number,
    EditAdminProfile,
)

# ✅ Тест: показ меню з даними адміністратора
@pytest.mark.asyncio
async def test_show_edit_admin_profile_menu_callback_found(monkeypatch):
    class DummyCursor:
        def execute(self, q, p): pass
        def fetchone(self): return ("Адмін Тест", "+380501234567")
    class DummyConn:
        def cursor(self): return DummyCursor()
        def close(self): pass

    monkeypatch.setattr("BOT.handlers.edit.edit_profile_admin.get_connection", lambda: DummyConn())

    called = {}
    class DummyMessage:
        async def edit_text(self, text, **kwargs): called["text"] = text
    callback = SimpleNamespace(
        from_user=SimpleNamespace(id=1),
        message=DummyMessage(),
        answer=dummy_answer  # тепер це awaitable
    )
    class DummyState:
        async def set_state(self, s): called["state"] = s

    await show_edit_admin_profile_menu_callback(callback, DummyState())
    assert "Ваші дані" in called["text"]
    assert called["state"] == EditAdminProfile.choosing_field

async def dummy_answer(): pass  # виправлення

# ❌ Тест: якщо дані адміністратора не знайдено
@pytest.mark.asyncio
async def test_show_edit_admin_profile_menu_callback_not_found(monkeypatch):
    class DummyCursor:
        def execute(self, q, p): pass
        def fetchone(self): return None
    class DummyConn:
        def cursor(self): return DummyCursor()
        def close(self): pass
    monkeypatch.setattr("BOT.handlers.edit.edit_profile_admin.get_connection", lambda: DummyConn())

    called = {}
    class DummyMessage:
        async def edit_text(self, text, **kwargs): called["text"] = text
    callback = SimpleNamespace(
        from_user=SimpleNamespace(id=1),
        message=DummyMessage(),
        answer=dummy_answer  # тепер це awaitable    
    )
    class DummyState:
        async def set_state(self, s): called["state"] = s

    await show_edit_admin_profile_menu_callback(callback, DummyState())
    assert "не знайдено" in called["text"]


# ✅ Повернення до головного меню
@pytest.mark.asyncio
async def test_back_to_admin_menu():
    called = {}
    class DummyMessage:
        async def edit_text(self, text, **kwargs): called["text"] = text
    class DummyState:
        async def clear(self): called["cleared"] = True

    callback = SimpleNamespace(message=DummyMessage())
    await back_to_admin_menu(callback, DummyState())

    assert "Повернулись до головного меню" in called["text"]
    assert called["cleared"] is True


# ✏️ Тест: вибір ПІБ для редагування
@pytest.mark.asyncio
async def test_choose_admin_field_to_edit_full_name():
    called = {}
    class DummyMessage:
        async def answer(self, text): called["text"] = text
    class DummyState:
        async def set_state(self, s): called["state"] = s

    callback = SimpleNamespace(data="admin_data_edit_full_name", message=DummyMessage())
    await choose_admin_field_to_edit(callback, DummyState())

    assert "ПІБ" in called["text"]
    assert called["state"] == EditAdminProfile.editing_full_name


# ❌ Некоректне ПІБ — відмова
@pytest.mark.asyncio
async def test_admin_data_edit_full_name_invalid():
    called = {}
    class DummyMessage:
        from_user = SimpleNamespace(id=1)
        text = "ОднеСлово"
        async def answer(self, text): called["text"] = text

    await admin_data_edit_full_name(DummyMessage(), state=None)
    assert "двох слів" in called["text"]


# ❌ Некоректний телефон — відмова
@pytest.mark.asyncio
async def test_admin_data_edit_phone_number_invalid(monkeypatch):
    called = {}
    monkeypatch.setattr("BOT.handlers.edit.edit_profile_admin.is_valid_phone", lambda p: False)

    class DummyMessage:
        from_user = SimpleNamespace(id=1)
        text = "123"
        async def answer(self, text): called["text"] = text

    await admin_data_edit_phone_number(DummyMessage(), state=None)
    assert "Неправильний номер" in called["text"]
