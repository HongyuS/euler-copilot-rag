from schema.enum import ExperienceStatus, ExperienceType
from sqlite import AsyncSQLiteSingleton


class KeyWordManager:
    @staticmethod
    def add_keywords(experience_id: str, keywords: list[str]) -> None:
        db = AsyncSQLiteSingleton()
        for keyword in keywords:
            db._run(
                "INSERT INTO keyword_table (experience_id, name) VALUES (?, ?)",
                (experience_id, keyword),
            )

    @staticmethod
    def get_keywords_by_experience_id(experience_id: str) -> list[str]:
        db = AsyncSQLiteSingleton()
        rows = db._query(
            "SELECT name FROM keyword_table WHERE experience_id = ?", (experience_id,)
        )
        return [row["name"] for row in rows]

    @staticmethod
    def delete_keywords_by_experience_id(experience_id: str) -> None:
        db = AsyncSQLiteSingleton()
        db._run("DELETE FROM keyword_table WHERE experience_id = ?", (experience_id,))

    @staticmethod
    def get_all_keywords(experience_type: ExperienceType | None = None) -> list[str]:
        """获取所有不重复的关键词名，可按经验类型过滤。"""
        db = AsyncSQLiteSingleton()
        if experience_type is not None:
            rows = db._query(
                """
                SELECT DISTINCT k.name
                FROM keyword_table k
                JOIN experience_table e ON k.experience_id = e.id
                WHERE e.type = ? AND e.status = ?
                ORDER BY k.name
                """,
                (experience_type.value, ExperienceStatus.EXISTED.value),
            )
        else:
            rows = db._query(
                """
                SELECT DISTINCT k.name
                FROM keyword_table k
                JOIN experience_table e ON k.experience_id = e.id
                WHERE e.status = ?
                ORDER BY k.name
                """,
                (ExperienceStatus.EXISTED.value,),
            )
        return [row["name"] for row in rows]

    @staticmethod
    def get_experience_ids_by_keywords(keywords: list[str]) -> list[str]:
        """获取包含任意指定关键词的经验 ID 列表（去重）。"""
        if not keywords:
            return []
        db = AsyncSQLiteSingleton()
        placeholders = ",".join(["?"] * len(keywords))
        rows = db._query(
            f"""
            SELECT DISTINCT k.experience_id
            FROM keyword_table k
            JOIN experience_table e ON k.experience_id = e.id
            WHERE k.name IN ({placeholders}) AND e.status = ?
            """,
            (*keywords, ExperienceStatus.EXISTED.value),
        )
        return [row["experience_id"] for row in rows]
