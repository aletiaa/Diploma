from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import csv
from pathlib import Path

from ...utils.keyboard import communication_admin_menu_keyboard, filter_chats_keyboard
from ...utils.notify import notify_users_about_chat

router = Router()
CHAT_CSV_PATH = Path("BOT/handlers/communication/chat_links.csv")

class ChatCreationState(StatesGroup):
    entering_group = State()
    entering_specialty = State()
    entering_enrollment_year = State()
    entering_graduation_year = State()
    waiting_for_link = State()

class ChatFilterState(StatesGroup):
    waiting_filter_value = State()

@router.callback_query(lambda c: c.data == "admin_communication_menu")
async def open_admin_communication_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "<b>Меню спілкування:</b>\nОберіть дію нижче.",
        reply_markup=communication_admin_menu_keyboard,
        parse_mode="HTML"
    )

@router.callback_query(lambda c: c.data == "create_new_chat")
async def start_chat_creation(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("✏️ Введіть назву групи (наприклад: ТВ-13):")
    await state.set_state(ChatCreationState.entering_group)

@router.message(ChatCreationState.entering_group)
async def get_group(message: Message, state: FSMContext):
    await state.update_data(group=message.text.strip())
    await message.answer("🔢 Введіть код спеціальності:")
    await state.set_state(ChatCreationState.entering_specialty)

@router.message(ChatCreationState.entering_specialty)
async def get_specialty(message: Message, state: FSMContext):
    await state.update_data(specialty=message.text.strip())
    await message.answer("📅 Введіть рік вступу:")
    await state.set_state(ChatCreationState.entering_enrollment_year)

@router.message(ChatCreationState.entering_enrollment_year)
async def get_enrollment_year(message: Message, state: FSMContext):
    await state.update_data(enrollment_year=message.text.strip())
    await message.answer("📅 Введіть рік випуску:")
    await state.set_state(ChatCreationState.entering_graduation_year)

@router.message(ChatCreationState.entering_graduation_year)
async def get_graduation_year(message: Message, state: FSMContext):
    await state.update_data(graduation_year=message.text.strip())
    await message.answer("🔗 Введіть поилання на чат:")
    await state.set_state(ChatCreationState.waiting_for_link)

@router.message(ChatCreationState.waiting_for_link)
async def save_chat_link(message: Message, state: FSMContext):
    data = await state.get_data()
    link = message.text.strip()

    if not (link.startswith("https://t.me/") or link.startswith("https://telegram.me/")):
        await message.answer("❌ Посилання повинно починатися з https://t.me/ або https://telegram.me/")
        return

    new_row = {
        "group": data["group"],
        "specialty": data["specialty"],
        "enrollment_year": data["enrollment_year"],
        "graduation_year": data["graduation_year"],
        "link": link
    }

    rows = []
    updated = False

    if CHAT_CSV_PATH.exists():
        with CHAT_CSV_PATH.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

    for row in rows:
        if (
            row["group"] == new_row["group"] and
            row["specialty"] == new_row["specialty"] and
            row["enrollment_year"] == new_row["enrollment_year"] and
            row["graduation_year"] == new_row["graduation_year"]
        ):
            row["link"] = link
            updated = True
            break

    if not updated:
        rows.append(new_row)

    with CHAT_CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["group", "specialty", "enrollment_year", "graduation_year", "link"])
        writer.writeheader()
        writer.writerows(rows)

    await message.answer(f"✅ Посилання {'оновлено' if updated else 'збережено'}: {link}")

    await notify_users_about_chat(
        bot=message.bot,
        chat_type="group",
        match_value=f"{data['group']} | {data['specialty']} | {data['enrollment_year']}-{data['graduation_year']}",
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
            description = (
                f"👥 Група: {row['group']}\n"
                f"🧪 Спеціальність: {row['specialty']}\n"
                f"📅 {row['enrollment_year']} – {row['graduation_year']}\n"
        )
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔗 Перейти до чату", url=row['link'])]
            ])
            await callback.message.answer(
                f"📌 <b>Чат</b>\n{description}🔗 {row['link']}",
                parse_mode="HTML",
                reply_markup=keyboard
            )

@router.callback_query(lambda c: c.data == "communication_filter_chats")
async def show_filter_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🔍 Оберіть критерій для фільтрації чатів:", reply_markup=filter_chats_keyboard)

@router.callback_query(lambda c: c.data.startswith("communication_filter_"))
async def start_filtering(callback: CallbackQuery, state: FSMContext):
    filter_type = callback.data.replace("communication_filter_", "")
    await state.update_data(filter_type=filter_type)
    prompt = {
        "group": "Введіть назву групи:",
        "specialty": "Введіть код спеціальності:",
        "enrollment_year": "Введіть рік вступу:",
        "graduation_year": "Введіть рік випуску:"
    }[filter_type]
    await callback.message.answer(prompt)
    await state.set_state(ChatFilterState.waiting_filter_value)

@router.message(ChatFilterState.waiting_filter_value)
async def apply_filter(message: Message, state: FSMContext):
    data = await state.get_data()
    filter_type = data["filter_type"]
    value = message.text.strip()

    if not CHAT_CSV_PATH.exists():
        await message.answer("📭 Файл з чатами не знайдено.")
        await state.clear()
        return

    found = False
    with CHAT_CSV_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row[filter_type] == value:
                found = True
                description = (
                    f"👥 Група: {row['group']}\n"
                    f"🧪 Спеціальність: {row['specialty']}\n"
                    f"📅 {row['enrollment_year']} – {row['graduation_year']}\n"
                )
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔗 Перейти до чату", url=row['link'])]
                ])
                await message.answer(
                    f"📌 <b>Знайдено чат:</b>\n{description}🔗 {row['link']}",parse_mode = "HTML",reply_markup=keyboard
                )

    if not found:
        await message.answer("❌ Жодного чату за вказаним критерієм не знайдено.")

    await state.clear()