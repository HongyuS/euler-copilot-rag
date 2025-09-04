import logging
from typing import Any
import aiomysql
import urllib.parse

from apps.base.database_base import MetaDatabase

class MySQL(MetaDatabase):
    @staticmethod
    async def get_database_url(host: str, port: int, username: str, password: str, database: str):
        try:
            user = urllib.parse.quote_plus(username)
            pwd = urllib.parse.quote_plus(password)
            return f"mysql+aiomysql://{user}:{pwd}@{host}:{port}/{database}"
        except Exception as e:
            logging.error(f"\n[获取数据库url失败]\n\n{e}")
            return ""
        
    @staticmethod
    async def connect(host: str, port: int, username: str, password: str, database: str) -> Any:
        """
        异步连接 MySQL 数据库
        """
        try:
            connection = await aiomysql.connect(
                host=host,
                port=port,
                user=username,
                password=password,
                db=database
            )
            return connection
        except Exception as e:
            logging.error(f"\n[连接MySQL数据库失败]\n\n{e}")
            raise e

    @staticmethod
    async def list_tables(connection: Any) -> list[str]:
        """
        获取数据库中所有表名
        """
        try:
            async with connection.cursor() as cursor:
                await cursor.execute("SHOW TABLES")
                tables = [table[0] for table in await cursor.fetchall()]
            return tables
        except Exception as e:
            logging.error(f"\n[获取表名失败]\n\n{e}")
            raise e

    @staticmethod
    async def get_table_ddl(table_name: str, connection: Any) -> str:
        """
        获取指定表的 DDL（建表语句）
        """
        try:
            async with connection.cursor() as cursor:
                await cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
                result = await cursor.fetchone()
                return result[1] if result else ""
        except Exception as e:
            logging.error(f"\n[获取表 {table_name} DDL失败]\n\n{e}")
            raise e

    @staticmethod
    async def sample_table_rows(table_name: str, n: int, connection: Any) -> list[dict]:
        """
        随机获取表中 n 条数据
        """
        try:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(f"SELECT * FROM `{table_name}` ORDER BY RAND() LIMIT {n}")
                rows = await cursor.fetchall()
                return rows
        except Exception as e:
            logging.error(f"\n[获取表 {table_name} 样本数据失败]\n\n{e}")
            raise e

    @staticmethod
    async def execute_sql(sql: str, connection: Any) -> list[dict]:
        """
        异步执行 SQL, 自动返回查询结果或影响行数。

        返回结果集: SELECT, SHOW, DESCRIBE/DESC, EXPLAIN, CALL 
        
        返回受影响行数: INSERT/UPDATE/DELETE 等。
        """
        try:
            async with connection.cursor(aiomysql.DictCursor) as cursor:
                result = await cursor.execute(sql)
                await connection.commit()
                
                # 针对返回结果集的操作
                if sql.strip().upper().startswith(("SELECT", "SHOW", "DESCRIBE", "DESC", "EXPLAIN")):
                    rows = await cursor.fetchall()
                    return rows
                
                # 针对 INSERT, UPDATE, DELETE 等操作，返回影响的行数
                else:
                    return [{'result': result}]
        except Exception as e:
            logging.error(f"\n[执行SQL失败]\n\n{e}")
            raise e
