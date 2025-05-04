from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ...utils.keyboard import communication_admin_menu_keyboard
from ...utils.notify import notify_users_about_chat
from ...database.queries import get_connection

router = Router()


class ChatCreationState(StatesGroup):
    choosing_type = State()
    entering_value = State()


@router.callback_query(lambda c: c.data == "admin_communication_menu")
async def open_admin_communication_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>Меню спілкування:</b>\nОберіть тип чату, який хочете створити або переглянути.",
        reply_markup=communication_admin_menu_keyboard,
        parse_mode="HTML"
    )


@router.callback_query(lambda c: c.data in ["create_group_chat", "create_specialty_chat", "create_year_chat"])
async def start_chat_creation(callback: CallbackQuery, state: FSMContext):
    chat_type = callback.data
    await state.update_data(chat_type=chat_type)

    prompt = {
        "create_group_chat": "Введіть назву групи (наприклад: ТВ-12):",
        "create_specialty_chat": "Введіть код спеціальності (наприклад: 122):",
        "create_year_chat": "Введіть рік вступу:"
    }.get(chat_type)

    await callback.message.answer(prompt)
    await state.set_state(ChatCreationState.entering_value)


@router.message(ChatCreationState.entering_value)
async def receive_chat_value(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_type = data.get("chat_type")
    chat_value = message.text.strip()

    conn = get_connection()
    cursor = conn.cursor()

    if chat_type == "create_group_chat":
        chat_key = ("group", chat_value.upper())
    elif chat_type == "create_specialty_chat":
        chat_key = ("specialty", chat_value)
    elif chat_type == "create_year_chat":
        chat_key = ("enrollment_year", chat_value)
    else:
        await message.answer("❌ Невідомий тип чату.")
        return

    cursor.execute(
        "SELECT id FROM communication_chats WHERE chat_type = ? AND match_value = ?",
        (chat_key[0], chat_key[1])
    )
    exists = cursor.fetchone()

    if exists:
        await message.answer("⚠️ Такий чат вже існує.")
    else:
        fake_link = f"https://t.me/joinchat/{chat_key[0]}_{chat_key[1]}_link"

        cursor.execute('''
            INSERT INTO communication_chats (chat_type, match_value, link, created_by)
            VALUES (?, ?, ?, ?)
        ''', (chat_key[0], chat_key[1], fake_link, str(message.from_user.id)))
        conn.commit()

        await message.answer(f"✅ Чат створено для {chat_key[0]} = {chat_key[1]}")
        await notify_users_about_chat(
            bot=message.bot,
            chat_type=chat_key[0],
            match_value=chat_key[1],
            link=fake_link
        )

    conn.close()
    await state.clear()


@router.callback_query(lambda c: c.data == "view_all_chats")
async def view_all_chats(callback: CallbackQuery, state: FSMContext):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, chat_type, match_value, link FROM communication_chats ORDER BY created_at DESC")
    chats = cursor.fetchall()

    if not chats:
        await callback.message.answer("ℹ️ Жодного чату ще не створено.")
        return

    for chat_id, chat_type, value, link in chats:
        if chat_type == "group":
            cursor.execute("SELECT COUNT(*) FROM users WHERE group_name = ?", (value,))
        elif chat_type == "enrollment_year":
            cursor.execute("SELECT COUNT(*) FROM users WHERE enrollment_year = ?", (value,))
        elif chat_type == "specialty":
            cursor.execute("SELECT COUNT(*) FROM users WHERE specialty_id = ?", (value,))
        else:
            user_count = "?"
            continue
        user_count = cursor.fetchone()[0]

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Перейти до чату", url=link)]
        ])

        await callback.message.answer(
            f"📌 <b>Чат:</b> {chat_type} = {value}\n"
            f"👥 Учасників: <b>{user_count}</b>",
            parse_mode="HTML",
            reply_markup=keyboard
        )

    conn.close()
