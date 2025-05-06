from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

# --- ГОЛОВНЕ МЕНЮ КОРИСТУВАЧА --- #
user_main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Редагувати профіль", callback_data="edit_profile")],
        [InlineKeyboardButton(text="Новини", callback_data="view_news_menu")],
        [InlineKeyboardButton(text="Спілкування", callback_data="user_communication_menu")],
        [InlineKeyboardButton(text="Надіслати фото", callback_data="upload_photo")],
        [InlineKeyboardButton(text="Надіслати відео", callback_data="upload_video")], 
        [InlineKeyboardButton(text="Переглянути файли", callback_data="view_my_files")],
        [InlineKeyboardButton(text="Переглянути події", callback_data="view_events")]
    ]
)

# --- КНОПКА ПОДІЛИТИСЬ НОМЕРОМ --- #
request_phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Поділитися номером телефону", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# --- ГОЛОВНЕ МЕНЮ СИСТЕМИ --- #
main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Реєстрація користувача", callback_data="register_user")],
        [InlineKeyboardButton(text="Реєстрація адміністратора", callback_data="register_admin")],
        [InlineKeyboardButton(text="Вхід користувача", callback_data="login_user")],
        [InlineKeyboardButton(text="Вхід адміністратора", callback_data="login_admin")],
        [InlineKeyboardButton(text="Допомога", callback_data="help_info")]
    ]
)

# --- РЕДАГУВАННЯ ПРОФІЛЮ КОРИСТУВАЧА --- #
edit_profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Змінити ПІБ", callback_data="edit_full_name")],
        [InlineKeyboardButton(text="Змінити номер телефону", callback_data="edit_phone_number")],
        [InlineKeyboardButton(text="Змінити групу", callback_data="edit_group_name")],
        [InlineKeyboardButton(text="Змінити спеціальність", callback_data="edit_specialty")],
        [InlineKeyboardButton(text="Змінити рік вступу", callback_data="edit_enrollment_year")],
        [InlineKeyboardButton(text="Змінити рік випуску", callback_data="edit_graduation_year")],
        [InlineKeyboardButton(text="Змінити дату народження", callback_data="edit_birth_date")],
        [InlineKeyboardButton(text="⬅️ Назад до головного меню", callback_data="back_to_user_menu")]
    ]
)

# --- АДМІН-ПАНЕЛЬ --- #
admin_main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Редагувати профіль", callback_data="admin_data_edit")],
        [InlineKeyboardButton(text="Робота з новинами", callback_data="news_menu")],
        [InlineKeyboardButton(text="Робота з користувачами", callback_data="user_management_menu")],
        [InlineKeyboardButton(text="Переглянути файли", callback_data="view_uploaded_files")],
        [InlineKeyboardButton(text="Надіслати оголошення", callback_data="send_announcement")],
        [InlineKeyboardButton(text="Робота з подіями", callback_data="event_admin_menu")],
        [InlineKeyboardButton(text="Спілкування (адмін)", callback_data="admin_communication_menu")]
    ]
)

limited_admin_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Робота з користувачами", callback_data="user_management_menu")],
    ]
)


user_management_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Переглянути користувачів", callback_data="view_users")],
        [InlineKeyboardButton(text="Видалити користувача", callback_data="delete_user")],
        [InlineKeyboardButton(text="Заблокувати користувача", callback_data="block_user")],
        [InlineKeyboardButton(text="Змінити доступ", callback_data="change_access")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin_menu")]
    ]
)

# --- МЕНЮ НОВИН --- #
news_admin_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Додати новину", callback_data="add_news")],
        [InlineKeyboardButton(text="Редагувати новину", callback_data="edit_news")],
        [InlineKeyboardButton(text="Видалити новину", callback_data="delete_news")],
        [InlineKeyboardButton(text="Переглянути новину", callback_data="view_news")],
        [InlineKeyboardButton(text="Всі новини", callback_data="list_news")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin_menu")]
    ]
)

# --- РЕДАГУВАННЯ ПРОФІЛЮ АДМІНА --- #
edit_admin_profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Змінити ПІБ", callback_data="admin_data_edit_full_name")],
        [InlineKeyboardButton(text="Змінити номер телефону", callback_data="admin_data_edit_phone_number")],
        [InlineKeyboardButton(text="Змінити пароль", callback_data="admin_data_edit_password")],
        [InlineKeyboardButton(text="⬅️ Назад до головного меню", callback_data="back_to_admin_menu")]
    ]
)

