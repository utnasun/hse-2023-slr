import logging

from pathlib import Path
from omegaconf import OmegaConf
from hse_slr.recognition import Runner

from pathlib import Path

import cv2

logging.basicConfig(level=logging.INFO)


def make_prediction(file_path: Path) -> str:
    """
    Perform gesture prediction on a video file.

    Parameters
    ----------
    inference_thread : SLInference
        A thread for performing gesture inference.
    file_path : Path
        Path to the video file for gesture prediction.

    Returns
    -------
    str
    Predicted gestures concatenated as a single string.
    """
    cap = cv2.VideoCapture(str(file_path))

    mp = False # Enable multiprocessing
    verbose = False # Enable logging
    length = 1000 # Deque length for predictions

    project_path = (Path(__file__).parent.parent) 

    conf = OmegaConf.load(project_path / 'configs' / 'mvit_32_2_conf.yaml')

    runner = Runner(
        str(project_path / 'data' / 'models' / conf.model_name),
        conf,
        mp,
        verbose,
        length
    )

    predictions = runner.run(file_path)

    logging.info(f"Результат распознавания: {predictions}")
    
    return predictions


if __name__ == '__main__':
    print((Path(__file__).parent.parent))
