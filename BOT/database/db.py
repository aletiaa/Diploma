import sqlite3

DB_NAME = "alumni.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Таблиця користувачів
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            phone_number TEXT,
            old_phone_number TEXT,
            graduation_year INTEGER,
            department_id INTEGER,
            specialty_id INTEGER,
            group_name TEXT,
            role TEXT DEFAULT 'user',  -- 'user' або 'admin'
            access_level TEXT DEFAULT 'user',  -- 'user', 'admin_limited', 'admin_super'
            birth_date TEXT,
            FOREIGN KEY (department_id) REFERENCES departments(id),
            FOREIGN KEY (specialty_id) REFERENCES specialties(id)
        )
    ''')

    # Таблиця адміністраторів
    c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            phone_number TEXT,
            role TEXT DEFAULT 'admin_limited',
            access_level TEXT DEFAULT 'admin_limited',  -- 'admin_limited', 'admin_super'
            password TEXT NOT NULL
        )
    ''')

    # Таблиця факультетів
    c.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Таблиця спеціальностей
    c.execute('''
        CREATE TABLE IF NOT EXISTS specialties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            UNIQUE(code, name)
        )
    ''')

    # Таблиця новин
    c.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_description TEXT NOT NULL,
            full_description TEXT NOT NULL,
            date TEXT NOT NULL,
            link TEXT NOT NULL
        )
    ''')

    # Таблиця подій
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            short_description TEXT NOT NULL,
            place TEXT NOT NULL,
            event_datetime TEXT NOT NULL,
            seats INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Додати факультет за замовчуванням
    c.execute('INSERT OR IGNORE INTO departments (name) VALUES (?)',
              ("Теплоенергетичний факультет",))

    # Додати спеціальності
    specialties = [
        ("121", "Інженерія програмного забезпечення"),
        ("122", "Комп’ютерні науки"),
        ("174", "Автоматизація та комп'ютерно-інтегровані технології та робототехніка"),
        ("144", "Теплоенергетика"),
        ("143", "Атомна енергетика"),
        ("142", "Енергетичне машинобудування")
    ]
    for code, name in specialties:
        c.execute('INSERT OR IGNORE INTO specialties (code, name) VALUES (?, ?)', (code, name))

    conn.commit()
    conn.close()