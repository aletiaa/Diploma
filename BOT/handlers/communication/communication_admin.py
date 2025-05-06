from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import csv
from pathlib import Path

from ...utils.keyboard import communication_admin_menu_keyboard
from ...utils.notify import notify_users_about_chat

router = Router()
CHAT_CSV_PATH = Path("chat_links.csv")

class ChatCreationState(StatesGroup):
    choosing_type = State()
    entering_value = State()
    waiting_for_link = State()

@router.callback_query(lambda c: c.data == "admin_communication_menu")
async def open_admin_communication_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>Меню спілкування:</b>\nОберіть тип чату, який хочете створити або переглянути.",
        reply_markup=communication_admin_menu_keyboard,
        parse_mode="HTML"
    )

@router.callback_query(lambda c: c.data in ["create_specialty_chat", "create_year_chat"])
async def start_chat_creation(callback: CallbackQuery, state: FSMContext):
    chat_type = callback.data
    await state.update_data(chat_type=chat_type)

    prompt = {
        "create_specialty_chat": "Введіть код спеціальності (наприклад: 122):",
        "create_year_chat": "Введіть рік випуску:"
    }.get(chat_type)

    await callback.message.answer(prompt)
    await state.set_state(ChatCreationState.entering_value)

@router.message(ChatCreationState.entering_value)
async def receive_chat_value(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_type = data.get("chat_type")
    chat_value = message.text.strip()

    if not CHAT_CSV_PATH.exists():
        CHAT_CSV_PATH.write_text("year,link,specialty\n", encoding="utf-8")

    with CHAT_CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if chat_type == "create_year_chat" and row['year'] == chat_value:
                await message.answer(f"⚠️ Чат для року {chat_value} вже існує: {row['link']}")
                await state.clear()
                return
            if chat_type == "create_specialty_chat" and row['specialty'] == chat_value:
                await message.answer(f"⚠️ Чат для спеціальності {chat_value} вже існує: {row['link']}")
                await state.clear()
                return

    await state.update_data(chat_value=chat_value)
    await message.answer("🔗 Введіть посилання на новий чат:")
    await state.set_state(ChatCreationState.waiting_for_link)

@router.message(ChatCreationState.waiting_for_link)
async def save_chat_link(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_type = data.get("chat_type")
    chat_value = data.get("chat_value")
    link = message.text.strip()

    # ✅ ВАЛІДАЦІЯ ПОСИЛАННЯ
    if not (link.startswith("https://t.me/") or link.startswith("https://telegram.me/")):
        await message.answer("❌ Посилання повинно починатися з https://t.me/ або https://telegram.me/")
        return

    row = {}
    if chat_type == "create_year_chat":
        row = {"year": chat_value, "link": link, "specialty": ""}
    elif chat_type == "create_specialty_chat":
        row = {"year": "", "link": link, "specialty": chat_value}

    with CHAT_CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["year", "link", "specialty"])
        writer.writerow(row)

    await message.answer(f"✅ Посилання збережено: {link}")
    await notify_users_about_chat(
        bot=message.bot,
        chat_type=chat_type.replace("create_", "").replace("_chat", ""),
        match_value=chat_value,
        link=link
    )
    await state.clear()

@router.callback_query(lambda c: c.data == "view_all_chats")
async def view_all_chats(callback: CallbackQuery, state: FSMContext):
    if not CHAT_CSV_PATH.exists():
        await callback.message.answer("📭 Ще не збережено жодного чату.")
        return

    with CHAT_CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            description = ""
            if row["year"]:
                description += f"🎓 Рік випуску: {row['year']}\n"
            if row["specialty"]:
                description += f"🧪 Спеціальність: {row['specialty']}\n"

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔗 Перейти до чату", url=row['link'])]
            ])
            await callback.message.answer(
                f"📌 <b>Чат</b>\n{description}🔗 {row['link']}",
                parse_mode="HTML",
                reply_markup=keyboard
            )
