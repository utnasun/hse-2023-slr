from aiogram import F, Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message
from prettytable import PrettyTable
from sqlalchemy import func, select

from slr_bot.db import bot_users_table, engine
from slr_bot.keyboards.activity_buttons import get_activity_menu
from slr_bot.keyboards.menu import get_main_menu

router = Router()


@router.message(F.text == "Получить аналитику об активности")
async def call_rating_menu(message: Message):
    await message.answer("Что вы хотите узнать?", reply_markup=get_activity_menu())


@router.message(F.text == "Количество уникальных пользователей")
async def get_num_unique_users(message: Message):
    num_unique_users_statement = select(func.count(bot_users_table.c.user_id))

    with engine.connect() as conn:
        num_unique_users = conn.execute(num_unique_users_statement).scalar_one()

    await message.answer(
        f"Количество уникальных пользователей: {num_unique_users}",
        reply_markup=get_main_menu(),
    )


@router.message(F.text == "Суммарное количество новых пользователей по дням недели")
async def get_new_users_by_dow_count(message: Message):
    new_users_by_dow_table = PrettyTable()

    extract_dow_func = func.extract("isodow", bot_users_table.c.init_dttm)

    new_users_by_dow_count_statement = (
        select(
            extract_dow_func.label("День недели"),
            func.count(bot_users_table.c.user_id).label("Количество"),
        )
        .group_by(extract_dow_func)
        .order_by(extract_dow_func)
    )

    with engine.connect() as conn:
        new_users_by_dow = conn.execute(new_users_by_dow_count_statement)
        conn.commit()

    new_users_by_dow_table.field_names = (
        new_users_by_dow_count_statement.selected_columns.keys()
    )
    new_users_by_dow_table.add_rows(new_users_by_dow.fetchall())

    await message.answer(
        f"""
        Суммарное количество новых пользователей по дням недели:
        <pre>{new_users_by_dow_table}</pre>
        """,
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu(),
    )
