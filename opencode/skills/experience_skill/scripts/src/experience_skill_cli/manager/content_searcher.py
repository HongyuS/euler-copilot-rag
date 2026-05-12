"""正文内容搜索器。

支持 ripgrep(rg) → Python 原生 三级自动降级：
  1. rg --json（最快，结构化输出）
  2. Python 逐文件扫描（无额外依赖）
"""

from __future__ import annotations

import json
import logging
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path  # noqa: TC003 (used at runtime)

from experience_skill_cli.common.exprience import SKILL_ROOT
from experience_skill_cli.schema.enum import ExperienceType

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------


@dataclass
class ContentSnippet:
    """正文匹配片段。"""

    line_num: int
    content: str
    match_start: int = 0
    match_end: int = 0


@dataclass
class ContentMatch:
    """单篇文档的正文匹配结果。"""

    source: str  # 与 experience_table.source 对应的相对路径
    score: float  # 0.0 ~ 1.0 归一化得分
    snippets: list[ContentSnippet] = field(default_factory=list)
    hit_count: int = 0
    file_path: str = ""  # 文件系统绝对路径


# ---------------------------------------------------------------------------
# 搜索器
# ---------------------------------------------------------------------------


class ContentSearcher:
    """正文内容搜索器，自动选择最优搜索后端。"""

    # 匹配片段最大数量
    _MAX_SNIPPETS: int = 5
    # 搜索超时（秒）
    _SEARCH_TIMEOUT: int = 30

    # ------------------------------------------------------------------
    # 后端检测
    # ------------------------------------------------------------------

    @staticmethod
    def _rg_available() -> bool:
        """检测 ripgrep 是否可用。"""
        try:
            subprocess.run(
                ["rg", "--version"],
                capture_output=True,
                timeout=5,
                check=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
        else:
            return True

    # ------------------------------------------------------------------
    # 辅助方法
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_front_matter(text: str) -> str:
        """去除 YAML front matter（---...---），返回正文部分。

        仅处理文档开头的 front matter，正文中出现的 --- 不受影响。
        """
        m = re.match(r"^---\s*\n.*?\n---\s*\n", text, re.DOTALL)
        if m:
            return text[m.end() :]
        return text

    @staticmethod
    def resolve_md_file(source: str, exp_type: ExperienceType) -> Path | None:
        """根据 source 路径解析实际 markdown 文件。

        - SKILL: data/skill_hub/<name>/skill_def.md
        - WIKI:  data/wiki_hub/<name>.md
        """
        p = SKILL_ROOT / source / "skill_def.md" if exp_type == ExperienceType.SKILL else SKILL_ROOT / source
        return p if p.exists() else None

    @staticmethod
    def get_all_sources(exp_type: ExperienceType) -> list[str]:
        """获取指定类型所有已注册经验的 source 路径列表（去重）。"""
        from experience_skill_cli.sqlite import (  # noqa: PLC0415
            AsyncSQLiteSingleton,
        )

        db = AsyncSQLiteSingleton()
        rows = db.query(
            "SELECT DISTINCT source FROM experience_table WHERE type = ? AND status = ?",
            (exp_type.value, "existed"),
        )
        return [r["source"] for r in rows]

    # ------------------------------------------------------------------
    # ripgrep 后端
    # ------------------------------------------------------------------

    @staticmethod
    def _search_with_rg(
        query: str,
        target_paths: list[Path],
    ) -> dict[str, list[dict]]:
        """使用 ripgrep --json 搜索，返回按路径分组的匹配列表。"""
        cmd = [
            "rg",
            "--json",
            "--ignore-case",
            "--no-heading",
            "--fixed-strings",  # 字面匹配，避免 regex 特殊字符问题
            "--",
            query,
        ]
        cmd.extend([str(p) for p in target_paths])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=ContentSearcher._SEARCH_TIMEOUT,
                check=False,
            )
        except subprocess.TimeoutExpired:
            logger.warning("ripgrep 搜索超时（%ds）", ContentSearcher._SEARCH_TIMEOUT)
            return {}
        except Exception:
            logger.exception("ripgrep 搜索异常")
            return {}

        matches_by_path: dict[str, list[dict]] = {}
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            if entry.get("type") == "match":
                data = entry["data"]
                path = data["path"]["text"]
                if path not in matches_by_path:
                    matches_by_path[path] = []
                matches_by_path[path].append(data)

        return matches_by_path

    # ------------------------------------------------------------------
    # Python 原生后端（fallback）
    # ------------------------------------------------------------------

    @staticmethod
    def _search_with_python(
        query: str,
        target_paths: list[Path],
    ) -> dict[str, list[dict]]:
        """Python 原生逐文件行扫描（ripgrep 不可用时的 fallback）。

        跳过 YAML front matter，仅搜索正文部分。
        """
        query_lower = query.lower()
        matches_by_path: dict[str, list[dict]] = {}

        for file_path in target_paths:
            try:
                raw_text = file_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            # 跳过 front matter，仅搜索正文
            body = ContentSearcher._strip_front_matter(raw_text)
            body_lines = body.split("\n")

            file_matches: list[dict] = []
            for line_idx, line_text in enumerate(body_lines):
                pos = line_text.lower().find(query_lower)
                if pos != -1:
                    file_matches.append(
                        {
                            "line_number": line_idx + 1,
                            "lines": {"text": line_text},
                            "submatches": [
                                {"start": pos, "end": pos + len(query_lower)},
                            ],
                        },
                    )

            if file_matches:
                matches_by_path[str(file_path)] = file_matches

        return matches_by_path

    # ------------------------------------------------------------------
    # 公开接口
    # ------------------------------------------------------------------

    @staticmethod
    def search(
        query: str,
        sources: list[str],
        exp_type: ExperienceType,
    ) -> list[ContentMatch]:
        """对指定 source 列表进行正文内容搜索。

        Args:
            query: 原始搜索关键词（支持中文、英文、拼音）
            sources: 待搜索的 source 相对路径列表
            exp_type: 经验类型（SKILL / WIKI）

        Returns:
            ContentMatch 列表，按得分降序排列。

        """
        query_str = query.strip()
        if not query_str or not sources:
            return []

        # 解析文件路径
        path_to_source: dict[str, str] = {}
        target_paths: list[Path] = []
        for src in sources:
            p = ContentSearcher.resolve_md_file(src, exp_type)
            if p is not None:
                # 用 resolved 的绝对路径做 key（避免符号链接差异）
                target_paths.append(p)
                path_to_source[str(p)] = src

        if not target_paths:
            return []

        # 选择后端并搜索
        use_rg = ContentSearcher._rg_available()
        if use_rg:
            raw_matches = ContentSearcher._search_with_rg(query_str, target_paths)
        else:
            raw_matches = ContentSearcher._search_with_python(query_str, target_paths)

        if not raw_matches:
            return []

        # 归一化得分：以最大命中数为基准
        max_hits = max((len(v) for v in raw_matches.values()), default=1)

        results: list[ContentMatch] = []
        for path_str, hits in raw_matches.items():
            src = path_to_source.get(path_str, path_str)
            score = round(len(hits) / max(max_hits, 1), 4)

            snippets: list[ContentSnippet] = []
            for h in hits[: ContentSearcher._MAX_SNIPPETS]:
                line_num = h.get("line_number", 0)
                content = h.get("lines", {}).get("text", "")
                submatches = h.get("submatches", [])
                match_start = submatches[0]["start"] if submatches else 0
                match_end = submatches[0]["end"] if submatches else 0
                snippets.append(
                    ContentSnippet(
                        line_num=line_num,
                        content=content.strip(),
                        match_start=match_start,
                        match_end=match_end,
                    ),
                )

            results.append(
                ContentMatch(
                    source=src,
                    score=score,
                    snippets=snippets,
                    hit_count=len(hits),
                    file_path=path_str,
                ),
            )

        # 按得分降序
        results.sort(key=lambda x: x.score, reverse=True)
        return results

    @staticmethod
    def search_all(
        query: str,
        exp_type: ExperienceType,
    ) -> list[ContentMatch]:
        """搜索指定类型的所有已注册经验的正文内容。

        这是 search() 的便捷封装，自动从 DB 获取所有 source 列表。
        """
        all_sources = ContentSearcher.get_all_sources(exp_type)
        return ContentSearcher.search(query, all_sources, exp_type)
