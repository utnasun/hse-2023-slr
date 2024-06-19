import os

from slr_bot import session

from datetime import date, datetime

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from sqlalchemy import func, select

from slr_bot.db import bot_reviews_table, engine, upsert_review
from slr_bot.keyboards.menu import get_main_menu, get_rating_keyboard

router = Router()

user_data = {}


@router.message(F.text == "Оценить бота")
async def call_rating_menu(message: Message):

    user_data[message.from_user.id] = 0

    await message.answer(
        "Выберите оценку бота от 1 до 5:", reply_markup=get_rating_keyboard()
    )


async def update_num_text(message: Message, new_value: int):

    await message.edit_text(
        f'Ваша оценка: {new_value}. Нажмите "Подтвердить", если согласны с оценкой.',
        reply_markup=get_rating_keyboard(),
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

        response = session.post(f'http://{os.environ["APP_HOST"]}/rating/make_review/{user_data[callback.from_user.id]}')

        if eval(response.text) == "Go to / and try again":
            await callback.message.edit_text(
                "Пожалуста, отправьте /start для регистрации пользователя."
            )
        else:
            await callback.message.edit_text(
                f"Итоговая оценка: {user_data[callback.from_user.id]}"
            )

            await callback.message.answer(
                "Выберите интересующее вас действие", reply_markup=get_main_menu()
            )

    await callback.answer()


@router.message(F.text == "Посмотреть рейтинг бота")
async def show_rating(message: Message):
    response = session.get(f'http://{os.environ["APP_HOST"]}/rating/get_rating/')

    await message.answer(f"Средняя оценка бота: {response.json()['Средняя оценка приложения']}", reply_markup=get_main_menu())
