import os
from multiprocessing import Lock as ProcessLock
import asyncio
import sqlite3
import logging
from typing import Any, Optional
from src.config.config import Config

# 配置日志
logger = logging.getLogger(__name__)

# 表结构定义
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
    ''',
    "embedding_cache_table": '''
        CREATE TABLE IF NOT EXISTS embedding_cache_table (
            text_hash TEXT PRIMARY KEY,
            text_content TEXT NOT NULL,
            embedding_vector TEXT NOT NULL,
            model_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_accessed_at TEXT NOT NULL,
            access_count INTEGER DEFAULT 0
        )
    ''',
    "embedding_cache_index": '''
        CREATE INDEX IF NOT EXISTS idx_embedding_model ON embedding_cache_table (model_name)
    '''
}


class AsyncSQLiteSingleton:
    # 类级别的单例实例（按进程ID存储）
    _instances: dict[int, 'AsyncSQLiteSingleton'] = {}
    # 进程级锁（跨进程保护）
    _process_lock = ProcessLock()
    # 类级锁（单例创建保护）
    _class_lock = asyncio.Lock()

    def __new__(cls):
        """实现单例模式（支持多进程）"""
        pid = os.getpid()
        
        if pid not in cls._instances:
            with cls._process_lock:
                if pid not in cls._instances:
                    logger.debug(f"为进程 {pid} 创建新的数据库实例")
                    cls._instances[pid] = super().__new__(cls)
        
        return cls._instances[pid]

    def __init__(self):
        # 防止重复初始化
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        # 数据库配置
        self.DB_PATH = Config().get_config().sql_lite_db_path
        # 异步锁（协程级）
        self._async_lock = asyncio.Lock()
        # 数据库连接（复用连接，避免频繁创建/关闭）
        self._conn: Optional[sqlite3.Connection] = None
        # 初始化标记
        self._initialized = False
        
        # 初始化数据库连接
        self._init_connection()

    def _init_connection(self):
        """初始化数据库连接（复用连接）"""
        try:
            # 增加超时时间到30秒，关闭自动提交
            self._conn = sqlite3.connect(
                self.DB_PATH,
                check_same_thread=False,
                timeout=30.0,  # 增加超时时间
                isolation_level=None  # 关闭自动提交，手动控制事务
            )
            # 启用外键约束
            self._conn.execute("PRAGMA foreign_keys = ON")
            # 启用 WAL 模式（提高并发性能）
            self._conn.execute("PRAGMA journal_mode=WAL")
            # 设置同步模式为NORMAL（平衡性能和安全性）
            self._conn.execute("PRAGMA synchronous=NORMAL")
            
            logger.debug(f"进程 {os.getpid()} 数据库连接初始化成功")
        except sqlite3.Error as e:
            logger.error(f"数据库连接初始化失败: {e}")
            raise

    # -------------------------- 同步操作函数（所有操作都在同一个连接执行） --------------------------
    def _sync_init_database(self) -> bool:
        """同步初始化数据库（复用连接）"""
        # 确保连接存在
        if not self._conn:
            logger.debug(f"进程 {os.getpid()} 重新初始化连接")
            self._init_connection()
        
        # 再次检查连接
        if not self._conn:
            logger.error("无法建立数据库连接")
            return False

        try:
            # 初始化所有表
            for table_name, ddl in table_ddl_list.items():
                self._conn.execute(ddl)
            self._conn.commit()
            logger.info(f"进程 {os.getpid()} 数据库初始化成功，表创建完成")
            self._initialized = True
            return True
        except sqlite3.Error as e:
            try:
                self._conn.rollback()
            except:
                pass
            logger.error(f"数据库初始化失败: {e}")
            return False

    def _ensure_connection(self):
        """确保数据库连接可用"""
        if not self._conn:
            logger.debug(f"进程 {os.getpid()} 连接为空，正在重新初始化")
            self._init_connection()
            return True
        
        try:
            # 测试连接是否有效
            self._conn.execute("SELECT 1")
            return True
        except (sqlite3.Error, sqlite3.ProgrammingError):
            logger.warning(f"进程 {os.getpid()} 连接失效，正在重新初始化")
            self._init_connection()
            return True

    def _sync_execute_query(self, sql: str, params: dict | tuple = ()) -> list[dict]:
        """同步执行查询（复用连接）"""
        self._ensure_connection()

        try:
            self._conn.row_factory = sqlite3.Row
            cursor = self._conn.cursor()
            cursor.execute(sql, params)
            results = [dict(row) for row in cursor.fetchall()]
            logger.debug(f"执行查询成功，返回 {len(results)} 条记录")
            return results
        except (sqlite3.Error, sqlite3.ProgrammingError) as e:
            logger.warning(f"查询失败，尝试重新连接: {e}")
            # 如果连接有问题，重新初始化
            self._init_connection()
            try:
                self._conn.row_factory = sqlite3.Row
                cursor = self._conn.cursor()
                cursor.execute(sql, params)
                results = [dict(row) for row in cursor.fetchall()]
                logger.debug(f"重试查询成功，返回 {len(results)} 条记录")
                return results
            except Exception as e2:
                logger.error(f"重试查询也失败: {e2} (SQL: {sql}, params: {params})")
                return []

    def _sync_execute_modify(self, sql: str, params: Any = ()) -> bool:
        """
        同步执行增删改（支持单条/批量，复用连接）
        :param sql: SQL修改语句（位置参数用?，命名参数用:param_name）
        :param params: 单条：dict/元组；批量：list[元组]
        :return: 是否执行成功
        """
        self._ensure_connection()

        try:
            cursor = self._conn.cursor()

            # 判断是否为批量操作
            if isinstance(params, list) and len(params) > 0 and isinstance(params[0], (tuple, list)):
                # 批量操作：使用 executemany
                cursor.executemany(sql, params)
                logger.debug(f"批量执行修改成功，影响行数: {cursor.rowcount}")
            else:
                # 单条操作：使用 execute
                cursor.execute(sql, params)
                logger.debug(f"单条执行修改成功，影响行数: {cursor.rowcount}")

            self._conn.commit()
            return True
        except (sqlite3.Error, sqlite3.ProgrammingError) as e:
            logger.warning(f"修改失败，尝试重新连接: {e}")
            # 尝试回滚
            try:
                self._conn.rollback()
            except:
                pass
            # 重新初始化
            self._init_connection()
            # 重试
            try:
                cursor = self._conn.cursor()
                if isinstance(params, list) and len(params) > 0 and isinstance(params[0], (tuple, list)):
                    cursor.executemany(sql, params)
                else:
                    cursor.execute(sql, params)
                self._conn.commit()
                logger.debug("重试修改成功")
                return True
            except Exception as e2:
                logger.error(f"重试修改也失败: {e2} (SQL: {sql}, params: {params})")
                return False

    # -------------------------- 异步封装接口 --------------------------
    async def init_database(self) -> bool:
        """异步初始化数据库"""
        async with self._async_lock:
            return await asyncio.to_thread(self._sync_init_database)

    async def execute_query(self, sql: str, params: dict | tuple = ()) -> list[dict]:
        """
        异步执行查询语句
        :param sql: SQL查询语句（支持命名参数 :param_name 或位置参数 ?）
        :param params: 命名参数字典或位置参数元组
        :return: 查询结果列表（每行是字典）
        """
        async with self._async_lock:
            return await asyncio.to_thread(self._sync_execute_query, sql, params)

    async def execute_modify(self, sql: str, params: Any = ()) -> bool:
        """
        异步执行增删改语句
        :param sql: SQL修改语句（支持命名参数 :param_name 或位置参数 ?）
        :param params: 命名参数字典或位置参数元组
        :return: 是否执行成功
        """
        async with self._async_lock:
            return await asyncio.to_thread(self._sync_execute_modify, sql, params)

    async def close_connection(self):
        """关闭数据库连接"""
        async with self._async_lock:
            def _close():
                if self._conn:
                    self._conn.close()
                    self._conn = None
                    logger.info("数据库连接已关闭")
            await asyncio.to_thread(_close)

    def __del__(self):
        """析构函数：确保连接关闭"""
        if self._conn:
            self._conn.close()
            logger.info("析构函数中关闭数据库连接")