view_users_sort_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="За групою", callback_data="view_users_group")],
        [InlineKeyboardButton(text="За роком випуску", callback_data="view_users_year")],
        [InlineKeyboardButton(text="За спеціальністю", callback_data="view_users_specialty")],
        [InlineKeyboardButton(text="⬅️ Назад до адмін-панелі", callback_data="back_to_admin_menu")]
    ]
)

# --- МЕНЮ НОВИН КОРИСТУВАЧА --- #
user_news_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Новини за тиждень", callback_data="weekly_news")],
        [InlineKeyboardButton(text="Обрати дату", callback_data="choose_news_date")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_user_menu")]
    ]
)

# --- КНОПКА ПЕРЕГЛЯДУ ПОВНОЇ НОВИНИ --- #
def news_detail_button(news_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Детальніше", callback_data=f"news_{news_id}")]
    ])

# --- МЕНЮ ЧАТІВ --- #
communication_admin_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Чат за групою", callback_data="create_group_chat")],
        [InlineKeyboardButton(text="Чат за спеціальністю", callback_data="create_specialty_chat")],
        [InlineKeyboardButton(text="Чат за роком вступу", callback_data="create_year_chat")],
        [InlineKeyboardButton(text="Переглянути всі чати", callback_data="view_all_chats")],
        [InlineKeyboardButton(text="⬅️ Назад до адмін-панелі", callback_data="back_to_admin_menu")]
    ]
)

communication_user_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="За групою", callback_data="chat_by_group")],
        [InlineKeyboardButton(text="За спеціальністю", callback_data="chat_by_specialty")],
        [InlineKeyboardButton(text="За роком вступу", callback_data="chat_by_enrollment")],
        [InlineKeyboardButton(text="За роком випуску", callback_data="chat_by_graduation")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_user_menu")]
    ]
)


def chat_link_button(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Перейти до чату", url=url)],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="user_communication_menu")]
    ])

# --- ПІДТВЕРДЖЕННЯ ФОТО --- #
confirm_more_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Так, ще фото", callback_data="upload_yes"),
            InlineKeyboardButton(text="Завершити", callback_data="upload_no")
        ]
    ]
)

# --- ФІЛЬТРИ ФАЙЛІВ --- #
file_filter_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Фото", callback_data="filter_photo"),
        InlineKeyboardButton(text="Документи", callback_data="filter_document"),
        InlineKeyboardButton(text="Відео", callback_data="filter_video"),
    ],
    [
        InlineKeyboardButton(text="Всі", callback_data="filter_all"),
        InlineKeyboardButton(text="За користувачем", callback_data="filter_by_user"),
    ]
])

pagination_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_page"),
        InlineKeyboardButton(text="➡️ Вперед", callback_data="next_page"),
    ],
    [InlineKeyboardButton(text="⬅️ До меню", callback_data="back_to_admin_menu")]
])

# --- МЕНЮ РЕДАГУВАННЯ ПОДІЇ --- #
event_edit_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Редагувати назву", callback_data="event_edit_title")],
        [InlineKeyboardButton(text="Редагувати опис", callback_data="event_edit_description")],
        [InlineKeyboardButton(text="Редагувати дату та час", callback_data="event_edit_datetime")],
        [InlineKeyboardButton(text="Редагувати кількість місць", callback_data="event_edit_seats")],
        [InlineKeyboardButton(text="Переглянути зареєстрованих", callback_data="view_registered")],
        [InlineKeyboardButton(text="Синхронізувати з базою", callback_data="sync_event")],
        [InlineKeyboardButton(text="Видалити подію", callback_data="confirm_delete_event")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="edit_event")]
    ]
)
    
event_admin_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Додати подію", callback_data="add_event")],
        [InlineKeyboardButton(text="Видалити подію", callback_data="delete_event_menu")],
        [InlineKeyboardButton(text="Переглянути зареєстрованих", callback_data="choose_event_for_viewing")],
        [InlineKeyboardButton(text="Синхронізувати з базою", callback_data="sync_event")],
        [InlineKeyboardButton(text="Обрати подію для синхронізації", callback_data="choose_for_sync")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin_menu")]
    ]
)

event_filter_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard =[
        [InlineKeyboardButton(text="Завтра", callback_data="event_filter_day_1")],
        [InlineKeyboardButton(text="Наступний тиждень", callback_data="event_filter_day_7")],
        [InlineKeyboardButton(text="Цей місяць", callback_data="event_filter_day_30")],
        [InlineKeyboardButton(text="Всі події", callback_data="event_filter_all")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_user_menu")]
    ]
)