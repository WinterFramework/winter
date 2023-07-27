import sqlalchemy
from testcontainers.postgres import PostgresContainer


class DatabaseContainer:
    def __init__(self):
        self._postgress_container = PostgresContainer("postgres:11")
        self._container_started = False

    def start_container(self):
        if not self._container_started:
            self._postgress_container.start()
            self._container_started = True

    def stop_container(self):
        if self._container_started:
            self._postgress_container.stop()
            self._container_started = False

    def create_database(self, dbname: str) -> str:
        self.start_container()
        connection_url = self._postgress_container.get_connection_url()
        engine = sqlalchemy.create_engine(connection_url)
        engine.execution_options(isolation_level="AUTOCOMMIT").execute(f"CREATE DATABASE {dbname};")

        return connection_url[:connection_url.rfind("/")] + '/' + dbname


database_container = DatabaseContainer()
