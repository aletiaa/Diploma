import pytest
import csv
from types import SimpleNamespace
from pathlib import Path
from BOT.handlers.communication.communication_user import (
    open_communication_menu,
    send_group_chat_link,
    send_communication_link,
    CHAT_CSV_PATH
)

# === ФІКСТУРА для очищення CSV-файлу перед і після кожного тесту ===
@pytest.fixture(autouse=True)
def clean_csv():
    """
    🧹 Перед кожним тестом — видаляємо CSV-файл, якщо він існує.
    Після тесту — також видаляємо, щоб не заважав іншим тестам.
    """
    if CHAT_CSV_PATH.exists():
        CHAT_CSV_PATH.unlink()
    yield
    if CHAT_CSV_PATH.exists():
        CHAT_CSV_PATH.unlink()

# === ФІКСТУРА для підробленого callback об'єкта (користувача Telegram) ===
@pytest.fixture
def dummy_callback():
    """
    📩 Створює підроблений callback-об'єкт з фіктивним повідомленням та ID користувача.
    """
    class DummyMessage:
        async def edit_text(self, text, **kwargs):
            # Зберігаємо текст, який бот надішле при edit_text
            dummy_callback.called_text = text

        async def answer(self, text):
            # Зберігаємо відповідь бота
            dummy_callback.answered = text

    return SimpleNamespace(
        data="user_communication_menu",
        from_user=SimpleNamespace(id=123),
        message=DummyMessage()
    )

# === ТЕСТ: Відкриття меню спілкування користувача ===
@pytest.mark.asyncio
async def test_open_communication_menu():
    """
    ✅ Перевіряє, що при натисканні на кнопку 'Спілкування',
    бот відправляє правильне текстове повідомлення з меню.
    """

    class DummyMessage:
        def __init__(self):
            self.called_text = None  # зберігатимемо текст, який надішле бот

        async def edit_text(self, text, **kwargs):
            self.called_text = text

        async def answer(self, text):
            self.answered = text

    dummy_msg = DummyMessage()

    # Симулюємо callback від Telegram-користувача
    dummy_callback = SimpleNamespace(
        data="user_communication_menu",  # значення data відповідає маршруту
        from_user=SimpleNamespace(id=123),
        message=dummy_msg
    )

    # Викликаємо обробник функції
    await open_communication_menu(dummy_callback, state=None)

    # Перевіряємо, що бот відправив меню з текстом про спілкування
    assert "👥 Спілкування" in dummy_msg.called_text

# === GROUP CHAT TEST ===

# === ТЕСТ: Коли чат для групи знайдено в CSV ===
@pytest.mark.asyncio
async def test_send_group_chat_link_found(monkeypatch):
    """
    ✅ Перевіряє, що якщо в CSV існує чат для групи користувача (A-21),
    бот повертає правильне посилання.
    """

    # Створюємо CSV-файл із записом для групи A-21
    CHAT_CSV_PATH.write_text("group,link\nA-21,https://t.me/groupA21\n", encoding="utf-8")

    # Мокаємо SQLite-запит до БД: користувач належить до групи A-21
    class DummyCursor:
        def execute(self, sql, params): self.result = ("A-21",)
        def fetchone(self): return self.result

    class DummyConnection:
        def cursor(self): return DummyCursor()
        def close(self): pass

    # Підміна функції get_connection() на фейкове з'єднання
    monkeypatch.setattr("BOT.handlers.communication.communication_user.get_connection", lambda: DummyConnection())

    # Створюємо фейкове повідомлення з answer()
    class DummyMessage:
        async def answer(self, text): DummyMessage.answered = text

    # Формуємо фейковий callback з потрібними даними
    callback = SimpleNamespace(
        data="chat_by_group",
        from_user=SimpleNamespace(id=1),
        message=DummyMessage()
    )

    # Викликаємо обробник
    await send_group_chat_link(callback, state=None)

    # Перевіряємо, що бот відповів правильним посиланням
    assert "https://t.me/groupA21" in DummyMessage.answered

