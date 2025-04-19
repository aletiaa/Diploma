import sqlite3
from database.models import User

def get_user_by_telegram_id(telegram_id: str) -> User | None:
    conn = sqlite3.connect("alumni.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return User(*row)
    return None

def update_user_field(telegram_id: str, field: str, value):
    conn = sqlite3.connect("alumni.db")
    c = conn.cursor()
    c.execute(f"UPDATE users SET {field} = ? WHERE telegram_id = ?", (value, telegram_id))
    conn.commit()
    conn.close()

def get_all_specialties():
    conn = sqlite3.connect("alumni.db")
    c = conn.cursor()
    c.execute("SELECT code, name FROM specialties")
    result = c.fetchall()
    conn.close()
    return result