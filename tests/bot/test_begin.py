import pytest

from aiogram.filters import Command
from aiogram_tests import MockedBot
from aiogram_tests.handler import MessageHandler
from aiogram_tests.types.dataset import MESSAGE
from slr_bot.handlers.begin import cmd_start
from tests.bot.mock_engine import engine


@pytest.fixture(autouse=True)
def engine_mock(monkeypatch):
    monkeypatch.setattr('slr_bot.handlers.begin', engine)


@pytest.mark.asyncio
async def test_cmd_start_handler():

    requester = MockedBot(
        MessageHandler(cmd_start, Command("start"))
    )

    calls = await requester.query(MESSAGE.as_object(text="/start"))
    reply_message = calls.send_message.fetchone().text
    assert reply_message == (
        "Выберите интересующее вас действие"
    )
