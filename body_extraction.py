import cv2 as cv
import mediapipe as mp
import dataclasses
import time

from tqdm import tqdm

from pathlib import Path

model_path = './data/pose_landmarker_heavy.task'

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    num_poses = 1,
    running_mode=VisionRunningMode.VIDEO,
    min_pose_detection_confidence = 0.3,
    min_tracking_confidence = 0.3)    

for data_type in ['train', 'test']:
    video_path_dir = Path(f'./data/{data_type}')

    pose_landmark_features = {}

    for video_file_path in tqdm([*video_path_dir.iterdir()]):

        if str(video_file_path.name).startswith('.'):
            pass

        cap = cv.VideoCapture(str(video_file_path))

        with PoseLandmarker.create_from_options(options) as landmarker:

            pose_landmarker_results = []

            while True:
                ret, frame = cap.read()

                if not ret:
                    print("Can't receive frame (stream end?). Exiting ...")
                    break

                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
                
                pose_landmarker_result = landmarker.detect_for_video(mp_image, int(time.time() * 1000))
                pose_landmarker_results.append(dataclasses.asdict(pose_landmarker_result))

        cap.release()

        pose_landmark_features[video_file_path.stem] = pose_landmarker_results

    with open(f'./data/gesture_landmarks_{data_type}.json', 'w') as gesture_file:
        json.dump(hand_landmark_features, gesture_file)