# === ТЕСТ: Коли чат для групи НЕ знайдено в CSV ===
@pytest.mark.asyncio
async def test_send_group_chat_link_not_found(monkeypatch):
    """
    ❌ Перевіряє, що якщо група користувача (A-21) не знайдена в CSV,
    бот повідомляє, що чат ще не створено.
    """

    # CSV містить іншу групу (B-22), тому чат не має знайтись
    CHAT_CSV_PATH.write_text("group,link\nB-22,https://t.me/groupB22\n", encoding="utf-8")

    # Мокаємо повернення групи A-21 з БД
    class DummyCursor:
        def execute(self, sql, params): self.result = ("A-21",)
        def fetchone(self): return self.result

    class DummyConnection:
        def cursor(self): return DummyCursor()
        def close(self): pass

    monkeypatch.setattr("BOT.handlers.communication.communication_user.get_connection", lambda: DummyConnection())

    class DummyMessage:
        async def answer(self, text): DummyMessage.answered = text

    callback = SimpleNamespace(
        data="chat_by_group",
        from_user=SimpleNamespace(id=1),
        message=DummyMessage()
    )

    await send_group_chat_link(callback, state=None)

    # Перевіряємо, що бот повідомив про відсутність чату
    assert "ще не створено" in DummyMessage.answered

@pytest.mark.asyncio
async def test_chat_by_specialty_found(monkeypatch):
    """
    ✅ Перевіряємо, що якщо код спеціальності користувача (122) знайдено в chat_links.csv,
    бот надає правильне посилання на чат.
    """

    # Створюємо CSV-файл із чатом для спеціальності 122
    CHAT_CSV_PATH.write_text("specialty,link\n122,https://t.me/spec122\n", encoding="utf-8")

    # Підроблені SQL-запити
    class DummyCursor:
        def execute(self, query, params):
            # Перший запит: знайдено specialty_id = 1
            if "specialty_id" in query:
                self.result = (1,)
            # Другий запит: по цьому ID знайдено код "122"
            elif "code" in query:
                self.result = ("122",)
        def fetchone(self): return self.result

    class DummyConn:
        def cursor(self): return DummyCursor()
        def close(self): pass

    # Підміна з'єднання з базою даних
    monkeypatch.setattr("BOT.handlers.communication.communication_user.get_connection", lambda: DummyConn())

    # Фейковий об'єкт повідомлення
    class DummyMessage:
        async def answer(self, text): DummyMessage.answered = text

    # Симулюємо callback від користувача
    callback = SimpleNamespace(
        data="chat_by_specialty",
        from_user=SimpleNamespace(id=1),
        message=DummyMessage()
    )

    # Викликаємо функцію обробки
    await send_communication_link(callback, state=None)

    # Перевірка, що відповідь містить правильне посилання
    assert "https://t.me/spec122" in DummyMessage.answered

@pytest.mark.asyncio
async def test_chat_by_specialty_not_found(monkeypatch):
    """
    ❌ Перевіряємо, що якщо код спеціальності користувача (122) відсутній у chat_links.csv,
    бот повідомляє, що чат ще не створено.
    """

    # Створюємо CSV-файл із іншим кодом спеціальності (121)
    CHAT_CSV_PATH.write_text("specialty,link\n121,https://t.me/spec121\n", encoding="utf-8")

    class DummyCursor:
        def execute(self, query, params):
            # Як і раніше: ID спеціальності = 1 → код = "122"
            if "specialty_id" in query:
                self.result = (1,)
            elif "code" in query:
                self.result = ("122",)
        def fetchone(self): return self.result

    class DummyConn:
        def cursor(self): return DummyCursor()
        def close(self): pass

    monkeypatch.setattr("BOT.handlers.communication.communication_user.get_connection", lambda: DummyConn())

    class DummyMessage:
        async def answer(self, text): DummyMessage.answered = text

    callback = SimpleNamespace(
        data="chat_by_specialty",
        from_user=SimpleNamespace(id=1),
        message=DummyMessage()
    )

    await send_communication_link(callback, state=None)

    # Бот повинен повідомити, що чат ще не створено
    assert "ще не створено" in DummyMessage.answered

