import os

import pytest
from aiogram import F
from aiogram.client.bot import Bot
from aiogram_tests import MockedBot
from aiogram_tests.handler import MessageHandler
from aiogram_tests.types.dataset import MESSAGE

from hse_slr.features_extraction import BodyFeaturesExtractor
from slr_bot.handlers.feature_extraction import (
    LabelFeaturesStates,
    call_body_labeler,
    call_label_menu,
    suggest_video_upload,
)
from tests.bot.mock_datasets import MESSAGE_WITH_DOCUMENT


@pytest.mark.asyncio
async def test_call_label_menu():
    request = MockedBot(MessageHandler(call_label_menu))
    calls = await request.query(
        message=MESSAGE.as_object(text="Разметить элементы тела на видео")
    )
    answer_message = calls.send_message.fetchone()
    assert answer_message.text == "Что вы хотите разметить?"


@pytest.mark.asyncio
async def test_call_hand_extraction():
    request = MockedBot(MessageHandler(suggest_video_upload))
    calls = await request.query(message=MESSAGE.as_object(text="Разметить руки"))
    answer_message = calls.send_message.fetchone()

    assert answer_message.text == "Пожалуйста, загрузите видео файлом."


@pytest.mark.asyncio
async def test_call_pose_extraction():
    request = MockedBot(MessageHandler(suggest_video_upload))
    calls = await request.query(message=MESSAGE.as_object(text="Разметить позу"))
    answer_message = calls.send_message.fetchone()

    assert answer_message.text == "Пожалуйста, загрузите видео файлом."


@pytest.mark.asyncio
async def test_label_pose(monkeypatch):
    async def mock_download(*args, **kwargs):
        return True

    monkeypatch.setattr(Bot, "download", mock_download)

    monkeypatch.setattr(
        BodyFeaturesExtractor,
        "extract_body_features",
        lambda _: ("test_video", "test_json"),
    )

    monkeypatch.setattr(os, "remove", lambda file_name: file_name)

    request = MockedBot(
        MessageHandler(
            callback=call_body_labeler,
            filter=F.document,
            state=LabelFeaturesStates.uploading_video,
            state_data={"landmark_type": "Разметить руки"},
        )
    )

    calls = await request.query(message=MESSAGE_WITH_DOCUMENT.as_object())

    answer_message = calls.send_message.fetchone()

    assert answer_message.text == "Ожидайте завершения процесса разметки рук на видео."


if __name__ == "__main__":
    pytest.main(["tests/bot/test_features_extraction.py"])
