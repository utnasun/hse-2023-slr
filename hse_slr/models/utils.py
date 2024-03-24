from collections import deque
import json
from threading import Thread
from hse_slr.models.model import Predictor
from pathlib import Path
import time
import cv2
import logging

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
    cap = cv2.VideoCapture(str(file_path))

    gestures_deque = deque(maxlen=10)

    while True:
        success, img = cap.read()
        if not success:
            logging.info("Завершение чтения видео.")
            break

        img_resized = cv2.resize(img, (224, 224))
        inference_thread.input_queue.append(img_resized)

        gesture = inference_thread.pred

        if gesture not in ['no', '']:
            if not gestures_deque:
                gestures_deque.append(gesture)
            elif gesture != gestures_deque[-1]:
                gestures_deque.append(gesture)

        cv2.waitKey(1)

    cap.release()
    result = ""
    for gest in gestures_deque:
        result = result + gest + " "
    logging.info(f'Результат распознавания: {result}')
    return result
