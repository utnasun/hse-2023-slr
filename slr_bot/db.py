import os

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, URL,
    Table, MetaData,
    insert,
    func,
    select
)
from sqlalchemy.dialects.postgresql import insert as pg_insert

load_dotenv(Path(__file__).parent / '.env')

url_object = URL.create(
    "postgresql+psycopg2",
    host=os.environ['DB_HOST'],
    port=os.environ['DB_PORT'],
    database=os.environ['DB_NAME'],
    username=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
)

engine = create_engine(url_object)

bot_requests_table = Table(
    'bot_requests',
    MetaData(schema='public'),
    autoload_with=engine
)

bot_reviews_table = Table(
    'bot_reviews',
    MetaData(schema='public'),
    autoload_with=engine
)

bot_users_table = Table(
    'bot_users',
    MetaData(schema='public'),
    autoload_with=engine
)
def upsert_review(user_id, mark, date, timestamp):
    stmnt = pg_insert(bot_reviews_table).values(
        user_id=user_id, mark=mark, date=date, timestamp=timestamp
    ).on_conflict_do_update(
        index_elements=['user_id'],
        set_={"mark": mark, "date": date, "timestamp": timestamp}
    )

    with engine.connect() as conn:
        result = conn.execute(stmnt)
        conn.commit()

def get_average_mark():
    with engine.connect() as conn:
        query = select(func.round(func.avg(bot_reviews_table.c.mark), 2)) 
        result = conn.execute(query).fetchall()[0][0]

        return result

if __name__ == "__main__":
    print(get_average_mark())
