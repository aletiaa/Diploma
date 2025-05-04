import sqlite3
from .models import User, Specialty

# Загальна функція для підключення
def get_connection():
    return sqlite3.connect("alumni.db")

# ▸ Отримати користувача за telegram_id
def get_user_by_telegram_id(telegram_id: str) -> User | None:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return User(*row)
    return None


# ▸ Оновити конкретне поле користувача (з перевіркою)
def update_user_field(telegram_id: str, field: str, value):
    allowed_fields = {
        "full_name", "phone_number", "old_phone_number", "graduation_year",
        "department_id", "specialty_id", "group_name", "role", "access_level", "birth_date"
    }

    if field not in allowed_fields:
        raise ValueError(f"Неприпустиме поле для оновлення: {field}")

    conn = get_connection()
    c = conn.cursor()
    c.execute(f"UPDATE users SET {field} = ? WHERE telegram_id = ?", (value, telegram_id))
    conn.commit()
    conn.close()


# ▸ Отримати всі спеціальності (для пошуку або відображення)
def get_all_specialties() -> list[Specialty]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, code, name FROM specialties")
    rows = c.fetchall()
    conn.close()
    return [Specialty(*row) for row in rows]


# ▸ Отримати id спеціальності за code і name
def get_specialty_id_by_code_name(code: str, name: str) -> int | None:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM specialties WHERE code = ? AND name = ?", (code, name))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return None


# ▸ Отримати користувача разом з назвами спеціальності (для відображення профілю)
def get_user_profile_data(telegram_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.full_name, u.phone_number, u.group_name, s.name, s.code, u.graduation_year, u.birth_date
        FROM users u
        LEFT JOIN specialties s ON u.specialty_id = s.id
        WHERE u.telegram_id = ?
    ''', (telegram_id,))
    row = cursor.fetchone()
    conn.close()
    return row  # повертає кортеж або None


# ▸ Додати нового користувача (якщо буде потрібно)
def insert_new_user(user: User):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (
            telegram_id, full_name, phone_number, old_phone_number, graduation_year,
            department_id, specialty_id, group_name, role, access_level, birth_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user.telegram_id, user.full_name, user.phone_number, user.old_phone_number, user.graduation_year,
        user.department_id, user.specialty_id, user.group_name, user.role, user.access_level, user.birth_date
    ))
    conn.commit()
    conn.close()


# ▸ Перевірка існування користувача
def user_exists(telegram_id: str) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

def create_event(title, description, event_datetime, max_seats):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO events (title, description, event_datetime, max_seats, available_seats)
           VALUES (?, ?, ?, ?, ?)''',
        (title, description, event_datetime, max_seats, max_seats)
    )
    conn.commit()
    conn.close()

def get_all_events():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events ORDER BY event_datetime')
    events = cursor.fetchall()
    conn.close()
    return events

def get_event_by_id(event_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events WHERE id = ?', (event_id,))
    event = cursor.fetchone()
    conn.close()
    return event

def update_event(event_id, title, description, event_datetime, max_seats, available_seats):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''UPDATE events
           SET title = ?, description = ?, event_datetime = ?, max_seats = ?, available_seats = ?
           WHERE id = ?''',
        (title, description, event_datetime, max_seats, available_seats, event_id)
    )
    conn.commit()
    conn.close()

def delete_event(event_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()

def reserve_seat(event_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE events SET available_seats = available_seats - 1
        WHERE id = ? AND available_seats > 0
    ''', (event_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0
