from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.exceptions import TelegramBadRequest
from ...database.queries import get_connection
from ...utils.keyboard import admin_main_menu_keyboard, file_filter_keyboard, pagination_keyboard

router = Router()

FILES_PER_PAGE = 5

class FileViewState(StatesGroup):
    choosing_filter = State()
    viewing_files = State()


@router.callback_query(lambda c: c.data == "view_uploaded_files")
async def choose_filter(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(page=0, selected_file_type="all", user_id_filter=None)
    await callback.message.answer("🔍 Оберіть фільтр для перегляду файлів:", reply_markup=file_filter_keyboard)
    await state.set_state(FileViewState.choosing_filter)


@router.callback_query(lambda c: c.data.startswith("filter_"))
async def set_filter(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.data == "filter_by_user":
        await callback.message.answer("✏️ Введіть telegram_id користувача:")
        await state.set_state(FileViewState.viewing_files)
        await state.update_data(expect_user_id_input=True)
        return

    selected_file_type = callback.data.replace("filter_", "")
    await state.update_data(selected_file_type=selected_file_type, page=0, user_id_filter=None, expect_user_id_input=False)
    await show_file_page(callback.message, state)


@router.message(FileViewState.viewing_files)
async def receive_user_id_filter(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("expect_user_id_input"):
        return

    await state.update_data(user_id_filter=message.text.strip(), page=0, expect_user_id_input=False)
    await show_file_page(message, state)


@router.callback_query(lambda c: c.data in ["next_page", "prev_page"])
async def change_page(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    page = data.get("page", 0)

    if callback.data == "next_page":
        page += 1
    elif callback.data == "prev_page" and page > 0:
        page -= 1

    await state.update_data(page=page)
    await show_file_page(callback.message, state)


async def show_file_page(message_or_callback, state: FSMContext):
    bot = message_or_callback.bot
    chat_id = message_or_callback.chat.id if isinstance(message_or_callback, Message) else message_or_callback.from_user.id

    data = await state.get_data()
    page = data.get("page", 0)
    file_type = data.get("selected_file_type", "all")
    user_id_filter = data.get("user_id_filter")

    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT telegram_id, file_id, file_type, upload_time FROM user_files WHERE 1=1"
    params = []

    if file_type != "all":
        query += " AND file_type = ?"
        params.append(file_type)
    if user_id_filter:
        query += " AND telegram_id = ?"
        params.append(user_id_filter)

    query += " ORDER BY upload_time DESC LIMIT ? OFFSET ?"
    params += [FILES_PER_PAGE, FILES_PER_PAGE * page]

    cursor.execute(query, tuple(params))
    files = cursor.fetchall()
    conn.close()

    if not files:
        await bot.send_message(chat_id, "❗️ Файлів за заданими умовами не знайдено.")
        return

    for idx, (user_id, file_id, f_type, sent_at) in enumerate(files, start=1 + page * FILES_PER_PAGE):
        caption = f"#{idx} \ud83d\uddd3 {sent_at}\n\ud83d\udc64 <code>{user_id}</code>\n\ud83d\udce6 Тип: {f_type}"
        try:
            if f_type == "photo":
                await bot.send_photo(chat_id, file_id, caption=caption, parse_mode="HTML")
            elif f_type == "video":
                await bot.send_video(chat_id, file_id, caption=caption, parse_mode="HTML")
            elif f_type == "document":
                await bot.send_document(chat_id, file_id, caption=caption, parse_mode="HTML")
            else:
                await bot.send_message(chat_id, f"{caption}\n\ud83d\udd17 ID: {file_id}")
        except TelegramBadRequest as e:
            await bot.send_message(chat_id, f"⚠️ Не вдалося надіслати файл #{idx}: {e}")

    await bot.send_message(chat_id, "\ud83d\udd3b Сторінка керування:", reply_markup=pagination_keyboard)
