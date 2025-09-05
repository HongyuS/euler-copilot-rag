import logging
from typing import Any
from bson import ObjectId
from copy import deepcopy
import motor.motor_asyncio
import urllib.parse

from apps.base.database_base import MetaDatabase

class MongoDB(MetaDatabase):

    @staticmethod
    async def get_database_url(host: str, port: int, username: str, password: str, database: str):
        try:
            user = urllib.parse.quote_plus(username)
            pwd = urllib.parse.quote_plus(password)
            return f"mongodb://{user}:{pwd}@{host}:{port}/{database}"
        except Exception as e:
            logging.error(f"\n[获取数据库url失败]\n\n{e}")
            return ""

    @staticmethod
    async def connect(host: str, port: int, username: str, password: str, database: str) -> Any:
        try:
            user = urllib.parse.quote_plus(username)
            pwd = urllib.parse.quote_plus(password)
            mongo_uri = f"mongodb://{user}:{pwd}@{host}:{port}/{database}"
            client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
            return client[database]
        except Exception as e:
            logging.error(f"\n[连接MongoDB数据库失败]\n\n{e}")
            raise e

    @staticmethod
    async def list_tables(connection: Any) -> list[str]:
        try:
            return await connection.list_collection_names()
        except Exception as e:
            logging.error(f"\n[获取集合失败]\n\n{e}")
            raise e

    @staticmethod
    async def get_table_ddl(table_name: str, connection: Any) -> str:
        """
        将 MongoDB 集合信息格式化为类似 SQL DDL 的文本，用于大模型输入。
        包括索引信息和部分示例字段。
        """
        try:
            # 获取索引信息
            indexes = await connection[table_name].index_information()
            
            # 尝试获取部分文档字段类型
            sample_doc = await connection[table_name].find_one() or {}
            fields_ddl = []
            for field, value in sample_doc.items():
                dtype = type(value).__name__
                fields_ddl.append(f"    {field} {dtype.upper()}")

            # 格式化索引信息
            indexes_ddl = []
            for index_name, index_info in indexes.items():
                keys = ", ".join([f"{k[0]}({k[1]})" for k in index_info['key']])
                unique = " UNIQUE" if index_info.get('unique') else ""
                indexes_ddl.append(f"    INDEX {index_name} ON ({keys}){unique}")

            ddl = f"CREATE COLLECTION {table_name} (\n"
            ddl += ",\n".join(fields_ddl)
            ddl += "\n);\n"
            if indexes_ddl:
                ddl += "\n".join(indexes_ddl)

            return ddl

        except Exception as e:
            logging.error(f"\n[获取集合 {table_name} DDL失败]\n\n{e}")
            raise e

    @staticmethod
    async def sample_table_rows(table_name: str, n: int, connection: Any) -> list[dict]:
        """
        随机获取 n 条数据
        """
        try:
            cursor = connection[table_name].aggregate([{"$sample": {"size": n}}])
            result = [doc async for doc in cursor]
            return result
        except Exception as e:
            logging.error(f"\n[获取集合 {table_name} 样本数据失败]\n\n{e}")
            raise e

    @staticmethod
    async def execute_sql(sql: dict, connection: Any) -> list[dict]:
        """
        执行 MongoDB 操作，传入 dict 格式指令
        支持 find/insertOne/insertMany/updateOne/updateMany/deleteOne/deleteMany/aggregate
        返回值中所有 ObjectId 自动转换为 str
        """
        command = deepcopy(sql) # mongodb会修改输入的dict，所以这里需要深拷贝
        try:
            coll_name = command.get("collection")
            operation = command.get("operation", "find")
            filter_ = command.get("filter", {})
            data = command.get("data", {})
            pipeline = command.get("pipeline", [])
            many = command.get("many", False)

            collection = connection[coll_name]

            # 查询
            if operation == "find":
                cursor = collection.find(filter_)
                result = [doc async for doc in cursor]
                return MongoDB.transform_objectid(result)

            # 聚合
            elif operation == "aggregate":
                cursor = collection.aggregate(pipeline)
                result = [doc async for doc in cursor]
                return MongoDB.transform_objectid(result)

            # 插入
            elif operation in ("insert", "insertOne", "insertMany"):
                if many or operation == "insertMany":
                    res = await collection.insert_many(data)
                    return [{"inserted_ids": [str(_id) for _id in res.inserted_ids]}]
                else:
                    res = await collection.insert_one(data)
                    return [{"inserted_id": str(res.inserted_id)}]

            # 更新
            elif operation in ("update", "updateOne", "updateMany"):
                if many or operation == "updateMany":
                    res = await collection.update_many(filter_, {"$set": data})
                else:
                    res = await collection.update_one(filter_, {"$set": data})
                return [{"matched": res.matched_count, "modified": res.modified_count}]

            # 删除
            elif operation in ("delete", "deleteOne", "deleteMany"):
                if many or operation == "deleteMany":
                    res = await collection.delete_many(filter_)
                else:
                    res = await collection.delete_one(filter_)
                return [{"deleted": res.deleted_count}]

            else:
                raise ValueError(f"Unsupported MongoDB operation: {operation}")

        except Exception as e:
            logging.error(f"\n[执行MongoDB指令失败]\n\n{e}")
            raise e
    
    @staticmethod
    def transform_objectid(doc):
        """递归将 dict/list 中的 ObjectId 转为 str"""
        if isinstance(doc, list):
            return [MongoDB.transform_objectid(d) for d in doc]
        elif isinstance(doc, dict):
            return {k: MongoDB.transform_objectid(v) for k, v in doc.items()}
        elif isinstance(doc, ObjectId):
            return str(doc)
        else:
            return doc