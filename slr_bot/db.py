import os

from pathlib import Path
from typing import Any, List, Optional, Union
from dotenv import load_dotenv

from sqlalchemy.engine.mock import MockConnection
from sqlalchemy.engine import url as _url
from sqlalchemy import Executable, util
from sqlalchemy.engine.interfaces import _CoreAnyExecuteParams
from sqlalchemy.engine.interfaces import CoreExecuteOptionsParameter

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

if os.environ.get('BOT_ENV', 'test') == 'prod':

    url_object = URL.create(
        "postgresql+psycopg2",
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        database=os.environ['DB_NAME'],
        username=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
    )

    engine = create_engine(url_object)

elif os.environ.get('BOT_ENV') == 'test':

    class MockConnectionExtended(MockConnection):

        def __enter__(self):
            return self

        def __exit__(self, exception_type, exception_value, traceback):
            return self

        def commit(self):
            return self

        def execute(
            self,
            obj: Executable,
            parameters: Optional[_CoreAnyExecuteParams] = None,
            execution_options: Optional[CoreExecuteOptionsParameter] = None,
        ) -> Any:
            self.obj = obj
            return super().execute(obj, parameters, execution_options)

    def create_mock_engine(
        url: Union[str, URL],
        executor: Any,
        mock_connection: MockConnection,
        **kw: Any
    ) -> MockConnection:

        # create url.URL object
        u = _url.make_url(url)

        dialect_cls = u.get_dialect()

        dialect_args = {}
        # consume dialect arguments from kwargs
        for k in util.get_cls_kwargs(dialect_cls):
            if k in kw:
                dialect_args[k] = kw.pop(k)

        # create dialect
        dialect = dialect_cls(**dialect_args)

        return mock_connection(dialect, executor)

    class MockFetch:

        def __init__(self, sql) -> None:
            self.sql = sql

        def fetchall(self) -> List[List]:
            columns = len(self.sql.selected_columns.keys())
            return [[*range(columns)]]

        def scalar_one(self):
            return 1

    def fetch_range_row(sql, *multiparams, **params):
        print(sql.compile(dialect=engine.dialect))
        return MockFetch(sql)

    engine = create_mock_engine(
        'postgresql+psycopg2://',
        fetch_range_row,
        MockConnectionExtended
    )

else:

    raise KeyError('BOT_ENV environment variable must be set to prod or test.')


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

meta.create_all(bind=engine)


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
