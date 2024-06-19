import os
import pickle

import lightning.pytorch as pl
import matplotlib.pyplot as plt
import numpy as np
from lightning.pytorch.loggers import TensorBoardLogger
from pytorchvideo.transforms import Normalize, Permute, RandAugment
from torch import Tensor, nn
from torch.utils.data import DataLoader
from torchvision.transforms import transforms as T
from torchvision.transforms._transforms_video import ToTensorVideo

from tubevit.dataset import Slovo
from tubevit.model import TubeViTLightningModule


def main(
    dataset_root,
    annotation_path,
    num_classes=101,
    batch_size=32,
    frames_per_clip=32,
    video_size=(224, 224),
    max_epochs=2,
    num_workers=0,
    fast_dev_run=False,
    seed=42,
    preview_video=False,
):
    pl.seed_everything(seed)

    imagenet_mean = [0.485, 0.456, 0.406]
    imagenet_std = [0.229, 0.224, 0.225]

    train_transform = T.Compose(
        [
            ToTensorVideo(),  # C, T, H, W
            Permute(dims=[1, 0, 2, 3]),  # T, C, H, W
            RandAugment(magnitude=10, num_layers=2),
            Permute(dims=[1, 0, 2, 3]),  # C, T, H, W
            T.Resize(size=video_size),
            Normalize(mean=imagenet_mean, std=imagenet_std),
        ]
    )

    test_transform = T.Compose(
        [
            ToTensorVideo(),
            T.Resize(size=video_size),
            Normalize(mean=imagenet_mean, std=imagenet_std),
        ]
    )

    train_metadata_file = "slovo-train-meta.pickle"
    train_precomputed_metadata = None
    if os.path.exists(train_metadata_file):
        with open(train_metadata_file, "rb") as f:
            train_precomputed_metadata = pickle.load(f)

    train_set = Slovo(
        root="/root/work/data/videos/",
        annotation_path=annotation_path,
        _precomputed_metadata=train_precomputed_metadata,
        frames_per_clip=frames_per_clip,
        train=True,
        output_format="THWC",
        transform=train_transform,
        num_workers=0,
    )

    if not os.path.exists(train_metadata_file):
        with open(train_metadata_file, "wb") as f:
            pickle.dump(train_set.metadata, f, protocol=pickle.HIGHEST_PROTOCOL)

    val_metadata_file = "slovo-val-meta.pickle"
    val_precomputed_metadata = None
    if os.path.exists(val_metadata_file):
        with open(val_metadata_file, "rb") as f:
            val_precomputed_metadata = pickle.load(f)

    val_set = Slovo(
        root="/root/work/data/videos/",
        annotation_path=annotation_path,
        _precomputed_metadata=val_precomputed_metadata,
        frames_per_clip=frames_per_clip,
        train=False,
        output_format="THWC",
        transform=test_transform,
        num_workers=0,
    )

    if not os.path.exists(val_metadata_file):
        with open(val_metadata_file, "wb") as f:
            pickle.dump(val_set.metadata, f, protocol=pickle.HIGHEST_PROTOCOL)

    train_dataloader = DataLoader(
        train_set,
        batch_size=batch_size,
        num_workers=num_workers,
        shuffle=True,
        drop_last=True,
        pin_memory=True,
    )

    val_dataloader = DataLoader(
        val_set,
        batch_size=batch_size,
        num_workers=num_workers,
        shuffle=False,
        drop_last=True,
        pin_memory=True,
    )

    x, y = next(iter(train_dataloader))
    print(x.shape)

    if preview_video:
        x = x.permute(0, 2, 3, 4, 1)
        fig, axs = plt.subplots(4, 8)
        for i in range(4):
            for j in range(8):
                axs[i][j].imshow(x[0][i * 8 + j])
                axs[i][j].set_xticks([])
                axs[i][j].set_yticks([])
        plt.tight_layout()
        plt.show()

    size = np.random.random((1, 3, frames_per_clip, video_size[0], video_size[1]))
    size = Tensor(size)

    model = TubeViTLightningModule(
        num_classes=num_classes,
        video_shape=size.shape[1:],
        num_layers=12,
        num_heads=12,
        hidden_dim=768,
        mlp_dim=3072,
        lr=1e-4,
        weight_decay=0.001,
        weight_path="/root/work/tubevit_b_(a+iv)+(d+v)+(e+iv)+(f+v).pt",
        max_epochs=max_epochs,
    )

    for param in model.model.parameters():
        param.requires_grad = False

    model.model.heads.head = nn.Linear(model.model.heads.head.in_features, 1000)
    model.num_classes = 1000

    nn.init.xavier_uniform_(model.model.heads.head.weight)

    callbacks = [pl.callbacks.LearningRateMonitor(logging_interval="epoch")]
    logger = TensorBoardLogger("logs", name="TubeViT")

    trainer = pl.Trainer(
        max_epochs=max_epochs,
        accelerator="auto",
        fast_dev_run=fast_dev_run,
        logger=logger,
        callbacks=callbacks,
    )
    trainer.fit(
        model, train_dataloaders=train_dataloader, val_dataloaders=val_dataloader
    )
    trainer.save_checkpoint("./models/tubevit_slovo.ckpt")


if __name__ == "__main__":
    main("just", "for fun")
