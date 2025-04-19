from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔎 Пошук випускника")],
            [KeyboardButton(text="📰 Отримати новини")],
            [KeyboardButton(text="📅 Переглянути події")],
        ],
        resize_keyboard=True
    )

def edit_profile_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔤 Змінити ім’я"), KeyboardButton(text="📱 Змінити номер")],
            [KeyboardButton(text="🎓 Змінити групу"), KeyboardButton(text="📘 Змінити спеціальність")],
            [KeyboardButton(text="❌ Вийти")]
        ],
        resize_keyboard=True
    )

def admin_panel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 Переглянути користувачів")],
            [KeyboardButton(text="🔒 Заблокувати користувача"), KeyboardButton(text="✏️ Редагувати дані")],
            [KeyboardButton(text="📰 Опублікувати новину"), KeyboardButton(text="🗑 Видалити новину")],
            [KeyboardButton(text="📤 Надіслати матеріали")],
            [KeyboardButton(text="🔙 Назад до меню")],
        ],
        resize_keyboard=True
    )

def remove_keyboard():
    return ReplyKeyboardRemove()

def contact_request_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Надіслати мій номер", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
