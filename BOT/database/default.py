import random
from datetime import datetime
from .queries import get_connection

def populate_defaults():
    with get_connection() as conn:
        cursor = conn.cursor()

        # Додавання користувачів, якщо таблиця порожня
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            sample_users = [
                ("Андрій Коваль", "ТВ-21"),
                ("Олена Петренко", "ТВ-21"),
                ("Марія Шевченко", "ТФ-22"),
                ("Іван Іванов", "ТА-22"),
                ("Світлана Бондар", "НІ-23"),
                ("Олексій Соловей", "НІ-24"),
                ("Ірина Ткаченко", "ТР-24"),
                ("Микола Романенко", "ТР-25"),
                ("Ольга Зінченко", "ТА-25"),
                ("Юрій Литвин", "ТА-26"),
            ]

            specialty_ids = [1, 2, 3, 4, 5, 6]

            for i, (name, group) in enumerate(sample_users):
                telegram_id = str(100000 + i)
                phone = f"+38050{random.randint(1000000, 9999999)}"
                old_phone = phone if i % 2 == 0 else f"+38067{random.randint(1000000, 9999999)}"
                enrollment_year = 2020 + (i % 4)
                graduation_year = enrollment_year + 4
                specialty_id = specialty_ids[i % len(specialty_ids)]
                birth_date = f"0{(i % 9) + 1}.0{(i % 9) + 1}.200{i % 5}"

                cursor.execute('''
                    INSERT INTO users (
                        telegram_id, full_name, phone_number, old_phone_number,
                        enrollment_year, graduation_year, department_id, specialty_id,
                        group_name, role, access_level, birth_date,
                        failed_attempts, last_failed_login_time
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    telegram_id, name, phone, old_phone,
                    enrollment_year, graduation_year, 1, specialty_id,
                    group, 'user', 'user', birth_date,
                    0, None
                ))

        # Додавання новин, якщо таблиця порожня
        cursor.execute("SELECT COUNT(*) FROM news")
        if cursor.fetchone()[0] == 0:
            today = datetime.now().strftime("%Y-%m-%d")
            for i in range(1, 6):
                cursor.execute('''
                    INSERT INTO news (short_description, full_description, date, link)
                    VALUES (?, ?, ?, ?)
                ''', (
                    f"Новина {i}",
                    f"Повний опис новини {i}. Це приклад тексту для демонстрації.",
                    today,
                    f"https://example.com/news/{i}"
                ))

        # Додавання подій, якщо таблиця порожня
        cursor.execute("SELECT COUNT(*) FROM events")
        if cursor.fetchone()[0] == 0:
            events = [
                (1, "Навчання", "Аліна навчається", "2024-05-05T17:16:00", 12),
                (3, "Презентація проєкту", "Доповідь студентів про свої дипломні роботи.", "2025-05-10T14:00:00", 20),
                (4, "Воркшоп з Python", "Практичне заняття з програмування на Python.", "2025-05-12T11:30:00", 18),
                (5, "Кіноперегляд", "Перегляд фільму у студентському клубі.", "2025-05-14T19:00:00", 45),
                (6, "Майстер-клас з CV", "Як підготувати ефективне резюме для IT-компаній.", "2025-05-17T16:00:00", 25),
                (7, "Технічна конференція", "Виступи експертів з енергетики та технологій.", "2025-05-18T10:00:00", 50),
                (8, "Тренінг з публічних виступів", "Покращення навичок презентації та комунікації.", "2025-05-20T15:00:00", 30),
                (9, "Зустріч випускників", "Неформальна зустріч випускників кафедри.", "2025-05-22T18:30:00", 40),
                (10, "Спортивний турнір", "Змагання між студентськими командами.", "2025-05-25T09:00:00", 36),
                (11, "Кавова зустріч з деканом", "Відкрите обговорення питань навчання та ініціатив.", "2025-05-27T12:00:00", 12),
                (12, "Навчання з кібербезпеки", "Основи захисту даних та цифрової гігієни.", "2025-06-02T13:30:00", 22),
            ]

            for event in events:
                cursor.execute('''
                    INSERT INTO events (id, title, description, event_datetime, max_seats, available_seats)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (*event, event[4]))

        conn.commit()
