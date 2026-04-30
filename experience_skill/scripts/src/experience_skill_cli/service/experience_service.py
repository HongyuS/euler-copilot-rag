"""经验业务服务层。"""

import json
import re
from pathlib import Path

import yaml

from experience_skill_cli.manager.experience_manager import ExperienceManager
from experience_skill_cli.manager.keyword_manager import KeyWordManager
from experience_skill_cli.schema.enum import ExperienceType
from experience_skill_cli.schema.exprience import Experience


class ExperienceService:
    """Experience 服务"""

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
        """从 Markdown 的 YAML front matter 中解析结构化数据（name / description / keywords）"""
        result = {}
        # 匹配标准的 front matter：---\n...yaml...\n---
        match = __import__("re").match(
            r"^---\s*\n(.*?)\n---\s*(?:\n|$)",
            md_content,
            __import__("re").DOTALL,
        )
        if match:
            try:
                result = yaml.safe_load(match.group(1)) or {}
            except Exception:  # noqa: BLE001
                result = {}
        return result

    @staticmethod
    def add_experiences(experience_type: ExperienceType, source: str) -> Experience:
        """
        添加Experience（Skill / Wiki）。

        流程：
        1. 检查 source 路径是否已注册（精确去重）。
        2. 读取源文件（skill_def.md 或 .md），解析 YAML front matter。
        3. 仅提取 YAML header 中的 name / description / keywords / references 写入 DB。
           Markdown 正文不存入数据库，仅供检索命中后按 source 路径读取使用。
        4. 写入 experience_table + keyword_table + FTS 索引。
        """
        experiences = ExperienceManager.query_experience_by_source(source)
        if experiences:
            msg = f"Experience with source {source} already exists."
            raise ValueError(msg)
        description = ""
        keywords = []
        if experience_type == ExperienceType.SKILL:
            skill_md = Path(source) / "skill_def.md"
            if not skill_md.exists():
                msg = f"skill_def.md not found in {source}"
                raise FileNotFoundError(msg)
            structured_data = ExperienceService.md_to_structured_json(
                skill_md.read_text(encoding="utf-8"),
            )
        elif experience_type == ExperienceType.WIKI:
            wiki_md = Path(source)
            if not wiki_md.exists():
                msg = f"WIKI file not found: {source}"
                raise FileNotFoundError(msg)
            structured_data = ExperienceService.md_to_structured_json(
                wiki_md.read_text(encoding="utf-8"),
            )
        name = structured_data.get("name", "")
        description = structured_data.get("description", "")
        keywords = structured_data.get("keywords", [])
        references = structured_data.get("references")
        references_json = json.dumps(references, ensure_ascii=False) if references else ""
        description = ExperienceService.filter_special_characters(description)
        experience = Experience(
            type=experience_type,
            name=name,
            description=description,
            keywords=keywords,
            references=references_json,
            source=source,
        )
        KeyWordManager.add_keywords(experience.id, keywords)
        ExperienceManager.add_experiences([experience])
        return experience

    @staticmethod
    def check_duplicate_before_create(
        experience_type: ExperienceType,
        name: str,
        keywords: list[str],
    ) -> list[Experience]:
        """
        创建前查重：按名称和关键词搜索已有经验，返回相似结果列表。

        用于 create-skill / create-wiki 流程的前置查重步骤，
        若返回非空列表，说明存在相似资源，建议合并或优化。
        """
        # 用名称作为查询词 + 关键字标签做精确过滤
        query = name or " ".join(keywords)
        if not query.strip():
            return []
        similar = ExperienceService.search_experiences(
            query=query,
            exp_type=experience_type,
            fields=keywords or None,
            top_k=5,
        )
        # 进一步过滤：排除名称完全不相关的结果
        if name:
            similar = [
                exp for exp in similar if any(w in exp.name or w in (exp.description or "") for w in name.split())
            ]
        return similar

    @staticmethod
    def list_experiences(
        experience_type: ExperienceType | None,
        name: str | None,
        page: int,
        page_size: int,
        *,
        is_hot: bool | None,
    ) -> tuple[int, list[Experience]]:
        """列出Experience"""
        total_cnt, experiences = ExperienceManager.list_experiences(
            experience_type=experience_type,
            keywords=None,
            name=name,
            is_hot=is_hot,
            page=page,
            page_size=page_size,
        )
        for experience in experiences:
            experience.keywords = KeyWordManager.get_keywords_by_experience_id(
                experience.id,
            )
        return total_cnt, experiences

    @staticmethod
    def delete_experience_by_ids(experience_ids: list[str]) -> None:
        """删除Experience"""
        ExperienceManager.delete_experiences_by_ids(experience_ids)
        for experience_id in experience_ids:
            KeyWordManager.delete_keywords_by_experience_id(experience_id)

    @staticmethod
    def delete_experience_by_source(source: str) -> None:
        """按来源路径删除Experience（软删除）"""
        experience_ids = ExperienceManager.query_experience_ids_by_source(source)
        ExperienceManager.delete_experiences_by_ids(experience_ids)
        for experience_id in experience_ids:
            KeyWordManager.delete_keywords_by_experience_id(experience_id)

    @staticmethod
    def merge_experiences(
        experience_type: ExperienceType,
        base_id: str,
        merge_ids: list[str],
    ) -> Experience:
        """
        合并多个同类型 Experience

        以 base_id 为主，吸收 merge_ids 的关键词与描述，merge_ids 中的 Experience 将被软删除。
        返回合并后的 base Experience。
        """
        if not merge_ids:
            msg = "merge_ids 不能为空"
            raise ValueError(msg)

        # 加载 base 和被合并的经验
        all_ids = [base_id, *merge_ids]
        all_exps = ExperienceManager.query_experience_by_ids(all_ids)
        if len(all_exps) < 2:  # noqa: PLR2004
            msg = "部分 experience_id 不存在或已删除"
            raise ValueError(msg)

        exp_map = {e.id: e for e in all_exps}
        base = exp_map.get(base_id)
        if base is None:
            msg_0 = f"base_id={base_id} 不存在或已删除"
            raise ValueError(msg_0)
        if base.type != experience_type:
            msg_1 = f"base experience 类型不匹配，期望 {experience_type.value}，实际 {base.type.value}"
            raise ValueError(msg_1)

        # 收集被合并经验的数据
        merged_names = []
        merged_descriptions = []
        merged_keyword_sets = set(base.keywords or [])
        for mid in merge_ids:
            me = exp_map.get(mid)
            if me is None:
                continue
            if me.type != experience_type:
                msg_2 = f"合并目标 {mid} 类型不匹配"
                raise ValueError(msg_2)
            merged_names.append(me.name)
            if me.description:
                merged_descriptions.append(me.description)
            for kw in me.keywords or []:
                merged_keyword_sets.add(kw)

        # 合并 name：base_name (merged_from: name1, name2, ...)
        if merged_names:
            base.name = f"{base.name}（合并自：{', '.join(merged_names)}）"

        # 合并 description：用分隔线拼接
        if merged_descriptions:
            parts = [base.description] if base.description else []
            parts.extend(merged_descriptions)
            base.description = "\n---\n".join(parts)
            base.description = ExperienceService.filter_special_characters(
                base.description,
            )

        # 合并 keywords：去重
        base.keywords = list(merged_keyword_sets)

        # 持久化：更新 base + 删除 merge_ids
        ExperienceManager.update_experience(base)
        # 重设 keywords（先删后插）
        KeyWordManager.delete_keywords_by_experience_id(base.id)
        KeyWordManager.add_keywords(base.id, base.keywords)
        # 软删除被合并的经验
        ExperienceManager.delete_experiences_by_ids(merge_ids)
        for mid in merge_ids:
            KeyWordManager.delete_keywords_by_experience_id(mid)

        return base

    @staticmethod
    def optimize_experience(
        experience_id: str,
        name: str | None = None,
        description: str | None = None,
        keywords: list[str] | None = None,
    ) -> Experience:
        """
        优化已有 Experience

        按需更新 name / description / keywords，keywords 若传入则全量替换。
        返回更新后的 Experience。
        """
        exps = ExperienceManager.query_experience_by_ids([experience_id])
        if not exps:
            msg = f"experience_id={experience_id} 不存在或已删除"
            raise ValueError(msg)
        exp = exps[0]
        exp.keywords = KeyWordManager.get_keywords_by_experience_id(experience_id)

        if name is not None:
            exp.name = name
        if description is not None:
            exp.description = ExperienceService.filter_special_characters(description)
        if keywords is not None:
            exp.keywords = keywords

        ExperienceManager.update_experience(exp)
        if keywords is not None:
            KeyWordManager.delete_keywords_by_experience_id(experience_id)
            KeyWordManager.add_keywords(experience_id, keywords)

        return exp

    @staticmethod
    def search_experiences(
        query: str,
        exp_type: ExperienceType,
        fields: list[str] | None = None,
        top_k: int = 5,
        banned_experience_ids: list[str] | None = None,
        experience_ids: list[str] | None = None,
        *,
        is_hot: bool | None = None,
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
        # 过滤纯 ASCII 单字母，避免 c* / a* 等前缀匹配大量误召回
        keywords = [w for w in keywords if not (len(w) == 1 and w.isascii())]
        if not keywords:
            return []

        experiences = ExperienceManager.query_experience_by_fts5_use_description(
            keywords=keywords,
            exp_type=exp_type,
            fields=fields,
            is_hot=is_hot,
            top_k=top_k,
            banned_experience_ids=banned_experience_ids,
            experience_ids=experience_ids,
        )
        for experience in experiences:
            experience.keywords = KeyWordManager.get_keywords_by_experience_id(
                experience.id,
            )
        for experience in experiences:
            ExperienceManager.update_hot_experience(experience.id)
        return experiences
