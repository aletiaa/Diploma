import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

from ....database.queries import get_connection

EVENTS_FILE = Path("events.json")
REGISTRATIONS_FILE = Path("registrations.json")


# --- Універсальні функції для JSON файлів ---

def load_json(file_path: Path) -> List[Dict[str, Any]]:
    if not file_path.exists():
        return []
    try:
        with file_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_json(file_path: Path, data: List[Dict[str, Any]]):
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# --- Робота з подіями ---

def load_events() -> List[Dict[str, Any]]:
    return load_json(EVENTS_FILE)

def save_events(events: List[Dict[str, Any]]):
    save_json(EVENTS_FILE, events)

def get_next_event_id(events: List[Dict[str, Any]]) -> int:
    return max((event["id"] for event in events), default=0) + 1

def find_event_by_id(events: List[Dict[str, Any]], event_id: int) -> Optional[Dict[str, Any]]:
    return next((e for e in events if e["id"] == event_id), None)

def reserve_seat(events: List[Dict[str, Any]], event_id: int) -> bool:
    event = find_event_by_id(events, event_id)
    if event and event["available_seats"] > 0:
        event["available_seats"] -= 1
        return True
    return False

def add_event(title: str, description: str, event_datetime: datetime, max_seats: int) -> Dict[str, Any]:
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

def update_event(event_id: int, **kwargs) -> bool:
    events = load_events()
    event = find_event_by_id(events, event_id)
    if not event:
        return False
    for key, value in kwargs.items():
        if key in event:
            event[key] = value
    save_events(events)
    return True

def delete_event(event_id: int) -> bool:
    events = load_events()
    events = [e for e in events if e["id"] != event_id]
    save_events(events)
    return True


# --- Реєстрації користувачів на події ---

def load_registrations() -> List[Dict[str, Any]]:
    return load_json(REGISTRATIONS_FILE)

def save_registrations(data: List[Dict[str, Any]]):
    save_json(REGISTRATIONS_FILE, data)

def register_user_to_event(event_id: int, telegram_id: str):
    registrations = load_registrations()
    registrations.append({
        "event_id": event_id,
        "telegram_id": str(telegram_id),
        "timestamp": datetime.now().isoformat()
    })
    save_registrations(registrations)

    # Оновлення available_seats
    events = load_events()
    if reserve_seat(events, event_id):
        save_events(events)


# --- Синхронізація з БД ---

def sync_json_to_db():
    events = load_events()
    conn = get_connection()
    cursor = conn.cursor()
    for e in events:
        cursor.execute("""
            INSERT OR REPLACE INTO events (id, title, description, event_datetime, max_seats, available_seats)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (e['id'], e['title'], e['description'], e['datetime'], e['max_seats'], e['available_seats']))
    conn.commit()
    conn.close()

def sync_db_to_json():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, event_datetime, max_seats, available_seats FROM events")
    rows = cursor.fetchall()
    conn.close()

    events = [{
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "datetime": row[3],
        "max_seats": row[4],
        "available_seats": row[5]
    } for row in rows]

    save_events(events)
