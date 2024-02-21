import os
import time
import dataclasses
import json

import cv2 as cv
import mediapipe as mp

from pathlib import Path
from typing import Literal, Tuple, Union, Optional
from datetime import datetime
from hse_slr.draw_landmarks import draw_landmarks_on_image


from mediapipe.tasks.python.vision import (
    HandLandmarker, PoseLandmarker,
    HandLandmarkerOptions, PoseLandmarkerOptions
)


class BodyFeaturesExtractor:
    def __init__(
        self,
        input_video_path: Union[Path, str],
        landmarker: Union[HandLandmarker, PoseLandmarker],
        landmarker_options: Union[HandLandmarkerOptions, PoseLandmarkerOptions],
        landmark_type: Literal['pose', 'hand']
    ) -> None:

        self.input_video_path = Path(input_video_path)
        self.landmarker = landmarker
        self.landmarker_options = landmarker_options
        self.landmark_type = landmark_type

    def _add_time_to_file_path(
            self,
            file_path: Path
    ) -> Path:

        return (
           file_path.parent /
           (
               file_path.stem +
               '_' +
               datetime.now().strftime("%m_%d_%Y_%H_%M_%S") +
               file_path.suffix
           )
        )

    def extract_body_features(
        self,
        output_dir: Optional[Union[Path, str]] = None
    ) -> Tuple[Path, Path]:

        if not output_dir:
            output_dir = Path(os.getcwd())

        if not Path(output_dir).is_dir():
            raise TypeError('output_dir argument must be a directory.')

        json_file_name = self._add_time_to_file_path(Path('body_features_extractor_results.json'))
        video_file_name = self._add_time_to_file_path(Path('annotated_video.mp4'))

        json_file_path = str(output_dir / json_file_name)
        video_file_path = str(output_dir / video_file_name)

        cap = cv.VideoCapture(str(self.input_video_path))

        video_writer = cv.VideoWriter(
            video_file_path,
            cv.VideoWriter_fourcc(*'mp4v'),
            cap.get(cv.CAP_PROP_FPS),
            (
                int(cap.get(cv.CAP_PROP_FRAME_WIDTH)),
                int(cap.get(cv.CAP_PROP_FRAME_HEIGHT)),
            )
        )

        landmarker_results = []

        with self.landmarker.create_from_options(self.landmarker_options) as landmarker:

            while True:

                ret, frame = cap.read()

                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    break

                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

                landmarker_result = dataclasses.asdict(landmarker.detect_for_video(mp_image, int(time.time() * 1000)))

                annotated_image = draw_landmarks_on_image(
                    mp_image.numpy_view(),
                    landmarker_result,
                    self.landmark_type
                )

                landmarker_results.append(landmarker_result)
                video_writer.write(annotated_image)

        cap.release()

        with open(json_file_path, 'w') as results_file:
            json.dump(landmarker_results, results_file)

        return Path(video_file_path), Path(json_file_path)
