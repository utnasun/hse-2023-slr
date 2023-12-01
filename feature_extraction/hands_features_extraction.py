import mediapipe as mp
import cv2 as cv
import json
import time
import dataclasses

from tqdm import tqdm
from pathlib import Path

model_path = './data/hand_landmarker.task'

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence = 0.1,
    min_hand_presence_confidence = 0.1,
    min_tracking_confidence = 0.1
)

for data_type in ['train', 'test']:
    video_path_dir = Path(f'./data/raw/{data_type}')

    hand_landmark_features = {}

    for video_file_path in tqdm([*video_path_dir.iterdir()]):

        if str(video_file_path.name).startswith('.'):
            pass

        cap = cv.VideoCapture(str(video_file_path))

        with HandLandmarker.create_from_options(options) as landmarker:

            hand_landmarker_results = []

            while True:

                ret, frame = cap.read()

                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    break

                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

                hand_landmarker_result = landmarker.detect_for_video(mp_image, int(time.time() * 1000))
                hand_landmarker_results.append(dataclasses.asdict(hand_landmarker_result))

        cap.release()

        hand_landmark_features[video_file_path.stem] = hand_landmarker_results

    with open(f'./data/gesture_landmarks_{data_type}.json', 'w') as gesture_file:
        json.dump(hand_landmark_features, gesture_file)


