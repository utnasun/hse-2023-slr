import pytest
import os
os.environ['BOT_ENV'] = 'test'

from aiogram_tests import MockedBot
from aiogram_tests.handler import MessageHandler
from aiogram_tests.types.dataset import MESSAGE

from slr_bot.handlers.begin import cmd_start
from slr_bot.db import engine


@pytest.mark.asyncio
async def test_call_begin_menu():
    request = MockedBot(MessageHandler(cmd_start))
    calls = await request.query(message=MESSAGE.as_object(text="start"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text == "Выберите интересующее вас действие"


@pytest.mark.asyncio
async def test_insert_user():
    request = MockedBot(MessageHandler(cmd_start))
    calls = await request.query(message=MESSAGE.as_object(text="start"))
    calls.send_message.fetchone()
    assert engine.obj.is_insert
