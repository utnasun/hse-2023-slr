import pytest
import os

from pathlib import Path

from mediapipe.tasks.python.vision import (
    HandLandmarker, HandLandmarkerOptions, RunningMode,
    PoseLandmarker, PoseLandmarkerOptions
)

from mediapipe.tasks.python.core.base_options import BaseOptions

from hse_slr.features_extraction import BodyFeaturesExtractor


DATA_PATH = Path(__file__).parent.parent / 'data'
MODEL_PATH = DATA_PATH / 'hand_landmarker.task'


pose_options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=str(DATA_PATH / 'pose_landmarker_heavy.task')),
    running_mode=RunningMode.VIDEO,
    num_poses=1,
    min_tracking_confidence=0.3
)

hand_options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.1,
    min_hand_presence_confidence=0.1,
    min_tracking_confidence=0.1
)


@pytest.fixture()
def body_features_extractor(request):

    body_features_extractor = BodyFeaturesExtractor(
        input_video_path=DATA_PATH / 'raw/test/0a89730f-c271-4429-8351-fdfb2daf6b81.mp4',
        landmarker=request.param[0],
        landmarker_options=request.param[1],
        landmark_type=request.param[2]
    )

    yield body_features_extractor


@pytest.fixture()
def formatted_video_path(body_features_extractor):
    path_formatted = body_features_extractor._add_time_to_file_path(body_features_extractor.input_video_path)
    yield path_formatted


@pytest.fixture()
def extracted_features(body_features_extractor):
    body_features = body_features_extractor.extract_body_features()
    yield body_features
    for features in body_features:
        os.remove(features)


@pytest.fixture()
def not_dir_file():
    with open('not_dir', 'w') as file:
        file.write('test')

    yield file

    os.remove('not_dir')


@pytest.mark.parametrize(
    "body_features_extractor",
    [
        (PoseLandmarker, pose_options, 'pose'),
        (HandLandmarker, hand_options, 'hand')
    ],
    indirect=True
)
class TestPath:

    def test_path_type(self, body_features_extractor, formatted_video_path):
        assert isinstance(formatted_video_path, Path)

    def test_path_datestamp_existance(self, body_features_extractor, formatted_video_path):
        assert len(formatted_video_path.stem.split('_')) > 1


@pytest.mark.parametrize(
    "body_features_extractor",
    [
        (PoseLandmarker, pose_options, 'pose'),
        (HandLandmarker, hand_options, 'hand')
    ],
    indirect=True
)
class TestExtractedFeatures:

    def test_num_output_files(self, body_features_extractor, extracted_features):
        assert len(extracted_features) == 2

    def test_wrong_type_output_dir(self, body_features_extractor, not_dir_file):

        with pytest.raises(TypeError, match='output_dir argument must be a directory.'):
            body_features_extractor.extract_body_features('not_dir')

    def test_video_extension(self, body_features_extractor, extracted_features):
        assert extracted_features[0].suffix == '.mp4'

    def test_features_extension(self, body_features_extractor, extracted_features):
        assert extracted_features[1].suffix == '.json'
