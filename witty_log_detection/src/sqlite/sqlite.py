from multiprocessing import Lock
import asyncio
import sqlite3
import logging
from typing import Any
from src.config.config import Config

logger = logging.getLogger(__name__)

table_ddl_list = {
    "task_table": '''
        CREATE TABLE IF NOT EXISTS task_table (
            task_id TEXT PRIMARY KEY,
            pid INTEGER,
            task_name TEXT NOT NULL,
            task_type TEXT NOT NULL,
            completion_precent REAL NOT NULL,
            status TEXT NOT NULL,
            task_related_params TEXT,
            created_at TEXT NOT NULL
        )
    ''',
    "log_parse_result_table": '''
        CREATE TABLE IF NOT EXISTS log_parse_result_table(
            id TEXT PRIMARY KEY,
            file_path TEXT,
            offset INTEGER,
            is_anomalous BOOLEAN NOT NULL,
            task_id TEXT,
            content TEXT,
            anomaly_reason TEXT,
            anomaly_score REAL,
            FOREIGN KEY (task_id) REFERENCES task_table (task_id) ON DELETE CASCADE
        )
    '''
}


class AsyncSQLiteSingleton:
    def __init__(self):
        self.DB_PATH = Config().get_config().sql_lite_db_path
        self._async_lock = asyncio.Lock()
        self._sync_init_database()
    # -------------------------- 同步操作函数（所有操作都在同一个线程执行） --------------------------

    def _sync_init_database(self):
        """同步初始化数据库（完整生命周期，单线程内完成）"""
        conn = None
        try:
            # 创建连接时指定 check_same_thread=False 允许跨线程（但我们会保证单线程使用）
            conn = sqlite3.connect(
                self.DB_PATH,
                check_same_thread=False,
                timeout=5
            )
            conn.execute("PRAGMA foreign_keys = ON")

            # 初始化所有表
            for ddl in table_ddl_list.values():
                cursor = conn.cursor()
                cursor.execute(ddl)
            conn.commit()
            logger.info("数据库初始化成功，表创建完成")
            return True
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"数据库初始化失败: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def _sync_execute_query(self, sql: str, params: dict | tuple) -> list[dict]:
        """同步执行查询（完整生命周期，单线程内完成）"""
        conn = None
        try:
            conn = sqlite3.connect(
                self.DB_PATH,
                check_same_thread=False,
                timeout=5
            )
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql, params)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        except sqlite3.Error as e:
            logger.error(f"执行查询失败: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def _sync_execute_modify(self, sql: str, params: Any) -> bool:
        """
        同步执行增删改（支持单条/批量，完整生命周期，单线程内完成）
        :param sql: SQL修改语句（位置参数用?，命名参数用:param_name）
        :param params: 单条：dict/元组；批量：list[元组]
        :return: 是否执行成功
        """
        conn = None
        try:
            conn = sqlite3.connect(
                self.DB_PATH,
                check_same_thread=False,
                timeout=5
            )
            cursor = conn.cursor()

            # 判断是否为批量操作
            if isinstance(params, list) and len(params) > 0 and isinstance(params[0], (tuple, list)):
                # 批量操作：使用 executemany
                cursor.executemany(sql, params)
                logger.debug(f"批量执行修改成功，影响行数: {cursor.rowcount}")
            else:
                # 单条操作：使用 execute
                cursor.execute(sql, params)
                logger.debug(f"单条执行修改成功，影响行数: {cursor.rowcount}")

            conn.commit()
            return True
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"执行修改失败: {e}")
            return False
        finally:
            if conn:
                conn.close()

    # -------------------------- 异步封装接口 --------------------------
    async def init_database(self):
        """异步初始化数据库"""
        async with self._async_lock:
            # 整个初始化操作在同一个线程中完成
            result = await asyncio.to_thread(self._sync_init_database)
            return result

    async def execute_query(self, sql: str, params: dict | tuple = {}) -> list[dict]:
        """
        异步执行查询语句
        :param sql: SQL查询语句（支持命名参数 :param_name 或位置参数 ?）
        :param params: 命名参数字典或位置参数元组
        :return: 查询结果列表（每行是字典）
        """
        async with self._async_lock:
            # 整个查询操作在同一个线程中完成
            return await asyncio.to_thread(self._sync_execute_query, sql, params)

    async def execute_modify(self, sql: str, params: dict | tuple = {}) -> bool:
        """
        异步执行增删改语句
        :param sql: SQL修改语句（支持命名参数 :param_name 或位置参数 ?）
        :param params: 命名参数字典或位置参数元组
        :return: 是否执行成功
        """
        async with self._async_lock:
            # 整个修改操作在同一个线程中完成
            return await asyncio.to_thread(self._sync_execute_modify, sql, params)
