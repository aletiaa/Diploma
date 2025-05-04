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
            enrollment_year INTEGER,
            graduation_year INTEGER,
            department_id INTEGER,
            specialty_id INTEGER,
            group_name TEXT,
            role TEXT DEFAULT 'user',  -- 'user' або 'admin'
            access_level TEXT DEFAULT 'user',  -- 'user', 'admin_limited', 'admin_super'
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
    
    # Таблиця чатів для спілкування
    c.execute('''
        CREATE TABLE IF NOT EXISTS communication_chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_type TEXT NOT NULL,  -- 'group', 'enrollment_year', 'specialty'
            match_value TEXT NOT NULL,  -- Наприклад, "ТВ-12", "2020", "121"
            link TEXT NOT NULL,  -- Посилання на чат
            created_by TEXT NOT NULL,  -- telegram_id адміністратора
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_type TEXT NOT NULL,
            value TEXT NOT NULL,
            link TEXT NOT NULL,
            UNIQUE(chat_type, value)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT NOT NULL,
            file_type TEXT NOT NULL,       -- 'photo', 'video', 'document' тощо
            file_id TEXT NOT NULL,
            file_unique_id TEXT,
            caption TEXT,
            upload_time TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
        )
    ''')
    
    c.execute('''
       CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            event_datetime TEXT NOT NULL,  -- ISO-формат: YYYY-MM-DDTHH:MM:SS
            max_seats INTEGER NOT NULL,
            available_seats INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT NOT NULL,
            event_id INTEGER NOT NULL,
            registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(telegram_id, event_id)
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