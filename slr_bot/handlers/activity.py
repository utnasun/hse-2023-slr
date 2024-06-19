import os

from aiogram import F, Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message
from prettytable import PrettyTable
from sqlalchemy import func, select

from slr_bot import session
from slr_bot.keyboards.activity_buttons import get_activity_menu
from slr_bot.keyboards.menu import get_main_menu

router = Router()


@router.message(F.text == "Получить аналитику об активности")
async def call_rating_menu(message: Message):
    await message.answer("Что вы хотите узнать?", reply_markup=get_activity_menu())


@router.message(F.text == "Количество уникальных пользователей")
async def get_num_unique_users(message: Message):
    

    response = session.get(f'http://{os.environ["APP_HOST"]}/activity/unique_users')
    print(response.text)

    await message.answer(
        f"Количество уникальных пользователей: {response.json()['Количество уникальных пользователей']}",
        reply_markup=get_main_menu(),
    )


@router.message(F.text == "Суммарное количество новых пользователей по дням недели")
async def get_new_users_by_dow_count(message: Message):
    new_users_by_dow_table = PrettyTable()

    response = session.get(f'http://{os.environ["APP_HOST"]}/activity/new_users_by_dow')

    new_users_by_dow_table.field_names = (
        response.json()[0].keys()
    )
    new_users_by_dow_table.add_rows(
        [list(weekday.values()) for weekday in response.json()]
    )

    await message.answer(
        f"""
        Суммарное количество новых пользователей по дням недели:
        <pre>{new_users_by_dow_table}</pre>
        """,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu(),
    )
