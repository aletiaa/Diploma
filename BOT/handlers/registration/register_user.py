from aiogram import Router, types
from aiogram.filters import Command
from .state import user_state
from .shared_registration_steps import (
    handle_contact,
    ask_for_phone_number,
    ask_about_old_number,
    ask_old_number_directly,
    ask_birth_date,
    ask_graduation_year,
    ask_department,
    ask_specialty,
    finalize_registration
)
from ...utils.phone_validator import is_valid_phone

router = Router()

@router.message(Command("start"))
async def start_user(message: types.Message):
    chat_id = message.chat.id
    user_state[chat_id] = {"step": "name", "role": "user"}
    await message.answer("👤 Почнемо реєстрацію. Вкажіть ваше ім’я та прізвище:")

@router.message(lambda message: message.contact is not None)
async def contact_handler(message: types.Message):
    return await handle_contact(message, role="user")

@router.message()
async def continue_registration(message: types.Message):
    chat_id = message.chat.id
    text = message.text.strip()
    state = user_state.get(chat_id)

    if not state:
        return

    step = state.get("step")

    if step == "name":
        state["name"] = text
        return await ask_for_phone_number(message)

    elif step == "phone_number":
        if not is_valid_phone(text):
            await message.answer("❗ Невірний формат номера телефону або невідомий код країни. Спробуйте ще раз.")
            return
        state["phone_number"] = text
        state["step"] = "ask_old_number"
        await message.answer("📲 Чи мали ви цей номер під час навчання? Введіть <b>так</b> або <b>ні</b>.")

    elif step == "ask_old_number":
        await ask_about_old_number(message)

    elif step == "enter_old_number":
        await ask_old_number_directly(message)

    elif step == "birth_date":
        await ask_birth_date(message)

    elif step == "year":
        await ask_graduation_year(message)

    elif step == "department":
        await ask_department(message)

    elif step == "specialty":
        await ask_specialty(message)

    elif step == "finalize":
        await finalize_registration(message)
