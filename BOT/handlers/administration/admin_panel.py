# import sqlite3
# from aiogram import Router, types
# from aiogram.filters import Command
# from aiogram.types import ReplyKeyboardRemove
# from ...utils.keyboard import admin_panel_keyboard
# from ...config import SUPER_ADMIN_ID

# router = Router()
# admin_state = {}

# @router.message(Command("admin_panel"))
# async def open_admin_panel(message: types.Message):
#     telegram_id = str(message.from_user.id)

#     conn = sqlite3.connect("alumni.db")
#     c = conn.cursor()
#     c.execute("SELECT role FROM users WHERE telegram_id = ?", (telegram_id,))
#     result = c.fetchone()
#     conn.close()

#     if not result or result[0] != "admin":
#         await message.answer("❌ У вас немає прав адміністратора.")
#         return

#     level = "super" if message.from_user.id == SUPER_ADMIN_ID else "limited"
#     admin_state[message.chat.id] = {"level": level, "step": "menu"}

#     kb = admin_panel_keyboard(super_admin=(level == "super"))
#     await message.answer(f"🔧 Панель адміністратора ({level.upper()}):", reply_markup=kb)


# @router.message(lambda m: m.text == "👥 Переглянути користувачів")
# async def view_users(message: types.Message):
#     state = admin_state.get(message.chat.id)
#     if not state or state["level"] != "super":
#         await message.answer("❌ Ця функція доступна лише SUPER адміністраторам.")
#         return

#     conn = sqlite3.connect("alumni.db")
#     c = conn.cursor()
#     c.execute("""
#         SELECT u.full_name, u.phone_number, d.name, s.name, u.role 
#         FROM users u 
#         LEFT JOIN departments d ON u.department_id = d.id 
#         LEFT JOIN specialties s ON u.specialty_id = s.id
#     """)
#     users = c.fetchall()
#     conn.close()

#     if not users:
#         await message.answer("📭 Користувачів не знайдено.")
#         return

#     response = "👥 Список користувачів:\n\n"
#     for user in users:
#         response += f"• {user[0]} | {user[1]} | {user[2]} | {user[3]} | {user[4]}\n"
#     await message.answer(response[:4000])  # обмеження для довгих списків


# @router.message(lambda m: m.text == "🔄 Змінити роль користувача")
# async def change_user_role_start(message: types.Message):
#     state = admin_state.get(message.chat.id)
#     if not state or state["level"] != "super":
#         await message.answer("❌ Лише SUPER адміністратор може змінювати ролі.")
#         return

#     state["step"] = "await_user_for_role_change"
#     await message.answer("👤 Введіть номер телефону користувача, якому хочете змінити роль:")


# @router.message(lambda m: m.text == "📰 Публікувати новину")
# async def publish_news(message: types.Message):
#     admin_state[message.chat.id]["step"] = "await_news"
#     await message.answer("📝 Надішліть текст новини:")


# @router.message(lambda m: m.text == "📅 Додати подію")
# async def add_event(message: types.Message):
#     admin_state[message.chat.id]["step"] = "await_event"
#     await message.answer("📅 Надішліть опис події:")


# @router.message(lambda m: m.text == "❌ Вийти")
# async def exit_admin_panel(message: types.Message):
#     admin_state.pop(message.chat.id, None)
#     await message.answer("🚪 Ви вийшли з панелі адміністратора.", reply_markup=ReplyKeyboardRemove())


# # Обробка новин/подій/ролей
# @router.message()
# async def handle_admin_inputs(message: types.Message):
#     chat_id = message.chat.id
#     state = admin_state.get(chat_id)

#     if not state:
#         return

#     step = state.get("step")

#     if step == "await_news":
#         conn = sqlite3.connect("alumni.db")
#         c = conn.cursor()
#         c.execute("INSERT INTO news (content) VALUES (?)", (message.text,))
#         conn.commit()
#         conn.close()
#         await message.answer("✅ Новину збережено та опубліковано.")
#         state["step"] = "menu"

#     elif step == "await_event":
#         conn = sqlite3.connect("alumni.db")
#         c = conn.cursor()
#         c.execute("INSERT INTO events (description) VALUES (?)", (message.text,))
#         conn.commit()
#         conn.close()
#         await message.answer("✅ Подію збережено.")
#         state["step"] = "menu"

#     elif step == "await_user_for_role_change":
#         phone = message.text.strip()
#         conn = sqlite3.connect("alumni.db")
#         c = conn.cursor()
#         c.execute("SELECT full_name, role FROM users WHERE phone_number = ?", (phone,))
#         user = c.fetchone()
#         if not user:
#             await message.answer("❌ Користувача не знайдено.")
#             conn.close()
#             return

#         state["target_phone"] = phone
#         state["step"] = "confirm_new_role"
#         await message.answer(f"🔄 Поточна роль {user[0]}: {user[1]}\nВведіть нову роль (user/admin):")
#         conn.close()

#     elif step == "confirm_new_role":
#         new_role = message.text.strip().lower()
#         if new_role not in ["user", "admin"]:
#             await message.answer("❗ Введіть тільки 'user' або 'admin'.")
#             return

#         phone = state.get("target_phone")
#         conn = sqlite3.connect("alumni.db")
#         c = conn.cursor()
#         c.execute("UPDATE users SET role = ? WHERE phone_number = ?", (new_role, phone))
#         conn.commit()
#         conn.close()
#         await message.answer(f"✅ Роль для користувача {phone} оновлено на: {new_role}")
#         state["step"] = "menu"
