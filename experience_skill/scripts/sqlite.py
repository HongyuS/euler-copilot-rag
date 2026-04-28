from multiprocessing import Lock as ProcessLock
import asyncio
import sqlite3
import logging
from typing import Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====================== 表结构（正确版） ======================
table_ddl_list = {
    "keyword_table": """
        CREATE TABLE IF NOT EXISTS keyword_table (
            id TEXT PRIMARY KEY,
            experience_id TEXT NOT NULL,
            name TEXT NOT NULL
        )
    """,
    "experience_table": """
        CREATE TABLE IF NOT EXISTS experience_table (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            is_hot BOOLEAN NOT NULL DEFAULT 0,
            source TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """,
    "experience_fts": """
        CREATE VIRTUAL TABLE IF NOT EXISTS experience_fts USING fts5(
            description,
            content=experience_table,
            content_rowid=rowid
        )
    """,
    "trg1": """
        CREATE TRIGGER IF NOT EXISTS fts_insert
        AFTER INSERT ON experience_table
        BEGIN
            INSERT INTO experience_fts(rowid, description) VALUES (new.rowid, new.description);
        END
    """,
    "trg2": """
        CREATE TRIGGER IF NOT EXISTS fts_update
        AFTER UPDATE ON experience_table
        BEGIN
            UPDATE experience_fts SET description=new.description WHERE rowid=new.rowid;
        END
    """,
    "trg3": """
        CREATE TRIGGER IF NOT EXISTS fts_delete
        AFTER DELETE ON experience_table
        BEGIN
            DELETE FROM experience_fts WHERE rowid=old.rowid;
        END
    """,
}


class AsyncSQLiteSingleton:
    _instance: Optional["AsyncSQLiteSingleton"] = None
    _process_lock = ProcessLock()

    def __new__(cls):
        if cls._instance is None:
            with cls._process_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_init"):
            return
        self.DB_PATH = "experience.db"
        self._async_lock = asyncio.Lock()
        self._conn = None
        self._init = True
        self._connect()

    def _connect(self) -> None:
        if self._conn:
            return
        self._conn = sqlite3.connect(self.DB_PATH, check_same_thread=False, timeout=30)
        self._conn.execute("PRAGMA journal_mode=WAL")

    def _run(self, sql, params=()) -> bool:
        self._connect()
        try:
            cur = self._conn.cursor()
            cur.execute(sql, params)
            self._conn.commit()
            return True
        except:
            self._conn.rollback()
            return False

    def _query(self, sql, params=()) -> list[dict[str, Any]]:
        self._connect()
        try:
            self._conn.row_factory = sqlite3.Row
            cur = self._conn.cursor()
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]
        except:
            return []

    def init(self) -> None:
        for sql in table_ddl_list.values():
            self._run(sql)
