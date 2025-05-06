import pytest
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from datetime import datetime
from pathlib import Path
import csv
from types import SimpleNamespace

from BOT.handlers.communication.communication_admin import (
    open_admin_communication_menu,
    start_chat_creation,
    receive_chat_value,
    save_chat_link,
    ChatCreationState,
    CHAT_CSV_PATH,
)

# === FIXTURES ===

@pytest.fixture(autouse=True)
def clean_csv():
    if CHAT_CSV_PATH.exists():
        CHAT_CSV_PATH.unlink()
    yield
    if CHAT_CSV_PATH.exists():
        CHAT_CSV_PATH.unlink()

@pytest.fixture
def dummy_callback():
    class DummyMessage:
        async def edit_text(self, text, **kwargs):
            dummy_callback.called_text = text

        async def answer(self, text):
            dummy_callback.answered = text

    callback = SimpleNamespace(
        data="admin_communication_menu",
        message=DummyMessage()
    )
    return callback

@pytest.fixture
def dummy_message():
    class DummyMessage:
        text = "https://t.me/test_chat"
        bot = SimpleNamespace()
        async def answer(self, text):
            dummy_message.answered = text
    return DummyMessage()

# === TESTS ===
@pytest.mark.asyncio
async def test_open_admin_communication_menu():
    class DummyMessage:
        def __init__(self):
            self.called_text = None

        async def edit_text(self, text, **kwargs):
            self.called_text = text

        async def answer(self, text):
            self.answered = text

    dummy_msg = DummyMessage()
    dummy_callback = SimpleNamespace(data="admin_communication_menu", message=dummy_msg)

    await open_admin_communication_menu(dummy_callback, state=None)
    assert "<b>Меню спілкування:" in dummy_msg.called_text


@pytest.mark.asyncio
async def test_start_chat_creation_sets_state():
    called = {}

    class DummyState:
        async def update_data(self, **kwargs): called["update"] = kwargs
        async def set_state(self, state): called["set"] = state

    class DummyMessage:
        async def answer(self, text): called["answer"] = text

    callback = SimpleNamespace(
        data="create_specialty_chat",
        message=DummyMessage()
    )

    await start_chat_creation(callback, DummyState())
    assert called["update"]["chat_type"] == "create_specialty_chat"
    assert "код спеціальності" in called["answer"]
    assert called["set"] == ChatCreationState.entering_value

@pytest.mark.asyncio
async def test_save_chat_link_validation_and_write(monkeypatch):
    called = {}
    CHAT_CSV_PATH.write_text("year,link,specialty\n", encoding="utf-8")

    class DummyFSMContext:
        async def get_data(self):
            return {"chat_type": "create_year_chat", "chat_value": "2020"}
        async def clear(self):
            called["cleared"] = True

    class DummyMessage:
        text = "https://t.me/test2020chat"
        bot = SimpleNamespace()
        async def answer(self, text): called["answer"] = text

    async def dummy_notify_users_about_chat(**kwargs):
        called["notified"] = True

    monkeypatch.setattr("BOT.handlers.communication.communication_admin.notify_users_about_chat", dummy_notify_users_about_chat)

    await save_chat_link(DummyMessage(), DummyFSMContext())

    assert "збережено" in called["answer"]
    assert called["notified"]

    # Перевірка, що записалось у CSV
    with CHAT_CSV_PATH.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        assert any(r["year"] == "2020" and r["link"] == "https://t.me/test2020chat" for r in rows)

@pytest.mark.asyncio
async def test_save_chat_link_invalid_url(monkeypatch):
    """
    ❌ Перевіряє, що бот відмовляє, якщо посилання не починається з https://t.me/ або https://telegram.me/.
    Очікується повідомлення з помилкою та без запису в CSV.
    """

    context_data = {"chat_type": "create_year_chat", "chat_value": "2022"}
    called = {}

    # Підроблена FSMContext
    class DummyFSMContext:
        async def get_data(self): return context_data
        async def clear(self): called["cleared"] = True

    # Підроблений Message з невалідним посиланням
    class DummyMessage:
        text = "http://invalid.com/chat"
        async def answer(self, text): called["answer"] = text

    await save_chat_link(DummyMessage(), DummyFSMContext())

    # Перевірка, що бот повідомив про помилку
    assert "повинно починатися з https://t.me/" in called["answer"]
    assert "cleared" not in called  # FSM не повинен очищуватись

@pytest.mark.asyncio
async def test_save_chat_link_duplicate_entry(monkeypatch):
    """
    📎 Якщо у CSV вже існує запис для спеціальності '122',
    бот не повинен дозволити додавання дубліката.
    Очікується повідомлення про наявність чату та очищення FSM.
    """

    # CSV з уже існуючим записом для 122
    CHAT_CSV_PATH.write_text("year,link,specialty\n,https://t.me/exist,122\n", encoding="utf-8")

    context_data = {"chat_type": "create_specialty_chat", "chat_value": "122"}
    called = {}

    class DummyFSMContext:
        async def get_data(self): return context_data
        async def clear(self): called["cleared"] = True
        async def update_data(self, **kwargs): called["updated"] = kwargs
        async def set_state(self, state): called["state_set"] = state

    class DummyMessage:
        text = "122"  # чат_value передається з повідомлення
        async def answer(self, text): called["answer"] = text

    await receive_chat_value(DummyMessage(), DummyFSMContext())

    assert "вже існує" in called["answer"]
    assert called.get("cleared") is True

@pytest.mark.asyncio
async def test_admin_creates_same_year_twice(monkeypatch):
    """
    🔁 Якщо у CSV вже є чат для року '2020',
    бот має попередити про дублікат і завершити FSM.
    """

    # CSV з уже існуючим роком 2020
    CHAT_CSV_PATH.write_text("year,link,specialty\n2020,https://t.me/exist,\n", encoding="utf-8")

    context_data = {"chat_type": "create_year_chat", "chat_value": "2020"}
    called = {}

    class DummyFSMContext:
        async def get_data(self): return context_data
        async def clear(self): called["cleared"] = True
        async def update_data(self, **kwargs): called["updated"] = kwargs
        async def set_state(self, state): called["state_set"] = state

    class DummyMessage:
        text = "2020"
        async def answer(self, text): called["answer"] = text

    await receive_chat_value(DummyMessage(), DummyFSMContext())

    assert "вже існує" in called["answer"]
    assert called.get("cleared") is True