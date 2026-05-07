import os
from multiprocessing import Lock as ProcessLock
import asyncio
import sqlite3
import logging
from typing import Any, Optional
from src.config.config import Config

logger = logging.getLogger(__name__)


class EmbeddingCacheSQLite:
    """Embedding缓存专用的SQLite数据库单例
    
    与主数据库分离，独立管理embedding缓存
    """
    # 类级别的单例实例（按进程ID存储）
    _instances: dict[int, 'EmbeddingCacheSQLite'] = {}
    # 进程级锁（跨进程保护）
    _process_lock = ProcessLock()
    
    def __new__(cls):
        """实现单例模式（支持多进程）"""
        pid = os.getpid()
        
        if pid not in cls._instances:
            with cls._process_lock:
                if pid not in cls._instances:
                    logger.debug(f"为进程 {pid} 创建新的 EmbeddingCacheSQLite 实例")
                    cls._instances[pid] = super().__new__(cls)
        
        return cls._instances[pid]

    def __init__(self):
        # 防止重复初始化
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        # 数据库配置
        self.DB_PATH = Config().get_config().embedding_cache_db_path
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
                timeout=30.0,
                isolation_level=None
            )
            # 启用 WAL 模式（提高并发性能）
            self._conn.execute("PRAGMA journal_mode=WAL")
            # 设置同步模式为NORMAL（平衡性能和安全性）
            self._conn.execute("PRAGMA synchronous=NORMAL")
            
            logger.debug(f"进程 {os.getpid()} Embedding缓存数据库连接初始化成功")
        except sqlite3.Error as e:
            logger.error(f"Embedding缓存数据库连接初始化失败: {e}")
            raise

    def _ensure_connection(self):
        """确保数据库连接可用"""
        if not self._conn:
            logger.debug(f"进程 {os.getpid()} Embedding缓存连接为空，正在重新初始化")
            self._init_connection()
            return True
        
        try:
            # 测试连接是否有效
            self._conn.execute("SELECT 1")
            return True
        except (sqlite3.Error, sqlite3.ProgrammingError):
            logger.warning(f"进程 {os.getpid()} Embedding缓存连接失效，正在重新初始化")
            self._init_connection()
            return True

    def _sync_init_database(self) -> bool:
        """同步初始化数据库（复用连接）"""
        self._ensure_connection()
        
        try:
            # 创建缓存表
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS embedding_cache_table (
                    text_hash TEXT PRIMARY KEY,
                    text_content TEXT NOT NULL,
                    embedding_vector TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed_at TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0
                )
            """)
            
            # 创建索引
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_embedding_model ON embedding_cache_table (model_name)
            """)
            
            self._conn.commit()
            logger.info(f"进程 {os.getpid()} Embedding缓存数据库初始化成功")
            self._initialized = True
            return True
        except sqlite3.Error as e:
            try:
                self._conn.rollback()
            except:
                pass
            logger.error(f"Embedding缓存数据库初始化失败: {e}")
            return False

    def _sync_execute_query(self, sql: str, params: dict | tuple = ()) -> list[dict]:
        """同步执行查询（复用连接）"""
        self._ensure_connection()

        try:
            self._conn.row_factory = sqlite3.Row
            cursor = self._conn.cursor()
            cursor.execute(sql, params)
            results = [dict(row) for row in cursor.fetchall()]
            logger.debug(f"Embedding缓存查询成功，返回 {len(results)} 条记录")
            return results
        except (sqlite3.Error, sqlite3.ProgrammingError) as e:
            logger.warning(f"Embedding缓存查询失败，尝试重新连接: {e}")
            self._init_connection()
            try:
                self._conn.row_factory = sqlite3.Row
                cursor = self._conn.cursor()
                cursor.execute(sql, params)
                results = [dict(row) for row in cursor.fetchall()]
                logger.debug(f"Embedding缓存重试查询成功，返回 {len(results)} 条记录")
                return results
            except Exception as e2:
                logger.error(f"Embedding缓存重试查询也失败: {e2}")
                return []

    def _sync_execute_modify(self, sql: str, params: Any = ()) -> bool:
        """同步执行增删改（支持单条/批量，复用连接）"""
        self._ensure_connection()

        try:
            cursor = self._conn.cursor()

            if isinstance(params, list) and len(params) > 0 and isinstance(params[0], (tuple, list)):
                cursor.executemany(sql, params)
                logger.debug(f"Embedding缓存批量修改成功，影响行数: {cursor.rowcount}")
            else:
                cursor.execute(sql, params)
                logger.debug(f"Embedding缓存单条修改成功，影响行数: {cursor.rowcount}")

            self._conn.commit()
            return True
        except (sqlite3.Error, sqlite3.ProgrammingError) as e:
            logger.warning(f"Embedding缓存修改失败，尝试重新连接: {e}")
            try:
                self._conn.rollback()
            except:
                pass
            self._init_connection()
            try:
                cursor = self._conn.cursor()
                if isinstance(params, list) and len(params) > 0 and isinstance(params[0], (tuple, list)):
                    cursor.executemany(sql, params)
                else:
                    cursor.execute(sql, params)
                self._conn.commit()
                logger.debug("Embedding缓存重试修改成功")
                return True
            except Exception as e2:
                logger.error(f"Embedding缓存重试修改也失败: {e2}")
                return False

    async def init_database(self) -> bool:
        """异步初始化数据库"""
        async with self._async_lock:
            return await asyncio.to_thread(self._sync_init_database)

    async def execute_query(self, sql: str, params: dict | tuple = ()) -> list[dict]:
        """异步执行查询"""
        async with self._async_lock:
            return await asyncio.to_thread(self._sync_execute_query, sql, params)

    async def execute_modify(self, sql: str, params: Any = ()) -> bool:
        """异步执行增删改"""
        async with self._async_lock:
            return await asyncio.to_thread(self._sync_execute_modify, sql, params)

    async def close_connection(self):
        """关闭数据库连接"""
        async with self._async_lock:
            def _close():
                if self._conn:
                    self._conn.close()
                    self._conn = None
                    logger.info("Embedding缓存数据库连接已关闭")
            await asyncio.to_thread(_close)

    def __del__(self):
        """析构函数：确保连接关闭"""
        if self._conn:
            try:
                self._conn.close()
                logger.info("析构函数中关闭Embedding缓存数据库连接")
            except:
                pass
