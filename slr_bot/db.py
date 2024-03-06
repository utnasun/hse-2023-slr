import os

from pathlib import Path
from dotenv import load_dotenv

from sqlalchemy import (
    create_engine, URL,
    Table, MetaData,
    func,
    Column,
    Integer,
    DateTime,
    PrimaryKeyConstraint,
    UniqueConstraint,
    String,
    Date,
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

meta = MetaData(schema='public')

bot_requests_table = Table(
    'bot_requests',
    meta,
    Column('user_id', Integer, nullable=False),
    Column('init_dttm', DateTime, default=func.now()),
    PrimaryKeyConstraint('user_id', name='bot_requests_pkey')
)

bot_reviews_table = Table(
    'bot_reviews',
    meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', String, nullable=True),
    Column('mark', Integer, nullable=True),
    Column('date', Date, nullable=True),
    Column('timestamp', DateTime, nullable=True, default=func.now()),
    UniqueConstraint('user_id', name='bot_reviews_un')
)

bot_users_table = Table(
    'bot_users',
    meta,
    Column('user_id', Integer, nullable=False),
    Column('init_dttm', DateTime, default=func.now(), nullable=True),
    PrimaryKeyConstraint('user_id', name='bot_users_pkey')
)


def upsert_review(user_id, mark, date, timestamp):
    stmnt = pg_insert(bot_reviews_table).values(
        user_id=user_id, mark=mark, date=date, timestamp=timestamp
    ).on_conflict_do_update(
        index_elements=['user_id'],
        set_={"mark": mark, "date": date, "timestamp": timestamp}
    )

    with engine.connect() as conn:
        conn.execute(stmnt)
        conn.commit()
