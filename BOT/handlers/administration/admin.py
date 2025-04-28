# from aiogram import Router, types
# from aiogram.filters import Command
# from ...utils.keyboard import admin_panel_keyboard

# router = Router()

# @router.message(Command("admin_panel"))
# async def admin_panel(message: types.Message):
#     await message.answer(
#         "🔧 Панель адміністратора:",
#         reply_markup=admin_panel_keyboard()
#     )