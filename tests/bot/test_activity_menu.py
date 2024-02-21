import pytest
import os
os.environ['BOT_ENV'] = 'test'

from sqlalchemy import insert, text, select

from slr_bot.handlers.activity import call_rating_menu, get_num_unique_users, get_new_users_by_dow_count
from slr_bot.db import engine, bot_users_table

from aiogram_tests import MockedBot
from aiogram_tests.handler import MessageHandler
from aiogram_tests.types.dataset import MESSAGE


@pytest.fixture()
def sqlite_db():

    with engine.connect() as conn:
        conn.execute(
            insert(bot_users_table)
            .values(
                [
                    {'user_id': 1},
                    {'user_id': 2},
                    {'user_id': 3}
                ]
            )
        )

        conn.commit()

    with engine.connect() as conn:
        print(conn.execute(select(bot_users_table)).fetchall())

    yield


@pytest.mark.asyncio
async def test_call_rating_menu():
    request = MockedBot(MessageHandler(call_rating_menu))
    calls = await request.query(message=MESSAGE.as_object(text="Получить аналитику об активности"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text == "Что вы хотите узнать?"


@pytest.mark.asyncio
async def test_get_num_unique_users(sqlite_db):

    request = MockedBot(MessageHandler(get_num_unique_users))
    calls = await request.query(message=MESSAGE.as_object(text="Количество уникальных пользователей"))
    answer_message = calls.send_message.fetchone()

    assert answer_message.text == "Количество уникальных пользователей: 3"


# @pytest.mark.asyncio
# async def test_get_new_users_by_dow_count():

#     request = MockedBot(MessageHandler(get_new_users_by_dow_count))
#     calls = await request.query(message=MESSAGE.as_object(text="Суммарное количество новых пользователей по дням недели"))
#     answer_message = calls.send_message.fetchone()

#     expected_text = f"""
#                 Суммарное количество новых пользователей по дням недели:
#                 <pre>+-------------+------------+
#         | День недели | Количество |
#         +-------------+------------+
#         |      1      |     2      |
#         |      2      |     3      |
#         |      3      |     3      |
#         |      4      |     2      |
#         |      5      |     3      |
#         |      6      |     4      |
#         |      7      |     4      |
#         +-------------+------------+</pre>
#         """
#     assert answer_message.text == expected_text
