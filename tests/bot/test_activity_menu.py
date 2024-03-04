import pytest
import os
os.environ['BOT_ENV'] = 'test'

from sqlalchemy import insert, text, select

from slr_bot.handlers.activity import call_rating_menu, get_num_unique_users, get_new_users_by_dow_count
from slr_bot.db import engine, bot_users_table, bot_users_table

from aiogram_tests import MockedBot
from aiogram_tests.handler import MessageHandler
from aiogram_tests.types.dataset import MESSAGE


@pytest.mark.asyncio
async def test_call_rating_menu():
    request = MockedBot(MessageHandler(call_rating_menu))
    calls = await request.query(message=MESSAGE.as_object(text="Получить аналитику об активности"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text == "Что вы хотите узнать?"


@pytest.mark.asyncio
async def test_get_num_unique_users():

    request = MockedBot(MessageHandler(get_num_unique_users))
    calls = await request.query(message=MESSAGE.as_object(text="Количество уникальных пользователей"))
    answer_message = calls.send_message.fetchone()

    assert answer_message.text == "Количество уникальных пользователей: 1"


@pytest.mark.asyncio
async def test_get_new_users_by_dow_count():
    request = MockedBot(MessageHandler(get_new_users_by_dow_count))

    calls = await request.query(message=MESSAGE.as_object(text="Суммарное количество новых пользователей по дням недели"))
    answer_message = calls.send_message.fetchone()

    assert answer_message.text == '\n        Суммарное количество новых пользователей по дням недели:\n        <pre>+-------------+------------+\n| День недели | Количество |\n+-------------+------------+\n|      0      |     1      |\n+-------------+------------+</pre>\n        '
