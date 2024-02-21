from typing import Literal

import numpy as np
import mediapipe as mp

from mediapipe.framework.formats import landmark_pb2

MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54) # vibrant green


def draw_landmarks_on_image(
      rgb_image: np.array,
      detection_result: dict,
      landmark_type: Literal['pose', 'hand']):
    """
    Courtesy of https://github.com/googlesamples/mediapipe/blob/main/examples/hand_landmarker/python/hand_landmarker.ipynb
    """

    landmarks = detection_result[landmark_type + '_landmarks']

    try:

        if landmarks == []:
            return rgb_image

        else:
            annotated_image = np.copy(rgb_image)

            for idx in range(len(landmarks)):
                landmarks_ = landmarks[idx]

                # Draw the hand landmarks.
                landmarks_proto = landmark_pb2.NormalizedLandmarkList()

                landmarks_proto.landmark.extend(
                    [
                        landmark_pb2.NormalizedLandmark(
                            x=landmark['x'],
                            y=landmark['y'],
                            z=landmark['z']
                        ) for landmark in landmarks_
                    ]
                )

                match landmark_type:

                    case 'hand':

                        mp.solutions.drawing_utils.draw_landmarks(
                            annotated_image,
                            landmarks_proto,
                            mp.solutions.hands.HAND_CONNECTIONS,
                            mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                            mp.solutions.drawing_styles.get_default_hand_connections_style()
                        )

                    case 'pose':

                        mp.solutions.drawing_utils.draw_landmarks(
                            annotated_image,
                            landmarks_proto,
                            mp.solutions.pose.POSE_CONNECTIONS,
                            mp.solutions.drawing_styles.get_default_pose_landmarks_style()
                        )

            return annotated_image

    except BaseException:
        return rgb_image