@pytest.mark.asyncio
async def test_chat_by_specialty_user_not_found(monkeypatch):
    """
    ❌ Перевіряє, що якщо у базі немає specialty_id для користувача,
    бот повідомляє про помилку отримання спеціальності.
    """

    class DummyCursor:
        def execute(self, query, params):
            if "specialty_id" in query:
                self.result = None  # Запит нічого не знайшов
        def fetchone(self): return self.result

    class DummyConn:
        def cursor(self): return DummyCursor()
        def close(self): pass

    # Підміна функції get_connection
    monkeypatch.setattr("BOT.handlers.communication.communication_user.get_connection", lambda: DummyConn())

    class DummyMessage:
        async def answer(self, text): DummyMessage.answered = text

    callback = SimpleNamespace(
        data="chat_by_specialty",
        from_user=SimpleNamespace(id=1),
        message=DummyMessage()
    )

    await send_communication_link(callback, state=None)

    # Очікуємо повідомлення про відсутність спеціальності
    assert "Не вдалося отримати вашу спеціальність" in DummyMessage.answered

@pytest.mark.asyncio
async def test_chat_by_enrollment_found(monkeypatch):
    """
    ✅ Якщо в базі є рік вступу (2021), і в chat_links.csv є відповідний чат,
    бот має надіслати посилання.
    """

    # Створюємо запис у CSV
    CHAT_CSV_PATH.write_text("enrollment_year,link\n2021,https://t.me/enroll2021\n", encoding="utf-8")

    class DummyCursor:
        def execute(self, query, params):
            self.result = (2021,)  # Запит до users.enrollment_year
        def fetchone(self): return self.result

    class DummyConn:
        def cursor(self): return DummyCursor()
        def close(self): pass

    monkeypatch.setattr("BOT.handlers.communication.communication_user.get_connection", lambda: DummyConn())

    class DummyMessage:
        async def answer(self, text): DummyMessage.answered = text

    callback = SimpleNamespace(
        data="chat_by_enrollment",
        from_user=SimpleNamespace(id=1),
        message=DummyMessage()
    )

    await send_communication_link(callback, state=None)

    assert "https://t.me/enroll2021" in DummyMessage.answered

@pytest.mark.asyncio
async def test_chat_by_enrollment_not_found(monkeypatch):
    """
    ❌ Перевіряє, що якщо рік вступу користувача не відповідає жодному запису в chat_links.csv,
    бот повідомляє, що чат ще не створено.
    """

    # CSV-файл не містить чату для 2021 року
    CHAT_CSV_PATH.write_text("enrollment_year,link\n2020,https://t.me/enroll2020\n", encoding="utf-8")

    class DummyCursor:
        def execute(self, query, params):
            self.result = (2021,)  # БД повертає рік вступу, якого немає в CSV
        def fetchone(self): return self.result

    class DummyConn:
        def cursor(self): return DummyCursor()
        def close(self): pass

    monkeypatch.setattr("BOT.handlers.communication.communication_user.get_connection", lambda: DummyConn())

    class DummyMessage:
        async def answer(self, text): DummyMessage.answered = text

    callback = SimpleNamespace(
        data="chat_by_enrollment",
        from_user=SimpleNamespace(id=1),
        message=DummyMessage()
    )

    await send_communication_link(callback, state=None)

    assert "ще не створено" in DummyMessage.answered

