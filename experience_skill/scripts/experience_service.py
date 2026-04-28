import os
import re
import yaml
from ENUM.exprience import ExperienceType, ExperienceStatus
from manager.experience_manager import ExperienceManager
from manager.keyword_manager import KeyWordManager
from schema.exprience import Experience


class ExperienceService:
    @staticmethod
    def filter_special_characters(text: str) -> str:
        """
        清理 description 文本。
        去除 FTS5 特殊符号（保留中文、英文、数字、下划线），
        避免 simple_query / MATCH 时触发语法错误或分词异常。
        """
        # 保留中文(\u4e00-\u9fff)、英文、数字、下划线，其余替换为空格
        cleaned = re.sub(r"[^\u4e00-\u9fff\w]", " ", text)
        # 合并连续空格
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()

    @staticmethod
    def md_to_structured_json(md_content: str) -> dict:
        """
        从 Markdown 的 YAML front matter 中解析结构化数据（name / description / keywords）
        """
        result = {}
        # 匹配标准的 front matter：---\n...yaml...\n---
        match = __import__("re").match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", md_content, __import__("re").DOTALL)
        if match:
            try:
                result = yaml.safe_load(match.group(1)) or {}
            except Exception:
                result = {}
        return result

    @staticmethod
    async def add_experiences(
        experience_type: ExperienceType, source: str
    ) -> Experience:
        """
        添加Experience
        """
        description = ""
        keywords = []
        if experience_type == ExperienceType.SKILL:
            path = os.path.join(source, "SKILL.md")
            if not os.path.exists(path):
                raise FileNotFoundError(f"SKILL.md not found in {source}")
            md_content = open(path, "r", encoding="utf-8").read()
            structured_data = ExperienceService.md_to_structured_json(md_content)
        elif experience_type == ExperienceType.WIKI:
            path = source
            if not os.path.exists(path):
                raise FileNotFoundError(f"WIKI.md not found in {source}")
            structured_data = yaml.safe_load(open(path, "r", encoding="utf-8"))
        description = structured_data.get("description", "")
        keywords = structured_data.get("keywords", [])
        description = ExperienceService.filter_special_characters(description)
        experience = Experience(
            type=experience_type,
            description=description,
            keywords=keywords,
            source=source,
        )
        KeyWordManager.add_keywords(experience.id, keywords)
        ExperienceManager.add_experiences([experience])
        return experience

    @staticmethod
    def list_experiences(
        experience_type: ExperienceType | None,
        is_hot: bool | None,
        page: int,
        page_size: int,
    ) -> tuple[int, list[Experience]]:
        """
        列出Experience
        """
        total_cnt, experiences = ExperienceManager.list_experiences(
            experience_type=experience_type,
            keywords=None,
            is_hot=is_hot,
            page=page,
            page_size=page_size,
        )
        for experience in experiences:
            experience.keywords = KeyWordManager.get_keywords_by_experience_id(
                experience.id
            )
        return total_cnt, experiences

    @staticmethod
    def delete_experience_by_ids(experience_ids: list[str]) -> None:
        """
        删除Experience
        """
        ExperienceManager.delete_experiences_by_ids(experience_ids)
        for experience_id in experience_ids:
            KeyWordManager.delete_keywords_by_experience_id(experience_id)

    @staticmethod
    def delete_experience_by_source(source: str) -> None:
        """
        删除Experience
        """
        experience_ids = ExperienceManager.query_experience_ids_by_source(source)
        ExperienceManager.delete_experiences_by_ids(experience_ids)
        for experience_id in experience_ids:
            KeyWordManager.delete_keywords_by_experience_id(experience_id)

    @staticmethod
    def search_experiences(
        query: str,
        type: ExperienceType,
        fields: list[str] | None = None,
        top_k: int = 5,
        is_hot: bool | None = None,
        banned_experience_ids: list[str] | None = None,
        experience_ids: list[str] | None = None,
    ) -> list[Experience]:
        """
        搜索Experience。
        使用 simple tokenizer 扩展后，查询交由 simple_query() 自动处理中文/拼音分词，
        无需在应用层手动组装 FTS5 MATCH 语法。
        """
        query_str = query.strip()
        if not query_str:
            return []

        # 查询侧同样清洗特殊符号，与录入保持一致
        cleaned = re.sub(r"[^\u4e00-\u9fff\w]", " ", query_str)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        keywords = [w.strip() for w in cleaned.split() if w.strip()]
        if not keywords:
            keywords = [cleaned]

        experiences = ExperienceManager.query_experience_by_fts5_use_description(
            keywords=keywords,
            type=type,
            fields=fields,
            is_hot=is_hot,
            top_k=top_k,
            banned_experience_ids=banned_experience_ids,
            experience_ids=experience_ids,
        )
        for experience in experiences:
            experience.keywords = KeyWordManager.get_keywords_by_experience_id(
                experience.id
            )
        return experiences
