import os
from fastapi import File, UploadFile, Request, APIRouter
from pathlib import Path
from fastapi.responses import PlainTextResponse

from hse_slr.models.utils import make_prediction

CONFIG_PATH = Path(__file__).absolute().parent.parent.parent / 'hse_slr/models/configs/config.json'

router = APIRouter(
    prefix="/recognize",
    tags=["recognize"],
)


@router.post("/recognize")
async def recognize(request: Request, file: UploadFile = File(...)):

    file_path = Path("./uploads") / file.filename
    with file_path.open("wb") as buffer:
        buffer.write(await file.read())

    result = make_prediction(inference_thread=request.app.state.inference_thread, file_path=file_path)

    os.remove(file_path)
    return PlainTextResponse(content=result)
