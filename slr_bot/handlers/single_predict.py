import os
from datetime import datetime
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from hse_slr.models.utils import SLInference, make_prediction

router = Router()

CONFIG_PATH = (
    Path(__file__).absolute().parent.parent.parent
    / "hse_slr/models/configs/config.json"
)

inference_thread = SLInference(CONFIG_PATH)


class PredictVideo(StatesGroup):
    downloading_video = State()


@router.message(F.text == "Распознавание РЖЯ (1 видео)")
async def call_to_download_video(message: Message, state: FSMContext):
    await message.answer(
        "Загрузите видео одним файлом. Именно файлом, а не фото/видео."
    )
    await state.set_state(PredictVideo.downloading_video)


def add_time_to_file_path(file_path: Path) -> str:
    return file_path.parent / (
        file_path.stem
        + "_"
        + datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
        + file_path.suffix
    )


@router.message(PredictVideo.downloading_video, F.document)
async def video_downloaded(message: Message, state: FSMContext, bot):
    document = message.document

    file_dir = Path(__file__).absolute().parent.parent / "data" / document.file_name
    file_dir_with_timestamp = add_time_to_file_path(file_dir)

    await bot.download(document, file_dir_with_timestamp)

    await message.answer(
        text="Сейчас модель попытается распознать РЖЯ с Вашего видео. Ожидайте, пожалуйста!"
    )

    inference_thread.start()
    res = make_prediction(inference_thread, file_dir_with_timestamp)

    if res:
        await message.answer(text=f"Результат распознавания: {res}")
    else:
        await message.answer(
            text="Извините, у нас не получилось распознать Ваше видео."
        )

    inference_thread.stop()

    os.remove(file_dir_with_timestamp)
    await state.clear()
