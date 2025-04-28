# # handlers/administration/view_weekly.py
# from aiogram import Router, types
# from datetime import datetime, timedelta
# import sqlite3

# router = Router()

# async def send_weekly_summary(message: types.Message):
#     today = datetime.now()
#     next_week = today + timedelta(days=7)

#     conn = sqlite3.connect("alumni.db")
#     c = conn.cursor()

#     # Події
#     c.execute("SELECT description, location, time FROM events WHERE date(time) BETWEEN ? AND ?",
#               (today.strftime("%Y-%m-%d"), next_week.strftime("%Y-%m-%d")))
#     events = c.fetchall()

#     # Новини
#     c.execute("SELECT description, link FROM news WHERE date(date_published) BETWEEN ? AND ?",
#               (today.strftime("%Y-%m-%d"), next_week.strftime("%Y-%m-%d")))
#     news = c.fetchall()

#     conn.close()

#     response = "📅 <b>Події цього тижня:</b>\n"
#     if events:
#         for e in events:
#             response += f"🔹 {e[0]} ({e[1]}, {e[2]})\n"
#     else:
#         response += "— Немає запланованих подій.\n"

#     response += "\n📰 <b>Новини:</b>\n"
#     if news:
#         for n in news:
#             response += f"🔹 {n[0]} [<a href='{n[1]}'>Детальніше</a>]\n"
#     else:
#         response += "— Немає новин на цей тиждень."

#     await message.answer(response, disable_web_page_preview=True)
