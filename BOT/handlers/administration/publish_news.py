# from aiogram import Router, types
# from datetime import datetime
# import sqlite3

# router = Router()
# news_state = {}

# async def start_news_creation(message: types.Message):
#     chat_id = message.chat.id
#     news_state[chat_id] = {"step": "description"}
#     await message.answer("📝 Введіть короткий опис новини:")

# @router.message()
# async def handle_news_input(message: types.Message):
#     chat_id = message.chat.id
#     if chat_id not in news_state:
#         return

#     state = news_state[chat_id]
#     text = message.text.strip()

#     if state["step"] == "description":
#         state["description"] = text
#         state["step"] = "link"
#         await message.answer("🔗 Введіть посилання на повну новину:")

#     elif state["step"] == "link":
#         state["link"] = text
#         date_published = datetime.now().strftime("%Y-%m-%d")
#         conn = sqlite3.connect("alumni.db")
#         c = conn.cursor()
#         c.execute('''
#             CREATE TABLE IF NOT EXISTS news (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 description TEXT,
#                 link TEXT,
#                 date_published TEXT
#             )
#         ''')
#         c.execute("INSERT INTO news (description, link, date_published) VALUES (?, ?, ?)",
#                   (state["description"], state["link"], date_published))
#         conn.commit()
#         conn.close()
#         await message.answer(f"✅ Новину додано: {state['description']} ({date_published})\n🔗 {state['link']}")
#         del news_state[chat_id]
