import sqlalchemy
from testcontainers.postgres import PostgresContainer


class DatabaseContainer:
    def __init__(self):
        self._postgress_container = PostgresContainer("postgres:11")

    def start(self):
        self._postgress_container.start()

    def stop(self):
        self._postgress_container.stop()

    def create_database(self, dbname: str) -> str:
        connection_url = self._postgress_container.get_connection_url()
        engine = sqlalchemy.create_engine(connection_url)
        engine.execution_options(isolation_level="AUTOCOMMIT").execute(f"CREATE DATABASE {dbname};")

        return connection_url[:connection_url.rfind("/")] + '/' + dbname
