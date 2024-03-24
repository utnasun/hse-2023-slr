import os
import json


from pathlib import Path

from fastapi import Response, APIRouter,  File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from starlette.background import BackgroundTasks


from mediapipe.tasks.python.vision import (
    HandLandmarker, HandLandmarkerOptions, RunningMode,
    PoseLandmarker, PoseLandmarkerOptions
)
from mediapipe.tasks.python.core.base_options import BaseOptions
from enum import Enum

from slr_bot.keyboards.menu import get_main_menu

from hse_slr.features_extraction import BodyFeaturesExtractor


class LandmarkType(str, Enum):
    hand = 'hand'
    pose = 'pose'


class OutputFileType(str, Enum):
    json = 'json'
    video = 'video'


def remove_file(path: str) -> None:
    os.remove(path)


router = APIRouter(
    prefix="/feature_extraction",
    tags=["feature_extraction"],
)

DATA_PATH = Path(__file__).parent.parent.parent / 'data'


@router.post('/{landmark_type}/{output_file_type}')
async def call_body_labeler(
    landmark_type: LandmarkType,
    output_file_type: OutputFileType,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):

    file_path = Path("./uploads") / file.filename

    with file_path.open("wb") as buffer:
        buffer.write(await file.read())

    landmarkers = {
       'hand': {
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
       'pose': {
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
        **landmarkers[landmark_type.value]
    )

    video_file_name, json_file_name = body_features_extractor.extract_body_features()

    background_tasks.add_task(remove_file, file_path)
    background_tasks.add_task(remove_file, video_file_name)
    background_tasks.add_task(remove_file, json_file_name)

    match output_file_type.value:
        case 'json':
            with open(json_file_name, 'r') as file:
                return JSONResponse(json.load(file))

        case 'video':
            return FileResponse(video_file_name)