@pytest.mark.asyncio
async def test_chat_by_enrollment_user_not_found(monkeypatch):
    """
    ❌ Перевіряє ситуацію, коли у базі не знайдено рік вступу для користувача.
    Очікується повідомлення про неможливість отримати рік вступу.
    """

    class DummyCursor:
        def execute(self, query, params): self.result = None  # fetchone() поверне None
        def fetchone(self): return self.result

    class DummyConn:
        def cursor(self): return DummyCursor()
        def close(self): pass

    monkeypatch.setattr("BOT.handlers.communication.communication_user.get_connection", lambda: DummyConn())

    class DummyMessage:
        async def answer(self, text): DummyMessage.answered = text

    callback = SimpleNamespace(
        data="chat_by_enrollment",
        from_user=SimpleNamespace(id=1),
        message=DummyMessage()
    )

    await send_communication_link(callback, state=None)

    assert "Не вдалося отримати рік вступу" in DummyMessage.answered

@pytest.mark.asyncio
async def test_chat_by_graduation_found(monkeypatch):
    """
    ✅ Перевіряємо, що якщо рік випуску користувача знайдено в базі та є відповідний запис у CSV,
    бот надає посилання на чат.
    """

    # Створення CSV-файлу з чатом для 2025 року
    CHAT_CSV_PATH.write_text("graduation_year,link\n2025,https://t.me/grad2025\n", encoding="utf-8")

    class DummyCursor:
        def execute(self, query, params): self.result = (2025,)  # БД повертає 2025
        def fetchone(self): return self.result

    class DummyConn:
        def cursor(self): return DummyCursor()
        def close(self): pass

    monkeypatch.setattr("BOT.handlers.communication.communication_user.get_connection", lambda: DummyConn())

    class DummyMessage:
        async def answer(self, text): DummyMessage.answered = text

    callback = SimpleNamespace(
        data="chat_by_graduation",
        from_user=SimpleNamespace(id=1),
        message=DummyMessage()
    )

    await send_communication_link(callback, state=None)

    assert "https://t.me/grad2025" in DummyMessage.answered

@pytest.mark.asyncio
async def test_chat_by_graduation_not_found(monkeypatch):
    """
    ❌ Перевіряє ситуацію, коли рік випуску користувача знайдено, але в CSV-файлі немає чату для цього року.
    Очікується повідомлення, що чат ще не створено.
    """

    # CSV містить запис лише для 2024 року
    CHAT_CSV_PATH.write_text("graduation_year,link\n2024,https://t.me/grad2024\n", encoding="utf-8")

    class DummyCursor:
        def execute(self, query, params): self.result = (2025,)  # БД повертає 2025
        def fetchone(self): return self.result

    class DummyConn:
        def cursor(self): return DummyCursor()
        def close(self): pass

    monkeypatch.setattr("BOT.handlers.communication.communication_user.get_connection", lambda: DummyConn())

    class DummyMessage:
        async def answer(self, text): DummyMessage.answered = text

    callback = SimpleNamespace(
        data="chat_by_graduation",
        from_user=SimpleNamespace(id=1),
        message=DummyMessage()
    )

    await send_communication_link(callback, state=None)

    assert "ще не створено" in DummyMessage.answered

@pytest.mark.asyncio
async def test_chat_by_graduation_user_not_found(monkeypatch):
    """
    ❌ Перевіряє ситуацію, коли рік випуску (graduation_year) для користувача
    не знайдено в базі даних (fetchone() → None).
    
    Очікуємо, що бот відповість повідомленням про помилку.
    """

    # Підроблена реалізація курсора бази даних
    class DummyCursor:
        def execute(self, query, params):
            # Усі запити повертають None — значення не знайдено
            self.result = None
        def fetchone(self):
            return self.result

    # Підроблене з'єднання з БД, яке повертає курсор
    class DummyConn:
        def cursor(self):
            return DummyCursor()
        def close(self):
            pass

    # Підміна get_connection так, щоб він повертав DummyConn
    monkeypatch.setattr(
        "BOT.handlers.communication.communication_user.get_connection",
        lambda: DummyConn()
    )

    # Фейковий об'єкт повідомлення з методом answer()
    class DummyMessage:
        async def answer(self, text):
            DummyMessage.answered = text  # Зберігаємо відповідь бота

    # Створення об'єкта callback для chat_by_graduation
    callback = SimpleNamespace(
        data="chat_by_graduation",
        from_user=SimpleNamespace(id=1),
        message=DummyMessage()
    )

    # Виклик функції, яка має обробити запит
    await send_communication_link(callback, state=None)

    # Перевірка, що бот відповів повідомленням про помилку
    assert "Не вдалося отримати рік випуску" in DummyMessage.answered

