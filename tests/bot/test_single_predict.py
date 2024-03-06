import pytest
import os
from datetime import datetime
from pathlib import Path

from aiogram import types, F
from aiogram_tests import MockedBot
from aiogram_tests.handler import MessageHandler
from aiogram_tests.types.dataset import MESSAGE, MESSAGE_WITH_DOCUMENT, DatasetItem
from aiogram.client.bot import Bot

from slr_bot.handlers.single_predict import (
    call_to_download_video,
    add_time_to_file_path,
    video_downloaded,
    PredictVideo
)

DATA_PATH = Path(__file__).parent.parent.parent / 'data'

DOCUMENT = DatasetItem(
    {
        "file_name": str(DATA_PATH / 'raw/test/0a89730f-c271-4429-8351-fdfb2daf6b81'),
        "mime_type": "video/quicktime",
        "file_id": "BQADAgADpgADy_JxS66XQTBRHFleAg",
        "file_unique_id": "file_unique_id",
        "file_size": 21331,
    },
    model=types.Document,
)

MESSAGE_WITH_DOCUMENT.data['document'] = DOCUMENT


@pytest.mark.asyncio
async def test_call_to_download_video():

    requester = MockedBot(
        MessageHandler(call_to_download_video)
    )

    calls = await requester.query(MESSAGE.as_object(text="Распознавание РЖЯ (1 видео)"))
    answer_message = calls.send_message.fetchone()

    assert answer_message.text == "Загрузите видео одним файлом. Именно файлом, а не фото/видео."


def test_add_time_to_file_path():
    file_path = Path("example.txt")

    expected_result = (
        file_path.parent /
        (
            file_path.stem +
            '_' +
            datetime.now().strftime("%m_%d_%Y_%H_%M_%S") +
            file_path.suffix
        )
    )

    result = add_time_to_file_path(file_path)
    assert result == expected_result


@pytest.mark.asyncio
async def test_downloaded_video(monkeypatch):

    async def mock_download(*args, **kwargs):
        return True

    def mock_prediction(*args, **kwargs):
        return 'prediction'

    monkeypatch.setattr(Bot, 'download', mock_download)

    monkeypatch.setattr("slr_bot.handlers.single_predict.make_prediction", mock_prediction)

    monkeypatch.setattr(os, 'remove', lambda file_name: file_name)

    request = MockedBot(
        MessageHandler(
            callback=video_downloaded,
            filter=F.document,
            state=PredictVideo.downloading_video,
        )
    )

    calls = await request.query(
        message=MESSAGE_WITH_DOCUMENT.as_object()
    )

    answer_message = calls.send_message.fetchone()

    assert answer_message.text == "Результат распознавания: prediction"


@pytest.mark.asyncio
async def test_false_predict_video(monkeypatch):

    async def mock_download(*args, **kwargs):
        return True

    def mock_prediction(*args, **kwargs):
        return False

    monkeypatch.setattr(Bot, 'download', mock_download)

    monkeypatch.setattr("slr_bot.handlers.single_predict.make_prediction", mock_prediction)

    monkeypatch.setattr(os, 'remove', lambda file_name: file_name)

    request = MockedBot(
        MessageHandler(
            callback=video_downloaded,
            filter=F.document,
            state=PredictVideo.downloading_video,
        )
    )

    calls = await request.query(
        message=MESSAGE_WITH_DOCUMENT.as_object()
    )

    answer_message = calls.send_message.fetchone()

    assert answer_message.text == "Извините, у нас не получилось распознать Ваше видео."

if __name__ == '__main__':
    pytest.main(['tests/bot/test_single_predict.py'])
