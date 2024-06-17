import json

import logging

from threading import Thread
from hse_slr.models.model import Predictor
from pathlib import Path
from omegaconf import OmegaConf
from hse_slr.recognition import Runner

import time
from collections import deque
from pathlib import Path
from threading import Thread

import cv2

from hse_slr.models.model import Predictor

logging.basicConfig(level=logging.INFO)


class SLInference:
    """
    Main prediction thread.

    Attributes:
        running (bool): Flag to control the running of the thread.
        config (dict): Configuration parameters for the model.
        model (Predictor): The prediction model.
        input_queue (deque): A queue to hold the input data.
        pred (str): The prediction result.
        thread (Thread): The worker thread.
    """

    def __init__(self, config_path):
        """
        Initialize the SLInference object.

        Args:
            config_path (str): Path to the configuration file.
        """
        self.running = True
        self.config = self.read_config(config_path)
        self.model = Predictor(self.config)
        self.input_queue = deque(maxlen=self.config["window_size"])
        self.pred = ""

    def read_config(self, config_path):
        """
        Read the configuration file.

        Args:
            config_path (str): Path to the configuration file.

        Returns:
            dict: The configuration parameters.
        """
        with open(config_path, "r") as f:
            config = json.load(f)
        return config

    def worker(self):
        """
        The main worker function that runs in a separate thread.
        """
        while self.running:
            if len(self.input_queue) == self.config["window_size"]:
                pred_dict = self.model.predict(self.input_queue)
                if pred_dict:
                    self.pred = pred_dict["labels"][0]
                    self.input_queue.clear()
                else:
                    self.pred = ""
            time.sleep(0.1)

    def start(self):
        """
        Start the worker thread.
        """
        self.thread = Thread(target=self.worker)
        self.thread.start()

    def stop(self):
        """
        Stop the worker thread.
        """
        self.running = False
        self.pred = ""
        self.input_queue = deque(maxlen=self.config["window_size"])
        self.thread.join()


def make_prediction(inference_thread: SLInference, file_path: Path) -> str:
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

    conf = OmegaConf.load("/Users/lmruwork/Desktop/Education/Masters/hse-2023-slr/configs/s3d_32_1_conf.yaml")
    runner = Runner(conf.model_path, conf, mp, verbose, length)

    predictions = runner.run(file_path)

    logging.info(f"Результат распознавания: {predictions}")

    return predictions

