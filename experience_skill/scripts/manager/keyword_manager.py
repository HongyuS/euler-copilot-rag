from datetime import datetime
from operator import is_

from ENUM.exprience import ExperienceStatus, ExperienceType
from schema.exprience import Experience
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
        rows = db._query("SELECT name FROM keyword_table WHERE experience_id = ?", (experience_id,))
        return [row["name"] for row in rows]

    @staticmethod
    def delete_keywords_by_experience_id(experience_id: str) -> None:
        db = AsyncSQLiteSingleton()
        db._run("DELETE FROM keyword_table WHERE experience_id = ?", (experience_id,))
