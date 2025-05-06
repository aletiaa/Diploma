from aiogram import Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from ics import Calendar, Event as IcsEvent
from io import BytesIO
from ...database.queries import get_connection, get_all_events, get_event_by_id, reserve_seat
from ...utils.keyboard import user_main_menu_keyboard

router = Router()

class UploadPhotoStates(StatesGroup):
    waiting_photo = State()
    confirming_more = State()

class UploadVideoStates(StatesGroup):
    waiting_video = State()
    confirming_more = State()

class UploadDocumentStates(StatesGroup):
    waiting_document = State()
    confirming_more = State()

confirm_more_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Так, ще файл", callback_data="upload_yes"),
            InlineKeyboardButton(text="Завершити", callback_data="upload_no")
        ]
    ]
)

@router.callback_query(lambda c: c.data == "upload_photo")
async def start_upload(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📸 Надішліть фотографію:")
    await state.set_state(UploadPhotoStates.waiting_photo)

@router.message(UploadPhotoStates.waiting_photo)
async def receive_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("❗ Надішліть саме фотографію.")
        return

    file_id = message.photo[-1].file_id
    telegram_id = str(message.from_user.id)
    timestamp = datetime.now().isoformat()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_files (telegram_id, file_id, file_type, upload_time) VALUES (?, ?, ?, ?)",
        (telegram_id, file_id, "photo", timestamp)
    )
    conn.commit()
    conn.close()

    await message.answer("✅ Фото збережено. Бажаєте надіслати ще?", reply_markup=confirm_more_keyboard)
    await state.set_state(UploadPhotoStates.confirming_more)

@router.callback_query(lambda c: c.data == "upload_video")
async def start_video_upload(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🎬 Надішліть відео:")
    await state.set_state(UploadVideoStates.waiting_video)

@router.message(UploadVideoStates.waiting_video)
async def receive_video(message: Message, state: FSMContext):
    if not message.video:
        await message.answer("❗ Надішліть саме відео.")
        return

    file_id = message.video.file_id
    telegram_id = str(message.from_user.id)
    timestamp = datetime.now().isoformat()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_files (telegram_id, file_id, file_type, upload_time) VALUES (?, ?, ?, ?)",
        (telegram_id, file_id, "video", timestamp)
    )
    conn.commit()
    conn.close()

    await message.answer("✅ Відео збережено. Бажаєте надіслати ще?", reply_markup=confirm_more_keyboard)
    await state.set_state(UploadVideoStates.confirming_more)

@router.callback_query(lambda c: c.data == "upload_document")
async def start_document_upload(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📎 Надішліть документ:")
    await state.set_state(UploadDocumentStates.waiting_document)

@router.message(UploadDocumentStates.waiting_document)
async def receive_document(message: Message, state: FSMContext):
    if not message.document:
        await message.answer("❗ Надішліть саме документ.")
        return

    file_id = message.document.file_id
    telegram_id = str(message.from_user.id)
    timestamp = datetime.now().isoformat()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_files (telegram_id, file_id, file_type, upload_time) VALUES (?, ?, ?, ?)",
        (telegram_id, file_id, "document", timestamp)
    )
    conn.commit()
    conn.close()

    await message.answer("✅ Документ збережено. Бажаєте надіслати ще?", reply_markup=confirm_more_keyboard)
    await state.set_state(UploadDocumentStates.confirming_more)

@router.callback_query(lambda c: c.data in ["upload_yes", "upload_no"])
async def handle_upload_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    current_state = await state.get_state()

    if current_state == UploadPhotoStates.confirming_more.state:
        if callback.data == "upload_yes":
            await callback.message.answer("📸 Надішліть ще одне фото:")
            await state.set_state(UploadPhotoStates.waiting_photo)
        else:
            await callback.message.answer("✅ Дякуємо! Повертаємося до головного меню.", reply_markup=user_main_menu_keyboard)
            await state.clear()

    elif current_state == UploadVideoStates.confirming_more.state:
        if callback.data == "upload_yes":
            await callback.message.answer("🎬 Надішліть ще одне відео:")
            await state.set_state(UploadVideoStates.waiting_video)
        else:
            await callback.message.answer("✅ Дякуємо! Повертаємося до головного меню.", reply_markup=user_main_menu_keyboard)
            await state.clear()

    elif current_state == UploadDocumentStates.confirming_more.state:
        if callback.data == "upload_yes":
            await callback.message.answer("📎 Надішліть ще один документ:")
            await state.set_state(UploadDocumentStates.waiting_document)
        else:
            await callback.message.answer("✅ Дякуємо! Повертаємося до головного меню.", reply_markup=user_main_menu_keyboard)
            await state.clear()

@router.callback_query(lambda c: c.data == "view_my_files")
async def view_my_files(callback: CallbackQuery):
    telegram_id = str(callback.from_user.id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_type, file_id, upload_time FROM user_files WHERE telegram_id = ? ORDER BY upload_time DESC LIMIT 10", (telegram_id,))
    files = cursor.fetchall()
    conn.close()

    if not files:
        await callback.message.answer("📂 Ви ще не надсилали файлів.")
        return

    for idx, (file_type, file_id, upload_time) in enumerate(files, 1):
        caption = f"#{idx} | Тип: {file_type}\n📅 {upload_time}"
        if file_type == "photo":
            await callback.message.bot.send_photo(chat_id=telegram_id, photo=file_id, caption=caption)
        elif file_type == "video":
            await callback.message.bot.send_video(chat_id=telegram_id, video=file_id, caption=caption)
        elif file_type == "document":
            await callback.message.bot.send_document(chat_id=telegram_id, document=file_id, caption=caption)

    await callback.message.answer("⬅️ Повертаємось до меню", reply_markup=user_main_menu_keyboard)

