from sqlalchemy import URL

from sqlalchemy.engine.mock import MockConnection
from sqlalchemy import Executable, util
from sqlalchemy.engine.interfaces import _CoreAnyExecuteParams
from sqlalchemy.engine.interfaces import CoreExecuteOptionsParameter
from sqlalchemy.engine import url as _url

from typing import Any, List, Optional, Union


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
