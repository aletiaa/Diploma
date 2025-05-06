import sqlite3

from .default import populate_defaults

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
            enrollment_year INTEGER,
            graduation_year INTEGER,
            department_id INTEGER,
            specialty_id INTEGER,
            group_name TEXT,
            role TEXT DEFAULT 'user',
            access_level TEXT DEFAULT 'user',
            birth_date TEXT,
            failed_attempts INTEGER DEFAULT 0,
            last_failed_login_time TEXT,
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
            access_level TEXT DEFAULT 'admin_limited',
            password TEXT NOT NULL,
            is_super INTEGER DEFAULT 0
        )
    ''')

    # Таблиця запитів на адмінство
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT UNIQUE,
            full_name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            password TEXT NOT NULL,
            requested_at TEXT DEFAULT CURRENT_TIMESTAMP
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

    # Таблиця чатів для спілкування
    c.execute('''
        CREATE TABLE IF NOT EXISTS communication_chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_type TEXT NOT NULL,
            match_value TEXT NOT NULL,
            link TEXT NOT NULL,
            created_by TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблиця чатів з унікальними значеннями
    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_type TEXT NOT NULL,
            value TEXT NOT NULL,
            link TEXT NOT NULL,
            UNIQUE(chat_type, value)
        )
    ''')

    # Таблиця файлів
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_id TEXT NOT NULL,
            file_unique_id TEXT,
            caption TEXT,
            upload_time TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
        )
    ''')

    # Таблиця подій
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            event_datetime TEXT NOT NULL,
            max_seats INTEGER NOT NULL,
            available_seats INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблиця реєстрацій на події
    c.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT NOT NULL,
            event_id INTEGER NOT NULL,
            registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(telegram_id, event_id)
        )
    ''')

    # Додавання факультету за замовчуванням
    c.execute('INSERT OR IGNORE INTO departments (name) VALUES (?)',
              ("Теплоенергетичний факультет",))

    # Додавання спеціальностей
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

    # Додавання супер-адміністратора
    SUPER_ADMIN_ID = "511884422"
    SUPER_ADMIN_NAME = "Аліна Сейкаускайте"
    SUPER_ADMIN_PHONE = "+447706698818"
    SUPER_ADMIN_PASSWORD = "05122004"

    c.execute("SELECT 1 FROM admins WHERE telegram_id = ?", (SUPER_ADMIN_ID,))
    if not c.fetchone():
        c.execute('''
            INSERT INTO admins (telegram_id, full_name, phone_number, role, access_level, password)
            VALUES (?, ?, ?, 'admin_super', 'admin_super', ?)
        ''', (SUPER_ADMIN_ID, SUPER_ADMIN_NAME, SUPER_ADMIN_PHONE, SUPER_ADMIN_PASSWORD))

    conn.commit()
    conn.close()

init_db()
populate_defaults()