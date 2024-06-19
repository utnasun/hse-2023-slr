import os
from pathlib import Path

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import PlainTextResponse

from hse_slr.utils import make_prediction

CONFIG_PATH = (
    Path(__file__).absolute().parent.parent.parent
    / "hse_slr/models/configs/config.json"
)

router = APIRouter(
    prefix="/recognize",
    tags=["recognize"],
)


@router.post("/recognize")
async def recognize(request: Request, file: UploadFile = File(...)):

    file_path = Path("./") / file.filename

    with file_path.open("wb") as buffer:
        buffer.write(await file.read())

    result = make_prediction(file_path=str(file_path))

    os.remove(file_path)

    if len(result) == 1:
        return "Не смог распознать."

    return PlainTextResponse(content=' '.join(result[1:]))
