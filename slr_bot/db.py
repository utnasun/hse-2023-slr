import os

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, URL,
    Table, MetaData,
    insert
)

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

stmnt = (
    insert(bot_requests_table)
    .values(id=1, user_id=1)
)

with engine.connect() as conn:
    result = conn.execute(stmnt)
    conn.commit()
