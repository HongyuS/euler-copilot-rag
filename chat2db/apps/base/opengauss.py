import logging
import asyncpg
from typing import Any
from apps.base.database_base import MetaDatabase

class OpenGauss(MetaDatabase):

    @staticmethod
    async def get_database_url(host: str, port: int, username: str, password: str, database: str):
        try:
            return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
        except Exception as e:
            logging.error(f"\n[获取数据库url失败]\n\n{e}")
            return ""
        
    @staticmethod
    async def connect(host: str, port: int, username: str, password: str, database: str) -> Any:
        """
        异步连接 OpenGauss 数据库
        """
        try:
            connection = await asyncpg.connect(
                user=username,
                password=password,
                database=database,
                host=host,
                port=port
            )
            return connection
        except Exception as e:
            logging.error(f"\n[连接OpenGauss数据库失败]\n\n{e}")
            raise e

    @staticmethod
    async def list_tables(connection: Any) -> list[str]:
        """
        获取数据库中的所有表名
        """
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        try:
            tables = await connection.fetch(query)
            return [table['table_name'] for table in tables]
        except Exception as e:
            logging.error(f"\n[获取表名失败]\n\n{e}")
            raise e

    @staticmethod
    async def get_table_ddl(table_name: str, connection: Any) -> str:
        """
        获取指定表的 DDL（建表语句）
        """
        try:
            # OpenGauss/Postgres 可以使用 pg_get_tabledef 获取 DDL
            sql = f"SELECT pg_get_tabledef('{table_name}'::regclass);"
            ddl = await connection.fetchval(sql)
            return ddl or ""
        except Exception as e:
            logging.error(f"\n[获取表 {table_name} DDL失败]\n\n{e}")
            raise e

    @staticmethod
    async def sample_table_rows(table_name: str, num_rows: int, connection: Any) -> list[dict]:
        """
        随机获取表中 n 条数据
        """
        try:
            sql = f"SELECT * FROM {table_name} ORDER BY random() LIMIT {num_rows};"
            rows = await connection.fetch(sql)
            return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"\n[获取表 {table_name} 样本数据失败]\n\n{e}")
            raise e

    @staticmethod
    async def execute_sql(sql: str, connection: Any) -> list[dict]:
        """
        异步执行 SQL, 自动返回查询结果或原始输出。

        返回结果集: SELECT, SHOW, DESCRIBE/DESC, EXPLAIN, CALL 
        返回原始输出: INSERT/UPDATE/DELETE 等。
        """
        try:
            async with connection.transaction():

                sql_type = sql.strip().split()[0].upper()
                # 返回结果集的语句类型
                result_set_statements = {"SELECT", "SHOW", "DESCRIBE", "DESC", "EXPLAIN", "CALL"}

                if sql_type in result_set_statements:
                    rows = await connection.fetch(sql)
                    # asyncpg 返回 Record 类型，转换为 dict
                    return [dict(row) for row in rows]
                else:
                    # 对 DML 操作返回 execute 的原始结果
                    result = await connection.execute(sql)
                    return [{'result': result}]
        except Exception as e:
            logging.error(f"\n[执行OpenGauss SQL失败]\n\n{e}")
            raise e
