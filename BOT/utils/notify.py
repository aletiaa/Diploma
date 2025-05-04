from aiogram import Bot, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest

from ..database.queries import get_connection

router = Router()

# Стан оголошення
class AnnouncementState(StatesGroup):
    waiting_text_or_file = State()


# Отримати всіх користувачів з певною роллю
def get_user_ids_by_filter(column: str = None, value: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    if column and value:
        cursor.execute(f"SELECT telegram_id FROM users WHERE {column} = ?", (value,))
    else:
        cursor.execute("SELECT telegram_id FROM users WHERE role = 'user'")
    user_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return user_ids


# Старт запиту на оголошення
@router.callback_query(lambda c: c.data == "send_announcement")
async def prompt_announcement(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("✉️ Введіть текст або надішліть файл (фото/документ) для оголошення:")
    await state.set_state(AnnouncementState.waiting_text_or_file)


# Обробка оголошення
@router.message(AnnouncementState.waiting_text_or_file)
async def handle_announcement_input(message: Message, state: FSMContext):
    user_ids = get_user_ids_by_filter()
    sent_count, failed = 0, []

    for user_id in user_ids:
        try:
            if message.photo:
                file_id = message.photo[-1].file_id
                await message.bot.send_photo(
                    chat_id=user_id,
                    photo=file_id,
                    caption=message.caption or "📢 Оголошення",
                    parse_mode="HTML"
                )
            elif message.video:
                file_id = message.video.file_id
                await message.bot.send_video(
                    chat_id=user_id,
                    video=file_id,
                    caption=message.caption or "📢 Оголошення",
                    parse_mode="HTML"
                )
            elif message.document:
                file_id = message.document.file_id
                await message.bot.send_document(
                    chat_id=user_id,
                    document=file_id,
                    caption=message.caption or "📢 Оголошення",
                    parse_mode="HTML"
                )
            elif message.text:
                await message.bot.send_message(
                    chat_id=user_id,
                    text=f"📢 Оголошення:\n\n{message.text}",
                    parse_mode="HTML"
                )
            else:
                continue

            sent_count += 1
        except TelegramBadRequest as e:
            print(f"Telegram error for {user_id}: {e}")
            failed.append(user_id)
        except Exception as e:
            print(f"General error for {user_id}: {e}")
            failed.append(user_id)

    await message.answer(f"✅ Оголошення надіслано {sent_count} користувачам.")
    if failed:
        await message.answer(f"Не вдалося надіслати {len(failed)} користувачам.")
    await state.clear()


# Надіслати повідомлення одному користувачу
async def send_message_to_user(bot: Bot, telegram_id: str, text: str):
    try:
        await bot.send_message(chat_id=telegram_id, text=text)
    except Exception as e:
        print(f"Не вдалося надіслати користувачу {telegram_id}: {e}")


# Надіслати повідомлення всім користувачам
async def notify_all_users(bot: Bot, message_text: str):
    user_ids = get_user_ids_by_filter()
    for user_id in user_ids:
        await send_message_to_user(bot, user_id, message_text)


# Сповіщення про створення чату
async def notify_users_about_chat(bot: Bot, chat_type: str, match_value: str, link: str):
    column_map = {
        "group": "group_name",
        "specialty": "specialty_id",
        "year": "enrollment_year"
    }

    column = column_map.get(chat_type)
    if not column:
        print(f"[⚠️] Невідомий тип чату: {chat_type}")
        return

    user_ids = get_user_ids_by_filter(column, match_value)
    text = (
        f"🔔 Створено новий чат для <b>{chat_type}</b>: <code>{match_value}</code>\n"
        f"🔗 {link}"
    )

    for user_id in user_ids:
        await send_message_to_user(bot, user_id, text)