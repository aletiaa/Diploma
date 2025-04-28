from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton, 
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

# Персональне головне меню після входу
user_main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редагувати профіль", callback_data="edit_profile")],
    ]
)

# Кнопка для поділитись номером телефону
request_phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Поділитися номером телефону", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Головне меню користувача та адміністратора
main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Реєстрація користувача", callback_data="register_user")],
        [InlineKeyboardButton(text="Реєстрація адміністратора", callback_data="register_admin")],
        [InlineKeyboardButton(text="Вхід користувача", callback_data="login_user")],
        [InlineKeyboardButton(text="Вхід адміністратора", callback_data="login_admin")],
        [InlineKeyboardButton(text="Допомога", callback_data="help_info")]
    ]
)

edit_profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Змінити ПІБ", callback_data="edit_full_name")],
        [InlineKeyboardButton(text="📱 Змінити номер телефону", callback_data="edit_phone_number")],
        [InlineKeyboardButton(text="🎓 Змінити групу", callback_data="edit_group_name")],
        [InlineKeyboardButton(text="📘 Змінити спеціальність", callback_data="edit_specialty")],
        [InlineKeyboardButton(text="📅 Змінити рік випуску", callback_data="edit_graduation_year")],
        [InlineKeyboardButton(text="🗓️ Змінити дату народження", callback_data="edit_birth_date")],
        [InlineKeyboardButton(text="⬅️ Назад до головного меню", callback_data="back_to_user_menu")]
    ]
)

# --- Головне меню адміністратора з новинами --- #
admin_main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редагувати профіль", callback_data="edit_admin")],
        [InlineKeyboardButton(text="📰 Робота з новинами", callback_data="news_menu")],
        [InlineKeyboardButton(text="👥 Переглянути користувачів", callback_data="view_users")],
        [InlineKeyboardButton(text="❌ Видалити користувача", callback_data="delete_user")],
        [InlineKeyboardButton(text="🚫 Заблокувати користувача", callback_data="block_user")],
        [InlineKeyboardButton(text="🔐 Змінити доступ користувача", callback_data="change_access")]
    ]
)

# --- Меню роботи з новинами --- #
news_admin_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати новину", callback_data="add_news")],
        [InlineKeyboardButton(text="✏️ Редагувати новину", callback_data="edit_news")],
        [InlineKeyboardButton(text="❌ Видалити новину", callback_data="delete_news")],
        [InlineKeyboardButton(text="🔍 Переглянути новину", callback_data="view_news")],
        [InlineKeyboardButton(text="📋 Всі новини", callback_data="list_news")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin_menu")]
    ]
)

# Меню редагування профілю адміністратора
edit_admin_profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Змінити ПІБ", callback_data="edit_admin_full_name")],
        [InlineKeyboardButton(text="📱 Змінити номер телефону", callback_data="edit_admin_phone_number")],
        [InlineKeyboardButton(text="🔐 Змінити пароль", callback_data="edit_admin_password")],
        [InlineKeyboardButton(text="⬅️ Назад до головного меню", callback_data="back_to_admin_menu")]
    ]
)

view_users_sort_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🎓 За групою", callback_data="view_users_group")],
        [InlineKeyboardButton(text="📅 За роком випуску", callback_data="view_users_year")],
        [InlineKeyboardButton(text="📘 За спеціальністю", callback_data="view_users_specialty")],
        [InlineKeyboardButton(text="⬅️ Назад до адмін-панелі", callback_data="back_to_admin_menu")]
    ]
)