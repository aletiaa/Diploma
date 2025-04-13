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

def remove_keyboard():
    return ReplyKeyboardRemove()