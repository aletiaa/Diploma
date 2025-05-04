from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from ...utils.keyboard import communication_user_menu_keyboard, user_main_menu_keyboard
from ...database.queries import get_connection

router = Router()

@router.callback_query(lambda c: c.data == "user_communication_menu")
async def open_communication_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>👥 Спілкування між випускниками</b>\n\n"
        "Оберіть тип спілкування:",
        reply_markup=communication_user_menu_keyboard,
        parse_mode="HTML"
    )

@router.callback_query(lambda c: c.data in ["chat_by_group", "chat_by_specialty", "chat_by_year"])
async def send_communication_link(callback: CallbackQuery, state: FSMContext):
    telegram_id = str(callback.from_user.id)
    chat_type = {
        "chat_by_group": "group",
        "chat_by_specialty": "specialty",
        "chat_by_year": "year"
    }[callback.data]

    conn = get_connection()
    cursor = conn.cursor()

    # Отримуємо відповідне значення з таблиці users
    cursor.execute(f'''
        SELECT { 
            "group_name" if chat_type == "group" else
            "specialty_id" if chat_type == "specialty" else
            "enrollment_year"
        }
        FROM users
        WHERE telegram_id = ?
    ''', (telegram_id,))
    result = cursor.fetchone()

    if not result or not result[0]:
        await callback.message.answer("⚠️ Неможливо знайти ваше значення для пошуку чату.")
        return

    user_value = result[0]

    # Якщо це спеціальність — отримаємо її код
    if chat_type == "specialty":
        cursor.execute("SELECT code FROM specialties WHERE id = ?", (user_value,))
        specialty_result = cursor.fetchone()
        if not specialty_result:
            await callback.message.answer("⚠️ Спеціальність не знайдено.")
            return
        user_value = specialty_result[0]

    # Шукаємо чат
    cursor.execute('''
        SELECT link FROM communication_chats
        WHERE chat_type = ? AND match_value = ?
    ''', (chat_type, str(user_value)))
    chat = cursor.fetchone()
    conn.close()

    if chat:
        await callback.message.answer(
            f"🔗 Ось посилання на чат {chat_type}:\n{chat[0]}"
        )
    else:
        await callback.message.answer("❌ Чат ще не створено адміністратором.")

# Повернення назад
@router.callback_query(lambda c: c.data == "back_to_user_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🏠 Головне меню:", reply_markup=user_main_menu_keyboard, parse_mode="HTML")
