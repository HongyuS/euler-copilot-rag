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
                INSERT INTO experience_table (id, type, description, keywords, status, created_at, updated_at,is_hot)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    experience.id,
                    experience.type.value,
                    experience.description,
                    experience.keywords,
                    experience.status.value,
                    experience.created_at,
                    experience.updated_at,
                    0,  # 默认is_hot为0
                ),
            )

    @staticmethod
    def update_experience(experience: Experience) -> None:
        db = AsyncSQLiteSingleton()
        db._run(
            """
            UPDATE experience_table
            SET type = ?, description = ?, keywords = ?, status = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                experience.type.value,
                experience.description,
                experience.keywords,
                experience.status.value,
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