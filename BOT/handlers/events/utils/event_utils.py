import json
from datetime import datetime
from pathlib import Path

EVENTS_FILE = Path("events.json")

# Завантаження подій з файлу

def load_events():
    if not EVENTS_FILE.exists():
        return []
    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Збереження подій у файл

def save_events(events):
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

# Отримання наступного ID (max + 1)

def get_next_event_id(events):
    if not events:
        return 1
    return max(event["id"] for event in events) + 1

# Пошук події за ID

def find_event_by_id(events, event_id):
    return next((e for e in events if e["id"] == event_id), None)

# Оновлення доступних місць (на 1 менше при реєстрації)

def reserve_seat(events, event_id):
    event = find_event_by_id(events, event_id)
    if event and event["available_seats"] > 0:
        event["available_seats"] -= 1
        return True
    return False

# Додавання нової події

def add_event(title, description, event_datetime, max_seats):
    events = load_events()
    new_event = {
        "id": get_next_event_id(events),
        "title": title,
        "description": description,
        "datetime": event_datetime.isoformat(),
        "max_seats": max_seats,
        "available_seats": max_seats
    }
    events.append(new_event)
    save_events(events)
    return new_event

# Оновлення події за ID

def update_event(event_id, **kwargs):
    events = load_events()
    event = find_event_by_id(events, event_id)
    if not event:
        return False
    for key, value in kwargs.items():
        if key in event:
            event[key] = value
    save_events(events)
    return True

# Видалення події

def delete_event(event_id):
    events = load_events()
    events = [e for e in events if e["id"] != event_id]
    save_events(events)
    return True
