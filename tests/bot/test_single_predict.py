import os
from datetime import datetime
from pathlib import Path

import pytest
from aiogram import F
from aiogram.client.bot import Bot
from aiogram_tests import MockedBot
from aiogram_tests.handler import MessageHandler
from aiogram_tests.types.dataset import MESSAGE

from slr_bot.handlers.single_predict import (
    PredictVideo,
    add_time_to_file_path,
    call_to_download_video,
    video_downloaded,
)
from tests.bot.mock_datasets import MESSAGE_WITH_DOCUMENT


@pytest.mark.asyncio
async def test_call_to_download_video():
    requester = MockedBot(MessageHandler(call_to_download_video))

    calls = await requester.query(MESSAGE.as_object(text="Распознавание РЖЯ (1 видео)"))
    answer_message = calls.send_message.fetchone()

    assert (
        answer_message.text
        == "Загрузите видео одним файлом. Именно файлом, а не фото/видео."
    )


def test_add_time_to_file_path():
    file_path = Path("example.txt")

    expected_result = file_path.parent / (
        file_path.stem
        + "_"
        + datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        + file_path.suffix
    )

    result = add_time_to_file_path(file_path)
    assert result == expected_result


@pytest.mark.asyncio
async def test_downloaded_video(monkeypatch):
    async def mock_download(*args, **kwargs):
        return True

    def mock_prediction(*args, **kwargs):
        return "prediction"

    monkeypatch.setattr(Bot, "download", mock_download)

    monkeypatch.setattr(
        "slr_bot.handlers.single_predict.make_prediction", mock_prediction
    )

    monkeypatch.setattr(os, "remove", lambda file_name: file_name)

    request = MockedBot(
        MessageHandler(
            callback=video_downloaded,
            filter=F.document,
            state=PredictVideo.downloading_video,
        )
    )

    calls = await request.query(message=MESSAGE_WITH_DOCUMENT.as_object())

    answer_message = calls.send_message.fetchone()

    assert answer_message.text == "Результат распознавания: prediction"


@pytest.mark.asyncio
async def test_false_predict_video(monkeypatch):
    async def mock_download(*args, **kwargs):
        return True

    def mock_prediction(*args, **kwargs):
        return False

    monkeypatch.setattr(Bot, "download", mock_download)

    monkeypatch.setattr(
        "slr_bot.handlers.single_predict.make_prediction", mock_prediction
    )

    monkeypatch.setattr(os, "remove", lambda file_name: file_name)

    request = MockedBot(
        MessageHandler(
            callback=video_downloaded,
            filter=F.document,
            state=PredictVideo.downloading_video,
        )
    )

    calls = await request.query(message=MESSAGE_WITH_DOCUMENT.as_object())

    answer_message = calls.send_message.fetchone()

    assert answer_message.text == "Извините, у нас не получилось распознать Ваше видео."


if __name__ == "__main__":
    pytest.main(["tests/bot/test_single_predict.py"])
