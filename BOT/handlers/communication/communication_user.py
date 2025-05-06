from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from ...utils.keyboard import communication_user_menu_keyboard, user_main_menu_keyboard
from ...database.queries import get_connection
from pathlib import Path
import csv

router = Router()
CHAT_CSV_PATH = Path("chat_links.csv")

@router.callback_query(lambda c: c.data == "user_communication_menu")
async def open_communication_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>👥 Спілкування між випускниками</b>\n\n"
        "Оберіть тип спілкування:",
        reply_markup=communication_user_menu_keyboard,
        parse_mode="HTML"
    )
    

@router.callback_query(lambda c: c.data == "chat_by_group")
async def send_group_chat_link(callback: CallbackQuery, state: FSMContext):
    telegram_id = str(callback.from_user.id)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT group_name FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        await callback.message.answer("❌ Не вдалося отримати вашу групу.")
        return

    group_name = result[0]

    # Пошук у CSV
    if not CHAT_CSV_PATH.exists():
        await callback.message.answer("📭 Жодного чату ще не створено.")
        return

    with CHAT_CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["group"] == group_name:
                await callback.message.answer(f"🔗 Ось ваше посилання на чат:\n{row['link']}")
                return

    await callback.message.answer("❌ Чат для вашої групи ще не створено адміністратором.")


@router.callback_query(lambda c: c.data in ["chat_by_specialty", "chat_by_enrollment", "chat_by_graduation"])
async def send_communication_link(callback: CallbackQuery, state: FSMContext):
    telegram_id = str(callback.from_user.id)

    conn = get_connection()
    cursor = conn.cursor()

    if callback.data == "chat_by_specialty":
        cursor.execute("SELECT specialty_id FROM users WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone()
        if not result:
            await callback.message.answer("❌ Не вдалося отримати вашу спеціальність.")
            return
        specialty_id = result[0]
        cursor.execute("SELECT code FROM specialties WHERE id = ?", (specialty_id,))
        code_result = cursor.fetchone()
        if not code_result:
            await callback.message.answer("❌ Не вдалося знайти код спеціальності.")
            return
        user_value = code_result[0]
        chat_type = "specialty"
    elif callback.data == "chat_by_enrollment":
        cursor.execute("SELECT enrollment_year FROM users WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone()
        if not result:
            await callback.message.answer("❌ Не вдалося отримати рік вступу.")
            return
        user_value = str(result[0])
        chat_type = "enrollment_year"
    elif callback.data == "chat_by_graduation":
        cursor.execute("SELECT graduation_year FROM users WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone()
        if not result:
            await callback.message.answer("❌ Не вдалося отримати рік випуску.")
            return
        user_value = str(result[0])
        chat_type = "graduation_year"
    else:
        await callback.message.answer("❌ Невідомий тип чату.")
        conn.close()
        return

    conn.close()

    if not CHAT_CSV_PATH.exists():
        await callback.message.answer("📭 Жодного чату ще не створено.")
        return

    with CHAT_CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get(chat_type) == user_value:
                await callback.message.answer(f"🔗 Ось ваше посилання на чат:\n{row['link']}")
                return

    await callback.message.answer("❌ Чат ще не створено адміністратором.")
