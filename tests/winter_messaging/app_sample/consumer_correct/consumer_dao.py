from injector import inject
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.engine import Engine

metadata = MetaData()
consumer_table = Table(
    'sample_messaging_consumers',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
)


class ConsumerDAO:
    @inject
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def get_by_id(self, id_: int):
        return 123

    def save(self, id: int, name: str):
        return 123