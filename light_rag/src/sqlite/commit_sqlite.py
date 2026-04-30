"""
Commit 向量库管理（本地 SQLite + sqlite-vec）
"""
import os
import sqlite3
import struct
import logging
from typing import Any, Dict, List

import sqlite_vec
from common.config import get_embedding_vector_dimension

logger = logging.getLogger(__name__)


def _resolve_db_path(db_path: str) -> str:
    if os.path.isabs(db_path):
        return db_path
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.abspath(os.path.join(src_dir, db_path))


def _connect(db_path: str) -> sqlite3.Connection:
    abs_db_path = _resolve_db_path(db_path)
    os.makedirs(os.path.dirname(abs_db_path), exist_ok=True)
    conn = sqlite3.connect(abs_db_path)
    conn.row_factory = sqlite3.Row
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)
    return conn


def init_commit_vector_db(db_path: str) -> None:
    vector_dim = get_embedding_vector_dimension()
    conn = _connect(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS commit_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo TEXT NOT NULL,
                sha TEXT NOT NULL,
                summary TEXT NOT NULL,
                content TEXT NOT NULL,
                author_date TEXT,
                api_url TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(repo, sha)
            )
            """
        )
        conn.execute(
            f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS commit_vec_index USING vec0(
                embedding float[{vector_dim}]
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def upsert_commit_records(db_path: str, records: List[Dict[str, Any]]) -> int:
    if not records:
        return 0
    conn = _connect(db_path)
    try:
        inserted = 0
        for rec in records:
            embedding = rec.get("embedding")
            if not embedding:
                continue
            embedding_bytes = struct.pack(f"{len(embedding)}f", *embedding)
            conn.execute(
                """
                INSERT INTO commit_records (repo, sha, summary, content, author_date, api_url, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(repo, sha) DO UPDATE SET
                    summary=excluded.summary,
                    content=excluded.content,
                    author_date=excluded.author_date,
                    api_url=excluded.api_url,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (
                    rec["repo"],
                    rec["sha"],
                    rec["summary"],
                    rec["content"],
                    rec.get("author_date"),
                    rec.get("api_url"),
                ),
            )
            row = conn.execute(
                "SELECT id FROM commit_records WHERE repo=? AND sha=?",
                (rec["repo"], rec["sha"]),
            ).fetchone()
            if row:
                conn.execute(
                    "INSERT OR REPLACE INTO commit_vec_index(rowid, embedding) VALUES (?, ?)",
                    (row["id"], embedding_bytes),
                )
                inserted += 1
        conn.commit()
        return inserted
    finally:
        conn.close()


def search_commit_vectors(db_path: str, query_vector: List[float], top_k: int) -> List[Dict[str, Any]]:
    if not query_vector:
        return []
    conn = _connect(db_path)
    try:
        query_vector_bytes = struct.pack(f"{len(query_vector)}f", *query_vector)
        rows = conn.execute(
            """
            SELECT c.repo, c.sha, c.summary, c.content, c.api_url, distance
            FROM commit_vec_index v
            JOIN commit_records c ON c.id = v.rowid
            WHERE v.embedding MATCH ? AND k = ?
            ORDER BY distance
            """,
            (query_vector_bytes, top_k),
        ).fetchall()
        results = []
        for row in rows:
            distance = float(row["distance"]) if row["distance"] is not None else 999.0
            similarity = round(1.0 / (1.0 + max(distance, 0.0)), 3)
            results.append(
                {
                    "repo": row["repo"],
                    "sha": row["sha"],
                    "summary": row["summary"],
                    "content": row["content"],
                    "api_url": row["api_url"],
                    "similarity": similarity,
                }
            )
        return results
    except Exception as e:
        logger.warning(f"[CommitVectorDB] 本地向量检索失败: {e}")
        return []
    finally:
        conn.close()
