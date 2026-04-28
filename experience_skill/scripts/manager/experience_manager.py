from operator import is_

from ENUM.exprience import ExperienceType, ExperienceStatus
from sqlite import AsyncSQLiteSingleton
from schema.exprience import Experience
from datetime import datetime


class experience_manager:
    @staticmethod
    def insert_experiences(experiences: list[Experience]) -> None:
        db = AsyncSQLiteSingleton()
        for experience in experiences:
            db._run(
                """
                INSERT INTO experience_table (id, type, description, status, is_hot, source, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    experience.id,
                    experience.type.value,
                    experience.description,
                    experience.status.value,
                    experience.is_hot,
                    experience.source,
                    datetime.now().isoformat("y-%m-%d %H:%M:%S"),
                    datetime.now().isoformat("y-%m-%d %H:%M:%S"),
                ),
            )

    @staticmethod
    def delete_experiences(experience_ids: list[str]) -> None:
        db = AsyncSQLiteSingleton()
        for experience_id in experience_ids:
            db._run(
                """
                UPDATE experience_table
                SET status = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    ExperienceStatus.DELETED.value,
                    datetime.now().isoformat("y-%m-%d %H:%M:%S"),
                    experience_id,
                ),
            )

    @staticmethod
    def update_experience(experience: Experience) -> None:
        db = AsyncSQLiteSingleton()
        db._run(
            """
            UPDATE experience_table
            SET type = ?, description = ?, status = ?, source = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                experience.type.value,
                experience.description,
                experience.status.value,
                experience.source,
                datetime.now().isoformat("y-%m-%d %H:%M:%S"),
                experience.id,
            ),
        )

    @staticmethod
    def update_hot_experience(experience_id: str) -> None:
        db = AsyncSQLiteSingleton()
        # 先查当前的experience是否存在
        experience = db._query(
            """
            SELECT * FROM experience_table WHERE id = ? AND status = ?
            """,
            (experience_id, ExperienceStatus.EXISTED.value),
        )
        if experience:
            if experience[0]["is_hot"] == 1:
                # 更新updated_at
                db._run(
                    """
                    UPDATE experience_table
                    SET updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        datetime.now().isoformat("y-%m-%d %H:%M:%S"),
                        experience_id,
                    ),
                )
                return
            experience_type = experience[0]["type"]
            hot_experience_cnt = db._query(
                """                SELECT COUNT(*) as cnt FROM experience_table WHERE type = ? AND is_hot = 1 AND status = ?
                """,
                (experience_type, ExperienceStatus.EXISTED.value),
            )[0]["cnt"]
            if hot_experience_cnt >= 20:
                # 将最早的一个is_hot的experience更新为is_hot=0
                db._run(
                    """
                    UPDATE experience_table
                    SET is_hot = 0
                    WHERE id = (
                        SELECT id FROM experience_table WHERE type = ? AND is_hot = 1 AND status = ? ORDER BY updated_at ASC LIMIT 1
                    )
                    """,
                    (experience_type, ExperienceStatus.EXISTED.value),
                )
            db._run(
                """
                    UPDATE experience_table
                    SET is_hot = 1, updated_at = ?
                    WHERE id = ?
                    """,
                (
                    datetime.now().isoformat("y-%m-%d %H:%M:%S"),
                    experience_id,
                ),
            )

    @staticmethod
    def list_experiences(
        experience_type: ExperienceType,
        keywords: list[str] | None,
        is_hot: bool | None,
        page: int,
        page_size: int,
    ) -> list[Experience]:
        if keywords is not None and len(keywords) == 0:
            return []
        db = AsyncSQLiteSingleton()
        offset = (page - 1) * page_size
        where_clauses = ["type = ?", "status = ?"]
        params = [experience_type.value, ExperienceStatus.EXISTED.value]
        if keywords is not None:
            where_clauses.append(" AND ".join(["description LIKE ?"] * len(keywords)))
            params.extend([f"%{keyword}%" for keyword in keywords])
        if is_hot is not None:
            where_clauses.append("is_hot = ?")
            params.append(int(is_hot))
        where_clause = " AND ".join(where_clauses)
        experience_rows = db._query(
            f"""
            SELECT * FROM experience_table
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (*params, page_size, offset),
        )
        experiences = []
        for row in experience_rows:
            experiences.append(
                Experience(
                    id=row["id"],
                    type=ExperienceType(row["type"]),
                    description=row["description"],
                    status=ExperienceStatus(row["status"]),
                    is_hot=bool(row["is_hot"]),
                    source=row["source"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            )
        return experiences

    @staticmethod
    async def query_experience_by_fts5_use_description(
        keywords: list[str],  # 修复拼写错误
        type: ExperienceType,
        top_k: int = 5,
        is_hot: bool | None = None,
        banned_experience_ids: bool | None = None,
        experience_ids: Optional[list[str]] = None,
    ) -> list[Experience]:
        """
        基于FTS5检索Experience：
        1. 先AND语义精确查询
        2. 不足数量再OR语义松散查询
        """
        # 1. 初始化默认参数
        if top_k <= 0:
            return []
        if experience_ids is not None and len(experience_ids) == 0:
            return []

        # 初始化列表，不修改外部传入参数
        banned_ids = banned_experience_ids.copy() if banned_experience_ids else []
        target_experience_ids = experience_ids

        db = AsyncSQLiteSingleton()
        tight_query_cnt = max(1, top_k // 2)
        experiences = []

        # ====================== 抽取公共方法：避免代码重复 ======================
        def build_fts_query(keywords_str: str, limit: int):
            """构建SQL和参数（公共逻辑）"""
            where_clause = "WHERE experience_fts MATCH ? AND type = ?"
            params = [keywords_str, type.value]

            # 过滤已排除ID
            if banned_ids:
                placeholders = ",".join(["?"] * len(banned_ids))
                where_clause += f" AND experience_table.id NOT IN ({placeholders})"
                params.extend(banned_ids)

            # 过滤指定ID
            if target_experience_ids:
                placeholders = ",".join(["?"] * len(target_experience_ids))
                where_clause += f" AND experience_table.id IN ({placeholders})"
                params.extend(target_experience_ids)

            # 安全拼接is_hot（使用?占位符）
            if is_hot is not None:
                where_clause += " AND experience_table.is_hot = ?"
                params.append(int(is_hot))

            # 最终SQL
            sql = f"""
            SELECT experience_table.* FROM experience_table
            JOIN experience_fts ON experience_table.id = experience_fts.rowid
            {where_clause}
            ORDER BY experience_fts.rank
            LIMIT ?
            """
            params.append(limit)
            return sql, params

        # ====================== 1. 紧凑查询（AND） ======================
        and_keywords = " ".join(keywords)
        sql, params = build_fts_query(and_keywords, tight_query_cnt)

        # 修复异步调用
        experience_rows = await db._query(sql, params)

        # 转换为模型
        for row in experience_rows:
            experiences.append(
                Experience(
                    id=row["id"],
                    type=ExperienceType(row["type"]),
                    description=row["description"],
                    status=ExperienceStatus(row["status"]),
                    is_hot=bool(row["is_hot"]),
                    source=row["source"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            )

        # 把已查到的ID加入排除列表（不修改外部参数）
        banned_ids.extend([exp.id for exp in experiences])

        # ====================== 2. 松散查询（OR） ======================
        if len(experiences) < top_k:
            loose_cnt = top_k - len(experiences)
            or_keywords = " OR ".join(keywords)
            sql, params = build_fts_query(or_keywords, loose_cnt)

            experience_rows = await db._query(sql, params)

            # 修复模型构造错误
            for row in experience_rows:
                experiences.append(
                    Experience(
                        id=row["id"],
                        type=ExperienceType(row["type"]),
                        description=row["description"],
                        status=ExperienceStatus(row["status"]),
                        is_hot=bool(row["is_hot"]),
                        source=row["source"],
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                    )
                )

        return experiences
