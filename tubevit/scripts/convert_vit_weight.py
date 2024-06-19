"""
Source code link https://github.com/daniel-code/TubeViT/blob/main/scripts/convert_vit_weight.py
"""
import click
import torch
from torch.nn import functional as F
from torchvision.models import ViT_B_16_Weights

from tubevit.model import TubeViTLightningModule


@click.command()
@click.option(
    "-nc", "--num-classes", type=int, default=1000, help="num of classes of dataset."
)
@click.option("-f", "--frames-per-clip", type=int, default=32, help="frame per clip.")
@click.option(
    "-v",
    "--video-size",
    type=click.Tuple([int, int]),
    default=(224, 224),
    help="frame per clip.",
)
@click.option(
    "-o",
    "--output-path",
    type=click.Path(),
    default="tubevit_b_(a+iv)+(d+v)+(e+iv)+(f+v).pt",
    help="output model weight name.",
)
def main(num_classes, frames_per_clip, video_size, output_path):
    model = TubeViTLightningModule.load_from_checkpoint(
        "/root/work/tubevit_ucf101_new.ckpt"
    )

    # print(model)

    # model = TubeViT(
    #     num_classes=num_classes,
    #     video_shape=x.shape[1:],
    #     num_layers=12,
    #     num_heads=12,
    #     hidden_dim=768,
    #     mlp_dim=3072,
    # )

    weights = ViT_B_16_Weights.DEFAULT.get_state_dict(progress=True)

    # inflated vit path convolution layer weight
    conv_proj_weight = weights["conv_proj.weight"]
    conv_proj_weight = F.interpolate(conv_proj_weight, (8, 8), mode="bilinear")
    conv_proj_weight = torch.unsqueeze(conv_proj_weight, dim=2)
    conv_proj_weight = conv_proj_weight.repeat(1, 1, 8, 1, 1)
    conv_proj_weight = conv_proj_weight / 8.0

    # remove missmatch parameters
    weights.pop("encoder.pos_embedding")
    weights.pop("heads.head.weight")
    weights.pop("heads.head.bias")

    model.model.load_state_dict(weights, strict=False)
    model.model.sparse_tubes_tokenizer.conv_proj_weight = torch.nn.Parameter(
        conv_proj_weight, requires_grad=True
    )

    torch.save(model.model.state_dict(), output_path)


if __name__ == "__main__":
    main()
