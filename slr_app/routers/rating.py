import re
from sqlalchemy import select, func
from datetime import datetime, date
from fastapi import APIRouter, Response, Request
from fastapi.responses import JSONResponse

from slr_bot.db import app_upsert_review, engine, app_reviews_table

router = APIRouter(
    prefix="/rating",
    tags=["rating"],
)


@router.post('/make_review/{mark}')
def make_review(response: Response, mark: int, request: Request):
    if user_id := request.cookies.get('user_id'):
        app_upsert_review(re.search(r"\((\d+),\)", user_id).group(1), mark, date.today(), datetime.now())
        return "Successfully made mark"

    return "Go to / and try again"


@router.get('/get_rating')
def get_average_rating():

    with engine.connect() as conn:
        query = select(func.round(func.avg(app_reviews_table.c.mark), 2))
        mark = conn.execute(query).fetchall()[0][0]

    return JSONResponse(
        {'Средняя оценка приложения': float(mark)},
        media_type='application/json; charset=utf-8'
    )