@pytest.mark.asyncio
async def test_chat_by_unknown_type(monkeypatch):
    """
    🔍 Тестуємо ситуацію, коли callback.data містить невідомий тип (не specialty, enrollment, graduation).
    Очікуємо відповідь про помилку типу чату.
    """

    # Мокаємо з'єднання з базою (воно не використається, бо бот зразу поверне помилку)
    class DummyConn:
        def cursor(self): return None
        def close(self): pass

    monkeypatch.setattr("BOT.handlers.communication.communication_user.get_connection", lambda: DummyConn())

    # Створюємо повідомлення з відстеженням відповіді
    class DummyMessage:
        async def answer(self, text): DummyMessage.answered = text

    # Вставляємо несподіване значення типу
    callback = SimpleNamespace(
        data="chat_by_unknown",
        from_user=SimpleNamespace(id=1),
        message=DummyMessage()
    )

    # Викликаємо функцію
    await send_communication_link(callback, state=None)

    # Перевіряємо, що бот відповів відповідним повідомленням про помилку
    assert "Невідомий тип чату" in DummyMessage.answered

@pytest.mark.asyncio
async def test_chat_csv_not_exists(monkeypatch):
    """
    📂 Тестуємо ситуацію, коли CSV-файл chat_links.csv взагалі відсутній.
    Очікуємо повідомлення про відсутність чатів.
    """

    # Видаляємо файл перед тестом (на випадок, якщо він існує)
    if CHAT_CSV_PATH.exists():
        CHAT_CSV_PATH.unlink()

    class DummyCursor:
        def execute(self, query, params): self.result = (2021,)
        def fetchone(self): return self.result

    class DummyConn:
        def cursor(self): return DummyCursor()
        def close(self): pass

    monkeypatch.setattr("BOT.handlers.communication.communication_user.get_connection", lambda: DummyConn())

    class DummyMessage:
        async def answer(self, text): DummyMessage.answered = text

    callback = SimpleNamespace(
        data="chat_by_enrollment",
        from_user=SimpleNamespace(id=1),
        message=DummyMessage()
    )

    await send_communication_link(callback, state=None)
    assert "Жодного чату ще не створено" in DummyMessage.answered

@pytest.mark.asyncio
async def test_chat_csv_empty_file(monkeypatch):
    """
    📭 Тестуємо ситуацію, коли CSV-файл існує, але не містить жодного запису.
    Очікуємо повідомлення, що чат ще не створено.
    """

    # Створюємо CSV-файл лише з заголовком
    CHAT_CSV_PATH.write_text("enrollment_year,link\n", encoding="utf-8")

    class DummyCursor:
        def execute(self, query, params): self.result = (2021,)
        def fetchone(self): return self.result

    class DummyConn:
        def cursor(self): return DummyCursor()
        def close(self): pass

    monkeypatch.setattr("BOT.handlers.communication.communication_user.get_connection", lambda: DummyConn())

    class DummyMessage:
        async def answer(self, text): DummyMessage.answered = text

    callback = SimpleNamespace(
        data="chat_by_enrollment",
        from_user=SimpleNamespace(id=1),
        message=DummyMessage()
    )

    await send_communication_link(callback, state=None)
    assert "ще не створено" in DummyMessage.answered