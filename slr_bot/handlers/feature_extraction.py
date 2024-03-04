import os

from pathlib import Path

from aiogram import Router, F, Bot
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from mediapipe.tasks.python.vision import (
    HandLandmarker, HandLandmarkerOptions, RunningMode,
    PoseLandmarker, PoseLandmarkerOptions
)
from mediapipe.tasks.python.core.base_options import BaseOptions

from slr_bot.keyboards.recognition_buttons import get_label_menu
from slr_bot.keyboards.menu import get_main_menu

from hse_slr.features_extraction import BodyFeaturesExtractor


class LabelFeaturesStates(StatesGroup):
    uploading_video = State()
    choosing_result = State()


router = Router()
DATA_PATH = Path(__file__).parent.parent.parent / 'data'


@router.message(F.text == "Разметить элементы тела на видео")
async def call_label_menu(message: Message):

    await message.answer(
        "Что вы хотите разметить?",
        reply_markup=get_label_menu()
    )


@router.message(F.text == "Разметить руки")
@router.message(F.text == "Разметить позу")
async def suggest_video_upload(message: Message, state: FSMContext):

    await state.set_state(LabelFeaturesStates.uploading_video)
    await state.update_data(landmark_type=message.text)

    await message.answer(
        "Пожалуйста, загрузите видео файлом.",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(LabelFeaturesStates.uploading_video, F.document)
async def call_body_labeler(message: Message, state: FSMContext, bot: Bot):

    data = await state.get_data()
    landmark_type = data['landmark_type']

    file_path = Path(f"{message.document.file_name}.mp4")

    await message.answer("Загружаю видео.")

    await bot.download(
        message.document,
        destination=file_path
    )

    landmarkers = {
       'Разметить руки': {
           'landmark_type': 'hand',
           'landmarker': HandLandmarker,
           'landmarker_options': HandLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=str(DATA_PATH / 'hand_landmarker.task')),
                running_mode=RunningMode.VIDEO,
                num_hands=2,
                min_hand_detection_confidence=0.1,
                min_hand_presence_confidence=0.1,
                min_tracking_confidence=0.1
            )
       },
       'Разметить позу': {
           'landmark_type': 'pose',
           'landmarker': PoseLandmarker,
           'landmarker_options': PoseLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=str(DATA_PATH / 'pose_landmarker_heavy.task')),
                running_mode=RunningMode.VIDEO,
                num_poses=1,
                min_tracking_confidence=0.3
            )
       }
    }

    body_features_extractor = BodyFeaturesExtractor(
        input_video_path=file_path,
        **landmarkers[landmark_type]
    )

    video_file_name, json_file_name = body_features_extractor.extract_body_features()

    await message.answer(
        "Ожидайте завершения процесса разметки рук на видео."
    )

    await message.answer_document(
        FSInputFile(video_file_name),
        caption="Видео с наложенной разметкой",
        reply_markup=get_main_menu(),
        disable_content_type_detection=True
    )

    await message.answer_document(
        FSInputFile(json_file_name),
        caption="Файл с разметкой",
        reply_markup=get_main_menu()
    )

    os.remove(video_file_name)
    os.remove(json_file_name)
    os.remove(file_path)
