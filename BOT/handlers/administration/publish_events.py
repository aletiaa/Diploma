# handlers/administration/publish_events.py
from aiogram import Router, types
import sqlite3

router = Router()
event_state = {}

async def start_event_creation(message: types.Message):
    chat_id = message.chat.id
    event_state[chat_id] = {"step": "description"}
    await message.answer("📝 Введіть короткий опис події:")

@router.message()
async def handle_event_input(message: types.Message):
    chat_id = message.chat.id
    if chat_id not in event_state:
        return

    state = event_state[chat_id]
    text = message.text.strip()

    if state["step"] == "description":
        state["description"] = text
        state["step"] = "location"
        await message.answer("📍 Введіть місце проведення:")

    elif state["step"] == "location":
        state["location"] = text
        state["step"] = "time"
        await message.answer("⏰ Введіть дату та час (формат: РРРР-ММ-ДД ГГ:ХХ):")

    elif state["step"] == "time":
        state["time"] = text
        state["step"] = "slots"
        await message.answer("👥 Введіть кількість місць для реєстрації:")

    elif state["step"] == "slots":
        if not text.isdigit():
            await message.answer("❗ Введіть число.")
            return
        state["slots"] = int(text)
        conn = sqlite3.connect("alumni.db")
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                location TEXT,
                time TEXT,
                slots INTEGER
            )
        ''')
        c.execute("INSERT INTO events (description, location, time, slots) VALUES (?, ?, ?, ?)",
                  (state["description"], state["location"], state["time"], state["slots"]))
        conn.commit()
        conn.close()
        await message.answer(f"✅ Подію додано: {state['description']}, {state['location']} ({state['time']})\n👥 Місць: {state['slots']}")
        del event_state[chat_id]
