from typing import Any

class MetaDatabase:
    @staticmethod
    async def get_database_url(host: str, port: int, username: str, password: str, database: str):
        raise NotImplementedError

    @staticmethod
    async def connect(host: str, port: int, username: str, password: str, database: str) -> Any:
        raise NotImplementedError

    @staticmethod
    async def list_tables(connection: Any) -> list[str]:
        raise NotImplementedError

    @staticmethod
    async def get_table_ddl(table_name: str, connection: Any) -> str:
        raise NotImplementedError

    @staticmethod
    async def sample_table_rows(table_name: str, n: int, connection: Any) -> list[dict]:
        raise NotImplementedError

    @staticmethod
    async def execute_sql(sql: str | dict, connection: Any) -> list[dict]:
        raise NotImplementedError
