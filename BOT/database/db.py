import sqlite3

def init_db():
    conn = sqlite3.connect("alumni.db")
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            phone_number TEXT,
            graduation_year INTEGER,
            department_id INTEGER,
            specialty_id INTEGER,
            group_name TEXT,
            role TEXT DEFAULT 'user',
            FOREIGN KEY (department_id) REFERENCES departments(id),
            FOREIGN KEY (specialty_id) REFERENCES specialties(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS specialties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            UNIQUE(code, name)
        )
    ''')

    # Додати факультет
    c.execute('INSERT OR IGNORE INTO departments (name) VALUES (?)',
              ("Теплоенергетичний факультет",))

    specialties = [
        ("121", "Інженерія програмного забезпечення"),
        ("122", "Комп’ютерні науки"),
        ("174", "Автоматизація та комп'ютерно-інтегровані технології та робототехника"),
        ("144", "Теплоенергетика"),
        ("143", "Атомна енергетика"),
        ("142", "Енергетичне машинобудування")
    ]
    for code, name in specialties:
        c.execute('INSERT OR IGNORE INTO specialties (code, name) VALUES (?, ?)', (code, name))

    conn.commit()
    conn.close()
