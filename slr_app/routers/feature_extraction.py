import os

from typing import Annotated, Literal

from pathlib import Path

from fastapi import Response, APIRouter,  File, UploadFile
from fastapi.responses import JSONResponse

from mediapipe.tasks.python.vision import (
    HandLandmarker, HandLandmarkerOptions, RunningMode,
    PoseLandmarker, PoseLandmarkerOptions
)
from mediapipe.tasks.python.core.base_options import BaseOptions
from pydantic import BaseModel

from slr_bot.keyboards.menu import get_main_menu

from hse_slr.features_extraction import BodyFeaturesExtractor


class LandmarkType_(BaseModel):
    landmark_type_: str
#  Literal['body', 'pose']

router = APIRouter(
    prefix="/feature_extraction",
    tags=["feature_extraction"],
)

DATA_PATH = Path(__file__).parent.parent.parent / 'data'


@router.post('/{landmark_type}')
def call_body_labeler(
    video_file: Annotated[bytes, File()],
    landmark_type_: Annotated[LandmarkType_, Path(title='The type of features to extract.')]
):
    # file_path = Path(f"{message.document.file_name}.mp4")

    print(landmark_type)
    print(video_file)

    return 'Got the file'


    # landmarkers = {
    #    'Разметить руки': {
    #        'landmark_type': 'hand',
    #        'landmarker': HandLandmarker,
    #        'landmarker_options': HandLandmarkerOptions(
    #             base_options=BaseOptions(model_asset_path=str(DATA_PATH / 'hand_landmarker.task')),
    #             running_mode=RunningMode.VIDEO,
    #             num_hands=2,
    #             min_hand_detection_confidence=0.1,
    #             min_hand_presence_confidence=0.1,
    #             min_tracking_confidence=0.1
    #         )
    #    },
    #    'Разметить позу': {
    #        'landmark_type': 'pose',
    #        'landmarker': PoseLandmarker,
    #        'landmarker_options': PoseLandmarkerOptions(
    #             base_options=BaseOptions(model_asset_path=str(DATA_PATH / 'pose_landmarker_heavy.task')),
    #             running_mode=RunningMode.VIDEO,
    #             num_poses=1,
    #             min_tracking_confidence=0.3
    #         )
    #    }
    # }

    # body_features_extractor = BodyFeaturesExtractor(
    #     input_video_path=file_path,
    #     **landmarkers[landmark_type]
    # )

    # video_file_name, json_file_name = body_features_extractor.extract_body_features()

    # await message.answer(
    #     "Ожидайте завершения процесса разметки рук на видео."
    # )

    # await message.answer_document(
    #     FSInputFile(video_file_name),
    #     caption="Видео с наложенной разметкой",
    #     reply_markup=get_main_menu(),
    #     disable_content_type_detection=True
    # )

    # await message.answer_document(
    #     FSInputFile(json_file_name),
    #     caption="Файл с разметкой",
    #     reply_markup=get_main_menu()
    # )

    # os.remove(video_file_name)
    # os.remove(json_file_name)
    # os.remove(file_path)
