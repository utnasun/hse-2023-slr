import os
import time
from collections import deque
from multiprocessing import Manager, Process, Value

import cv2
import numpy as np
import onnxruntime as ort
import pandas as pd
from constants import classes
from loguru import logger
from omegaconf import OmegaConf
from sklearn.metrics import confusion_matrix


class BaseRecognition:
    def __init__(self, model_path: str, tensors_list, prediction_list, verbose):
        self.verbose = verbose
        self.started = None
        self.output_names = None
        self.input_shape = None
        self.input_name = None
        self.session = None
        self.model_path = model_path
        self.window_size = None
        self.tensors_list = tensors_list
        self.prediction_list = prediction_list

    def clear_tensors(self):
        """
        Clear the list of tensors.
        """
        for _ in range(self.window_size):
            self.tensors_list.pop(0)

    def run(self):
        """
        Run the recognition model.
        """
        if self.session is None:
            sess_options = ort.SessionOptions()
            sess_options.log_severity_level = 3
            self.session = ort.InferenceSession(
                self.model_path,
                providers=["CUDAExecutionProvider"],
                sess_options=sess_options,
            )
            self.input_name = self.session.get_inputs()[0].name
            self.input_shape = self.session.get_inputs()[0].shape
            self.window_size = self.input_shape[3]
            self.output_names = [output.name for output in self.session.get_outputs()]

        if len(self.tensors_list) >= self.input_shape[3]:
            input_tensor = np.stack(self.tensors_list[: self.window_size], axis=1)[
                None
            ][None]
            st = time.time()
            outputs = self.session.run(
                self.output_names, {self.input_name: input_tensor.astype(np.float32)}
            )[0]
            et = round(time.time() - st, 3)
            gloss = str(classes[outputs.argmax()])
            if gloss != self.prediction_list[-1] and len(self.prediction_list):
                if gloss != "---":
                    self.prediction_list.append(gloss)
            self.clear_tensors()
            if self.verbose:
                logger.info(f"- Prediction time {et}, new gloss: {gloss}")
                logger.info(f" --- {len(self.tensors_list)} frames in queue")

    def kill(self):
        pass


class Recognition(BaseRecognition):
    def __init__(
        self, model_path: str, tensors_list: list, prediction_list: list, verbose: bool
    ):
        """
        Initialize recognition model.

        Parameters
        ----------
        model_path : str
            Path to the model.
        tensors_list : List
            List of tensors to be used for prediction.
        prediction_list : List
            List of predictions.

        Notes
        -----
        The recognition model is run in a separate process.
        """
        super().__init__(
            model_path=model_path,
            tensors_list=tensors_list,
            prediction_list=prediction_list,
            verbose=verbose,
        )
        self.started = True

    def start(self):
        self.run()


class RecognitionMP(Process, BaseRecognition):
    def __init__(self, model_path: str, tensors_list, prediction_list, verbose):
        """
        Initialize recognition model.

        Parameters
        ----------
        model_path : str
            Path to the model.
        tensors_list : Manager.list
            List of tensors to be used for prediction.
        prediction_list : Manager.list
            List of predictions.

        Notes
        -----
        The recognition model is run in a separate process.
        """
        super().__init__()
        BaseRecognition.__init__(
            self,
            model_path=model_path,
            tensors_list=tensors_list,
            prediction_list=prediction_list,
            verbose=verbose,
        )
        self.started = Value("i", False)

    def run(self):
        while True:
            BaseRecognition.run(self)
            self.started = True


