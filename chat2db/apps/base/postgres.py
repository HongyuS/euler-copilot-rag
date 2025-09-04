import logging
import asyncpg
from typing import Any
from apps.base.database_base import MetaDatabase


class Postgres(MetaDatabase):

    @staticmethod
    async def get_database_url(host: str, port: int, username: str, password: str, database: str):
        try:
            url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            return url
        except Exception as e:
            logging.error(f"\n[获取数据库url失败]\n\n{e}")
            return ""

    @staticmethod
    async def connect(host: str, port: int, username: str, password: str, database: str) -> Any:
        """
        异步连接 PostgreSQL 数据库
        """
        try:
            connection = await asyncpg.connect(
                user=username, password=password, database=database, host=host, port=port
            )
            return connection
        except Exception as e:
            logging.error(f"\n[连接PostgreSQL数据库失败]\n\n{e}")
            raise e

    @staticmethod
    async def list_tables(connection: Any) -> list[str]:
        """
        获取数据库中所有表名
        """
        try:
            tables = await connection.fetch(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
            )
            return [table["table_name"] for table in tables]
        except Exception as e:
            logging.error(f"\n[获取表名失败]\n\n{e}")
            raise e

    @staticmethod
    async def get_table_ddl(table_name: str, connection: Any) -> str:
        try:
            sql = f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
            """
            rows = await connection.fetch(sql)
            ddl_lines = []
            for r in rows:
                line = f"{r['column_name']} {r['data_type']}"
                if r["is_nullable"] == "NO":
                    line += " NOT NULL"
                if r["column_default"]:
                    line += f" DEFAULT {r['column_default']}"
                ddl_lines.append(line)
            ddl = f"CREATE TABLE {table_name} (\n  " + ",\n  ".join(ddl_lines) + "\n);"
            return ddl

        except Exception as e:
            logging.error(f"\n[获取表 {table_name} DDL失败]\n\n{e}")
            raise e

    @staticmethod
    async def sample_table_rows(table_name: str, n: int, connection: Any) -> list[dict]:
        try:
            sql = f"SELECT * FROM {table_name} ORDER BY random() LIMIT {n};"
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
                # 获取 SQL 类型
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
                    return [{"result": result}]
        except Exception as e:
            logging.error(f"\n[执行PostgreSQL SQL失败]\n\n{e}")
            raise e
