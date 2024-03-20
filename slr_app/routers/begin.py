from fastapi import APIRouter, Response, Request

from slr_bot.db import engine, app_users_table
from sqlalchemy.dialects.postgresql import insert as pg_insert
from datetime import datetime


router = APIRouter(
    tags=["register"]
)


@router.get('/')
def begin(response: Response, request: Request):

    if not request.cookies.get('_is_registed'):
        insert_user = (
            pg_insert(app_users_table)
            .values(init_dttm=datetime.now())
        )

        with engine.connect() as conn:
            conn.execute(insert_user)
            conn.commit()

        response.set_cookie('_is_registed', True)

        return "Successfully started a session"

    return "Already started a session"
