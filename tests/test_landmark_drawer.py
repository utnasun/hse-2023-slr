import pytest
import numpy as np

from hse_slr.draw_landmarks import draw_landmarks_on_image


@pytest.fixture()
def test_image():
    image = np.array([1, 2, 3])

    yield image


def test_empty_landmarks(test_image):

    result = draw_landmarks_on_image(
        rgb_image=test_image,
        detection_result={
            "handedness": [],
            "hand_landmarks": [],
            "hand_world_landmarks": []
        },
        landmark_type='hand'
    )

    assert test_image is result


def test_error_return(test_image):

    result = draw_landmarks_on_image(
        rgb_image=test_image,
        detection_result={
            "handedness": [],
            "hand_landmarks": ['test', 'error'],
            "hand_world_landmarks": []
        },
        landmark_type='hand'
    )

    assert test_image is result
