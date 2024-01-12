import re

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.menu import get_main_menu, get_rating_keyboard

router = Router()

user_data = {}

@router.message(F.text == "Оценить бота")
async def call_rating_menu(message: Message):
    user_data[message.from_user.id] = 0
    await message.answer(
        "Выберите оценку бота от 1 до 5:",
        reply_markup=get_rating_keyboard()
    )

async def update_num_text(message: Message, new_value: int):
    await message.edit_text(
        f"Ваша оценка: {new_value}. Нажмите \"Подтвердить\", если согласны с оценкой.",
        reply_markup=get_rating_keyboard()
    )

@router.callback_query(F.data.startswith("num_"))
async def callbacks_num(callback: CallbackQuery):
    action = callback.data.split("_")[1]
    if action == "one":
        user_data[callback.from_user.id] = 1
        await update_num_text(callback.message, 1)
    elif action == "two":
        user_data[callback.from_user.id] = 2
        await update_num_text(callback.message, 2)
    elif action == "three":
        user_data[callback.from_user.id] = 3
        await update_num_text(callback.message, 3)
    elif action == "four":
        user_data[callback.from_user.id] = 4
        await update_num_text(callback.message, 4)
    elif action == "five":
        user_data[callback.from_user.id] = 5
        await update_num_text(callback.message, 5)
    elif action == "finish":
        await callback.message.edit_text(f"Итоговая оценка: {user_data[callback.from_user.id]}")
        await callback.message.answer(
         f"Выберите интересующее вас действие",
         reply_markup=get_main_menu()
         )

    await callback.answer()


# @router.message(F.text.regexp(r'[1-5]'))
# async def answer_no(message: Message):
#     await message.answer(
#         f"Ваша оценка: {message.text}. Выберите следующее действие:",
#         reply_markup=get_main_menu()
#     )
