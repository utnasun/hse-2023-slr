import pandas as pd

from fastapi import Response, APIRouter
from fastapi.responses import JSONResponse

from slr_bot.db import engine, app_users_table
from sqlalchemy import select, func

router = APIRouter(
    prefix="/activity",
    tags=["activity"],
)


@router.get('/unique_users')
def get_num_unique_users():

    num_unique_users_statement = (
        select(func.count(app_users_table.c.user_id))
    )

    with engine.connect() as conn:
        num_unique_users = conn.execute(num_unique_users_statement).scalar_one()

    return JSONResponse(
        {'Количество уникальных пользователей': num_unique_users},
        media_type='application/json; charset=utf-8'
    )


@router.get('/new_users_by_dow')
def get_new_users_by_dow_count():

    extract_dow_func = func.extract('isodow', app_users_table.c.init_dttm)

    new_users_by_dow_count_statement = (
        select(
            extract_dow_func.label('День недели'),
            func.count(app_users_table.c.user_id).label('Количество'))
        .group_by(extract_dow_func)
        .order_by(extract_dow_func)
    )

    with engine.connect() as conn:
        new_users_by_dow = conn.execute(new_users_by_dow_count_statement)
        conn.commit()

    columns = new_users_by_dow_count_statement.selected_columns.keys()
    rows = new_users_by_dow.fetchall()

    new_users_by_dow_table = pd.DataFrame(
        data=rows,
        columns=columns
    )

    return Response(
        new_users_by_dow_table.to_json(orient='records', force_ascii=False),
        media_type='application/json; charset=utf-8'
    )
