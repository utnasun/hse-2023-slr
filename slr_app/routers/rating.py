import re
from datetime import date, datetime

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from fastapi_cache.decorator import cache
from sqlalchemy import func, select

from slr_bot.db import app_reviews_table, app_upsert_review, engine
from slr_bot import session

router = APIRouter(
    prefix="/rating",
    tags=["rating"],
)


@router.post("/make_review/{mark}")
def make_review(response: Response, mark: int, request: Request):
    if user_id := request.cookies.get("user_id"):
        app_upsert_review(
            re.search(r"\((\d+),\)", user_id).group(1),
            mark,
            date.today(),
            datetime.now(),
        )
        return "Successfully made mark"

    return "Go to / and try again"


@router.get("/get_rating")
@cache(expire=30)
def get_average_rating():
    with engine.connect() as conn:
        query = select(func.round(func.avg(app_reviews_table.c.mark), 2))
        mark = conn.execute(query).fetchall()[0][0]

    return JSONResponse(
        {"Средняя оценка приложения": float(mark)},
        media_type="application/json; charset=utf-8",
    )
