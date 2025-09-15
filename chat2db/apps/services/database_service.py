from typing import Any, Type
from chat2db.apps.schemas.enum_var import DatabaseType
from chat2db.apps.base import MySQL, MongoDB, OpenGauss, Postgres, MetaDatabase

class DatabaseService:

    DatabaseMap: dict[DatabaseType, Type[MetaDatabase]] = {
        DatabaseType.MYSQL: MySQL,
        DatabaseType.MONGODB: MongoDB,
        DatabaseType.OPENGAUSS: OpenGauss,
        DatabaseType.POSTGRES: Postgres,
    }

    @staticmethod
    async def get_database_url(
        database_type: DatabaseType, host: str, port: int, username: str, password: str, database: str
    ):
        """
        根据数据库类型和连接信息生成数据库 URL。

        :return: 数据库连接 URL 字符串
        """
        db_class = DatabaseService.DatabaseMap[database_type]
        return await db_class.get_database_url(host, port, username, password, database)

    @staticmethod
    async def connect_database(
        database_type: DatabaseType, host: str, port: int, username: str, password: str, database: str
    ):
        """
        根据数据库类型和连接信息建立数据库连接。

        :return: 数据库连接对象
        """
        db_class = DatabaseService.DatabaseMap[database_type]
        return await db_class.connect(host, port, username, password, database)

    @staticmethod
    async def list_tables(database_type: DatabaseType, connection: Any) -> list[str]:
        """
        获取指定数据库中所有表名。

        :param database_type: 数据库类型枚举
        :param connection: 数据库连接对象
        :return: 表名列表
        """
        db_module = DatabaseService.DatabaseMap[database_type]
        return await db_module.list_tables(connection)

    @staticmethod
    async def get_table_ddl(database_type: DatabaseType, table_name: str, connection: Any) -> str:
        """
        获取指定表的建表语句 DDL。

        :param database_type: 数据库类型枚举
        :param table_name: 表名
        :param connection: 数据库连接对象

        :return: 表的 DDL 字符串
        """
        db_module = DatabaseService.DatabaseMap[database_type]
        return await db_module.get_table_ddl(table_name, connection)

    @staticmethod
    async def sample_table_rows(
        database_type: DatabaseType, table_name: str, num_rows: int, connection: Any
    ) -> list[dict]:
        """
        获取指定表的前 n 条示例数据。

        :param database_type: 数据库类型枚举
        :param table_name: 表名
        :param n: 返回的行数
        :param connection: 数据库连接对象

        :return: 示例行列表，每行为字典
        """
        db_module = DatabaseService.DatabaseMap[database_type]
        return await db_module.sample_table_rows(table_name, num_rows, connection)

    @staticmethod
    async def execute_sql(database_type: DatabaseType, sql: str | dict, connection: Any) -> list[dict]:
        """
        执行 SQL 语句或 MongoDB 指令。

        :param database_type: 数据库类型枚举
        :param sql: SQL 语句字符串（非 MongoDB）或 MongoDB dict 指令
        :param connection: 数据库连接对象

        :return: 执行结果列表，每条记录为字典
        """
        db_module = DatabaseService.DatabaseMap[database_type]
        return await db_module.execute_sql(sql, connection)


if __name__ == "__main__":
    import asyncio

    async def main():
        type = "mysql"
        conn = await DatabaseService.connect_database(
            type,
            host="localhost",
            port=3306,
            username="chat2db",
            password="123456",
            database="chat2db",
        )
        print("\n[Connection]\n:", conn)

        tables = await DatabaseService.list_tables(type, conn)
        print("\n[Tables]:\n", tables)

        ddl = await DatabaseService.get_table_ddl(type, tables[0], conn)
        print("\n[DDL]\n:", ddl)

        sql = "SELECT DISTINCT `TABLE_NAME` FROM `information_schema`.`TABLES` WHERE `TABLE_SCHEMA` = DATABASE();",
        execute_res = await DatabaseService.execute_sql(
            type,
            sql,
            conn,
        )
        print("\n[Execute]:\n", execute_res)

    asyncio.run(main())