class Runner:
    STACK_SIZE = 6

    def __init__(
        self,
        model_path: str,
        config: OmegaConf = None,
        mp: bool = False,
        verbose: bool = False,
        length: int = STACK_SIZE,
    ) -> None:
        """
        Initialize runner.

        Parameters
        ----------
        model_path : str
            Path to the model.
        config : OmegaConf
            Configuration file.
        length : int
            Deque length for predictions

        Notes
        -----
        The runner uses multiprocessing to run the recognition model in a separate process.

        """
        self.multiprocess = mp
        self.manager = Manager() if self.multiprocess else None
        self.tensors_list = self.manager.list() if self.multiprocess else []
        self.prediction_list = self.manager.list() if self.multiprocess else []
        self.prediction_list.append("---")
        self.frame_counter = 0
        self.frame_interval = config.frame_interval
        self.length = length
        self.prediction_classes = deque(maxlen=length)
        self.mean = config.mean
        self.std = config.std
        if self.multiprocess:
            self.recognizer = RecognitionMP(
                model_path, self.tensors_list, self.prediction_list, verbose
            )
        else:
            self.recognizer = Recognition(
                model_path, self.tensors_list, self.prediction_list, verbose
            )

    def add_frame(self, image):
        """
        Add frame to queue.

        Parameters
        ----------
        image : np.ndarray
            Frame to be added.
        """
        self.frame_counter += 1
        if self.frame_counter == self.frame_interval:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = self.resize(image, (224, 224))
            image = (image - self.mean) / self.std
            image = np.transpose(image, [2, 0, 1])
            self.tensors_list.append(image)
            self.frame_counter = 0

    @staticmethod
    def resize(im, new_shape=(224, 224)):
        """
        Resize and pad image while preserving aspect ratio.

        Parameters
        ----------
        im : np.ndarray
            Image to be resized.
        new_shape : Tuple[int]
            Size of the new image.

        Returns
        -------
        np.ndarray
            Resized image.
        """
        shape = im.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])

        # Compute padding
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

        dw /= 2
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(
            im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114)
        )  # add border
        return im

    def run(self, video_path: str):
        """
        Run the runner.

        Parameters
        ----------
        video_path : str
            Path to the video file.

        Notes
        -----
        The runner will run until the end of the video file or the user presses 'q'.
        """
        self.cap = cv2.VideoCapture(video_path)

        if self.multiprocess:
            self.recognizer.start()

        while self.cap.isOpened():
            if self.recognizer.started:
                ret, frame = self.cap.read()
                if not ret:
                    break
                self.add_frame(frame)

                if not self.multiprocess:
                    self.recognizer.start()

                if len(self.prediction_list) > self.length:
                    print(self.prediction_list.pop(0))

        self.cap.release()
        if self.multiprocess:
            self.recognizer.kill()

        # Print prediction list
        # print("Prediction List:", self.prediction_list)
        return self.prediction_list


def calculate_mean_class_accuracy(test_dir, annotations_file, conf):
    annotations = pd.read_csv(annotations_file, sep="\t")

    # Создание списка всех видеофайлов в папке test
    video_files = [f for f in os.listdir(test_dir) if f.endswith(".mp4")]

    true_labels = []
    predicted_labels = []
    count = 0
    corr_count = 0
    for video_file in video_files:
        video_path = os.path.join(test_dir, video_file)

        runner = Runner(conf.model_path, conf, length=5)
        predicted_label = runner.run(video_path)
        if count % 1 == 0:
            print(f"LOG: number of recognized videos: {count}")
        count += 1
        # if corr_count == 2:
        #     break
        if len(predicted_label) > 1:
            correct_predict = " ".join(predicted_label[1:])
        else:
            correct_predict = "no_event"

        true_label = annotations.loc[
            annotations["attachment_id"] == video_file[:-4], "text"
        ].values[0]
        if correct_predict == "no_event":
            continue
        corr_count += 1
        true_labels.append(true_label)
        predicted_labels.append(correct_predict)

    # print(f'True labels: {true_labels}')
    # print(f'Predicted: {predicted_labels}')

    classes = sorted(list(set(true_labels)))
    # num_classes = len(classes)

    # print(classes, num_classes)

    # cm = confusion_matrix(true_labels, predicted_labels, labels=classes)
    conf_matrix = confusion_matrix(
        y_pred=predicted_labels, y_true=true_labels, labels=classes
    )

    cls_cnt = conf_matrix.sum(axis=1)  # all labels
    cls_hit = np.diag(conf_matrix)  # true positives

    metrics = [hit / cnt if cnt else 0.0 for cnt, hit in zip(cls_cnt, cls_hit)]
    mean_class_acc = np.mean(metrics)

    return mean_class_acc


if __name__ == "__main__":
    conf = OmegaConf.load("config_example.yaml")
    test_dir = "test/"
    annotation_file = "annotations.csv"

    metric = calculate_mean_class_accuracy(test_dir, annotation_file, conf)
    print(metric)

    with open("metrics_resnet_i3d.txt", "w") as file1:
        # Writing data to a file
        file1.write(str(metric))
