import pytest
import os
from sqlalchemy import insert, func, select

from aiogram_tests import MockedBot
from aiogram_tests.handler import MessageHandler, CallbackQueryHandler
from aiogram_tests.types.dataset import MESSAGE, CALLBACK_QUERY
from slr_bot.handlers.rating import call_rating_menu, callbacks_num, show_rating
from slr_bot.db import engine, bot_reviews_table

os.environ['BOT_ENV'] = 'test'


@pytest.fixture()
def sqlite_db():

    with engine.connect() as conn:
        conn.execute(
            insert(bot_reviews_table)
            .values(
                [
                    {'user_id': '100', 'mark': 5},
                    {'user_id': '200', 'mark': 4},
                    {'user_id': '300', 'mark': 3}
                ]
            )
        )

        conn.commit()

    with engine.connect() as conn:
        print(conn.execute(select(func.round(func.avg(bot_reviews_table.c.mark), 2))).fetchall()[0][0])

    yield


@pytest.mark.asyncio
async def test_call_menu_handler():

    requester = MockedBot(
        MessageHandler(call_rating_menu)
    )

    calls = await requester.query(MESSAGE.as_object(text="Оценить бота"))
    answer_message = calls.send_message.fetchone()

    assert answer_message.text == "Выберите оценку бота от 1 до 5:"
    assert "inline_keyboard" in answer_message.reply_markup


@pytest.mark.parametrize("call_back_num", ['num_one', 'num_two', 'num_three', 'num_four', 'num_five'])
@pytest.mark.asyncio
async def test_callbacks_num(call_back_num):

    requester = MockedBot(
        CallbackQueryHandler(callbacks_num)
    )

    dict_nums = {'num_one': '1', 'num_two': '2', 'num_three': '3', 'num_four': '4', 'num_five': '5'}

    callback_query = CALLBACK_QUERY.as_object(
        data=call_back_num, message=MESSAGE.as_object(text="Выберите оценку бота от 1 до 5")
    )
    calls = await requester.query(callback_query)

    callback_query = CALLBACK_QUERY.as_object(
        data="num_finish",
        message=MESSAGE.as_object(text=f"Ваша оценка: {dict_nums[call_back_num]}.\
                                   Нажмите \"Подтвердить\", если согласны с оценкой.")
    )
    calls = await requester.query(callback_query)

    answer_text = calls.send_message.fetchone().text
    assert answer_text == "Выберите интересующее вас действие"
    assert "keyboard" in calls.send_message.fetchone().reply_markup


@pytest.mark.asyncio
async def test_show_rating(sqlite_db):
    requester = MockedBot(
        MessageHandler(show_rating)
    )

    calls = await requester.query(message=MESSAGE.as_object(text="Посмотреть рейтинг бота"))
    answer_message = calls.send_message.fetchone()

    # marks : 5, 4, 3 fixture and 5 from test_callbacks_num
    assert answer_message.text == "Средняя оценка бота: 4.25"
    assert "keyboard" in calls.send_message.fetchone().reply_markup
