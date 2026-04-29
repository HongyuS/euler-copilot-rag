import asyncio
import logging
import os
import sqlite3
from multiprocessing import Lock as ProcessLock
from typing import Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====================== 路径常量 ======================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKENIZER_DIR = os.path.join(SCRIPT_DIR, "tokenizer")
LIBSIMPLE_PATH = os.path.join(TOKENIZER_DIR, "libsimple")


# ====================== 表结构 ======================
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
            name TEXT,
            description TEXT,
            "references" TEXT DEFAULT '',
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
            content_rowid=rowid,
            tokenize='simple'
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


def _check_tokenizer() -> str:
    """
    检查 libsimple 扩展是否已就绪，返回扩展路径（不带后缀）。
    如果不存在，抛出 RuntimeError 提示用户手动编译。
    """
    ext_candidates = [
        LIBSIMPLE_PATH,
        LIBSIMPLE_PATH + ".so",
        LIBSIMPLE_PATH + ".dylib",
        LIBSIMPLE_PATH + ".dll",
    ]
    ext_exists = any(os.path.exists(p) for p in ext_candidates)

    if not ext_exists:
        build_script = os.path.join(TOKENIZER_DIR, "build.sh")
        raise RuntimeError(
            f"[Tokenizer] 扩展未找到: {LIBSIMPLE_PATH}\n"
            f"            请先编译 simple 分词器扩展:\n"
            f"            bash {build_script}"
        )

    return LIBSIMPLE_PATH


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
        self.DB_PATH = os.path.join(SCRIPT_DIR, "experience.db")
        self._async_lock = asyncio.Lock()
        self._conn = None
        self._init = True
        self._ext_path: Optional[str] = None
        self._connect()

    def _connect(self) -> None:
        if self._conn:
            return
        self._conn = sqlite3.connect(self.DB_PATH, check_same_thread=False, timeout=30)
        self._conn.execute("PRAGMA journal_mode=WAL")

        # 加载 simple 分词器扩展（幂等：只加载一次）
        if self._ext_path is None:
            self._ext_path = _check_tokenizer()
        self._conn.enable_load_extension(True)
        self._conn.load_extension(self._ext_path)

    def _run(self, sql, params=()) -> bool:
        self._connect()
        try:
            cur = self._conn.cursor()
            cur.execute(sql, params)
            self._conn.commit()
            return True
        except Exception as e:
            logger.error(f"SQL execute error: {e}, sql: {sql}, params: {params}")
            self._conn.rollback()
            return False

    def _query(self, sql, params=()) -> list[dict[str, Any]]:
        self._connect()
        try:
            self._conn.row_factory = sqlite3.Row
            cur = self._conn.cursor()
            cur.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]
        except Exception as e:
            logger.error(f"SQL query error: {e}, sql: {sql}, params: {params}")
            return []

    def _ensure_column(self, table: str, column: str, col_type: str) -> None:
        """检查表是否包含指定列，没有则添加（用于旧表迁移）。"""
        self._connect()
        cur = self._conn.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cur.fetchall()]
        if column not in cols:
            self._run(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")

    def init(self) -> None:
        for sql in table_ddl_list.values():
            self._run(sql)
        # 兼容旧表：动态添加列（如果尚不存在）
        self._ensure_column("experience_table", "name", "TEXT")
        self._ensure_column("experience_table", "references", "TEXT")

    def clear_database(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
        for suffix in ["", "-wal", "-shm"]:
            path = self.DB_PATH + suffix
            if os.path.exists(path):
                os.remove(path)
