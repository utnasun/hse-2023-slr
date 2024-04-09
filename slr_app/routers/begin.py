from datetime import datetime

from fastapi import APIRouter, Request, Response
from sqlalchemy.dialects.postgresql import insert as pg_insert

from slr_bot.db import app_users_table, engine

router = APIRouter(tags=["register"])


@router.get("/")
def begin(response: Response, request: Request):
    if not request.cookies.get("_is_registed"):
        insert_user = pg_insert(app_users_table).values(init_dttm=datetime.now())

        with engine.connect() as conn:
            result = conn.execute(insert_user)
            conn.commit()

        response.set_cookie("_is_registed", True)
        response.set_cookie("user_id", result.inserted_primary_key)

        return "Successfully started a session"

    return "Already started a session"
