"""
Edited from https://github.com/daniel-code/TubeViT/blob/main/tubevit/dataset.py
"""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import pandas as pd
from torch import Tensor
from torchvision.datasets import UCF101
from torchvision.datasets.video_utils import VideoClips
from torchvision.datasets.vision import VisionDataset


class MyUCF101(UCF101):
    def __init__(self, transform: Optional[Callable] = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.transform = transform

    def __getitem__(self, idx: int) -> Tuple[Tensor, int]:
        video, audio, info, video_idx = self.video_clips.get_clip(idx)
        label = self.samples[self.indices[video_idx]][1]

        if self.transform is not None:
            video = self.transform(video)

        return video, label


class Slovo(VisionDataset):
    """

    To give an example, for 2 videos with 10 and 15 frames respectively, if ``frames_per_clip=5``
    and ``step_between_clips=5``, the dataset size will be (2 + 3) = 5, where the first two
    elements will come from video 1, and the next three elements from video 2.
    Note that we drop clips which do not have exactly ``frames_per_clip`` elements, so not all
    frames in a video might be present.

    Internally, it uses a VideoClips object to handle clip creation.

    Args:
        root (str or ``pathlib.Path``): Root directory of the Slovo Dataset.
        annotation_path (str): path to the folder containing the split files;
            see docstring above for download instructions of these files
        frames_per_clip (int): number of frames in a clip.
        step_between_clips (int, optional): number of frames between each clip.
        fold (int, optional): which fold to use. Should be between 1 and 3.
        train (bool, optional): if ``True``, creates a dataset from the train split,
            otherwise from the ``test`` split.
        transform (callable, optional): A function/transform that takes in a TxHxWxC video
            and returns a transformed version.
        output_format (str, optional): The format of the output video tensors (before transforms).
            Can be either "THWC" (default) or "TCHW".

    Returns:
        tuple: A 3-tuple with the following entries:

            - video (Tensor[T, H, W, C] or Tensor[T, C, H, W]): The `T` video frames
            -  audio(Tensor[K, L]): the audio frames, where `K` is the number of channels
               and `L` is the number of points
            - label (int): class of the video clip
    """

    def __init__(
        self,
        root: Union[str, Path],
        annotation_path: str,
        frames_per_clip: int,
        step_between_clips: int = 1,
        frame_rate: Optional[int] = None,
        fold: int = 1,
        train: bool = True,
        transform: Optional[Callable] = None,
        _precomputed_metadata: Optional[Dict[str, Any]] = None,
        num_workers: int = 1,
        _video_width: int = 0,
        _video_height: int = 0,
        _video_min_dimension: int = 0,
        _audio_samples: int = 0,
        output_format: str = "THWC",
    ) -> None:
        super().__init__(root)
        if not 1 <= fold <= 3:
            raise ValueError(f"fold should be between 1 and 3, got {fold}")

        extensions = (".mp4",)

        self.fold = fold
        self.train = train

        if self.train:
            task_type = "train"
        else:
            task_type = "test"

        annotations = (
            pd.read_csv(root + "raw/annotations.csv", sep="\t")
            .query('text != "no_event"')
            .query("train == @train")
        )

        self.classes = annotations.text.unique().tolist()

        class_to_idx = {cls_name: i for i, cls_name in enumerate(self.classes)}

        self.samples = [
            (row.path, class_to_idx[row.text])
            for row in (
                annotations[["attachment_id", "text"]]
                .assign(
                    path=lambda df: root
                    + f"raw/{task_type}/"
                    + df["attachment_id"]
                    + extensions[0]
                )[["attachment_id", "text", "path"]]
                .itertuples()
            )
        ]

        video_list = [x[0] for x in self.samples]
        video_clips = VideoClips(
            video_list,
            frames_per_clip,
            step_between_clips,
            frame_rate,
            _precomputed_metadata,
            num_workers=num_workers,
            _video_width=_video_width,
            _video_height=_video_height,
            _video_min_dimension=_video_min_dimension,
            _audio_samples=_audio_samples,
            output_format=output_format,
        )

        # we bookkeep the full version of video clips because we want to be able
        # to return the metadata of full version rather than the subset version of
        # video clips
        self.full_video_clips = video_clips
        self.indices = self._select_fold(video_list, annotation_path, fold, train)
        self.video_clips = video_clips.subset(self.indices)
        self.transform = transform

    @property
    def metadata(self) -> Dict[str, Any]:
        return self.full_video_clips.metadata

    def _select_fold(
        self, video_list: List[str], annotation_path: str, fold: int, train: bool
    ) -> List[int]:
        # name = "train" if train else "test"
        # name = f"{name}list{fold:02d}.txt"
        # f = os.path.join(annotation_path, name)
        # selected_files = set()
        # with open(f) as fid:
        #     data = fid.readlines()
        #     data = [x.strip().split(" ")[0] for x in data]
        #     data = [os.path.join(self.root, *x.split("/")) for x in data]
        #     selected_files.update(data)
        indices = [
            i
            for i in range(len(video_list))
            # if video_list[i] in selected_files
        ]

        return indices

    def __len__(self) -> int:
        return self.video_clips.num_clips()

    def __getitem__(self, idx: int) -> Tuple[Tensor, Tensor, int]:
        video, audio, info, video_idx = self.video_clips.get_clip(idx)
        label = self.samples[self.indices[video_idx]][1]

        if self.transform is not None:
            video = self.transform(video)

        return video, label


# slovo = Slovo(
#     root='/Users/lmruwork/Desktop/Education/Masters/hse-2023-slr/data/',
#     annotation_path='1221312',
#     frames_per_clip=2,
#     num_workers=11,
#     output_format="THWC",
#     train=False
# )
