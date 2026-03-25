"""任务数据库 - 独立 task.db，与 kb.db 分离"""
import asyncio
import logging
import os
import sqlite3
from typing import Any, Optional

logger = logging.getLogger(__name__)

TASK_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS task_table (
    task_id TEXT PRIMARY KEY,
    pid INTEGER,
    task_name TEXT NOT NULL,
    task_type TEXT NOT NULL,
    completion_precent REAL NOT NULL,
    status TEXT NOT NULL,
    task_related_params TEXT,
    result_summary TEXT,
    created_at TEXT NOT NULL
)
"""

_task_db_path: Optional[str] = None
_conn: Optional[sqlite3.Connection] = None
_lock = asyncio.Lock()


def init_task_db(db_path: str) -> None:
    """初始化任务数据库"""
    global _task_db_path, _conn
    abs_path = os.path.abspath(db_path)
    db_dir = os.path.dirname(abs_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    _task_db_path = abs_path
    _conn = sqlite3.connect(abs_path, check_same_thread=False, timeout=30.0)
    _conn.execute("PRAGMA journal_mode=WAL")
    _conn.execute(TASK_TABLE_DDL)
    _conn.commit()
    logger.info("任务数据库初始化完成: %s", abs_path)


def _get_conn() -> sqlite3.Connection:
    if _conn is None:
        raise RuntimeError("任务数据库未初始化，请先调用 init_task_db")
    return _conn


async def execute_query(sql: str, params: dict | tuple = ()) -> list[dict]:
    """异步查询"""
    def _run():
        conn = _get_conn()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]

    async with _lock:
        return await asyncio.to_thread(_run)


async def execute_modify(sql: str, params: Any = ()) -> bool:
    """异步增删改"""
    def _run():
        conn = _get_conn()
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()
            return True
        except sqlite3.Error:
            conn.rollback()
            raise

    async with _lock:
        try:
            await asyncio.to_thread(_run)
            return True
        except sqlite3.Error as e:
            logger.error("任务数据库执行失败: %s", e)
            return False
