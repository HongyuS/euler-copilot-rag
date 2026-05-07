import asyncio
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import numpy as np

from common.config import (
    get_commit_local_min_hits,
    get_commit_local_min_similarity,
    get_commit_vector_db_path,
    get_github_commit_repos,
    get_github_max_candidates,
    get_github_rate_limit_delay,
)
from common.embedding import Embedding
from sqlite.commit_sqlite import search_commit_vectors

logger = logging.getLogger(__name__)


def preprocess_text(raw_text: str) -> str:
    text = re.sub(r"<[^>]+>", "", raw_text)
    text = re.sub(r"[\[\]:'(),.]", " ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    stop_words = {"info", "none", "the", "a", "an", "is", "in", "on", "for", "with"}
    words = [w for w in text.split() if w not in stop_words]
    return " ".join(words) if words else text


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    try:
        vec1_array = np.array(vec1)
        vec2_array = np.array(vec2)
        dot_product = np.dot(vec1_array, vec2_array)
        norm1 = np.linalg.norm(vec1_array)
        norm2 = np.linalg.norm(vec2_array)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot_product / (norm1 * norm2))
    except Exception:
        return 0.0


def build_fuzzy_query(core_words: List[str]) -> str:
    return " OR ".join([f"{w}*" for w in core_words])


def extract_core_words(processed_text: str, max_words: int = 5) -> List[str]:
    words = processed_text.split()[:max_words]
    return words if words else []


def _fallback_commit_items(commit_candidates: List[Dict[str, Any]], top_k: int) -> List[Dict[str, Any]]:
    """向量不可用时，补齐 similarity 字段，避免下游 KeyError。"""
    return [
        {
            "summary": item["summary"],
            "api_url": item.get("api_url"),
            "similarity": 0.0,
        }
        for item in commit_candidates[:top_k]
    ]


def _local_result_is_good(results: List[Dict[str, Any]]) -> bool:
    if len(results) < get_commit_local_min_hits():
        return False
    top_similarity = max([item.get("similarity", 0.0) for item in results], default=0.0)
    return top_similarity >= get_commit_local_min_similarity()


async def search_local_commit_vector_db(query: str, top_k: int) -> List[Dict[str, Any]]:
    if not Embedding.is_configured():
        return []
    try:
        query_vector = await Embedding.vectorize_embedding(preprocess_text(query))
        if not query_vector:
            return []
        db_path = get_commit_vector_db_path()
        return search_commit_vectors(db_path, query_vector, top_k)
    except Exception as e:
        logger.warning(f"[OnlineCommit] 本地commit向量库检索失败: {e}")
        return []


async def fetch_github_commits_page(
    session: aiohttp.ClientSession,
    headers: Dict[str, str],
    repo: str,
    query: str,
    per_page: int,
    rate_limit_delay: int,
) -> List[Dict[str, Any]]:
    params = {
        "q": f"{query} repo:{repo} type:commit",
        "per_page": per_page,
        "sort": "updated",
    }
    try:
        await asyncio.sleep(rate_limit_delay)
        async with session.get("https://api.github.com/search/commits", headers=headers, params=params) as res:
            if res.status != 200:
                logger.warning(f"[OnlineCommit] Commit搜索失败，状态码: {res.status}, repo: {repo}")
                return []
            data = await res.json()
            commits = []
            for item in data.get("items", []):
                commit_msg = item["commit"]["message"]
                commits.append(
                    {
                        "summary": commit_msg[:60],
                        "api_url": item["url"],
                        "text": commit_msg,
                    }
                )
            return commits
    except Exception as e:
        logger.warning(f"[OnlineCommit] Commit搜索异常，repo: {repo}, 错误: {str(e)[:50]}")
        return []


async def search_github_commits(
    query: str,
    session: aiohttp.ClientSession,
    headers: Dict[str, str],
) -> List[Dict[str, Any]]:
    processed_text = preprocess_text(query)
    core_words = extract_core_words(processed_text)
    if not core_words:
        return []
    fuzzy_query = build_fuzzy_query(core_words)
    commit_repos = get_github_commit_repos()
    max_candidates = get_github_max_candidates()
    rate_limit_delay = get_github_rate_limit_delay()
    candidates = []
    for repo in commit_repos:
        if len(candidates) >= max_candidates:
            break
        per_page = min(max_candidates - len(candidates), 10)
        candidates.extend(
            await fetch_github_commits_page(session, headers, repo, fuzzy_query, per_page, rate_limit_delay)
        )
    return candidates


async def rerank_commit_candidates(
    query: str,
    commit_candidates: List[Dict[str, Any]],
    top_k: int,
) -> List[Dict[str, Any]]:
    if not commit_candidates:
        return []
    if not Embedding.is_configured():
        return _fallback_commit_items(commit_candidates, top_k)
    try:
        query_vector = await Embedding.vectorize_embedding(preprocess_text(query))
        if not query_vector:
            return _fallback_commit_items(commit_candidates, top_k)
        commit_texts = [preprocess_text(commit["text"]) for commit in commit_candidates]
        commit_vectors = await Embedding.vectorize_embeddings_batch(commit_texts, max_concurrent=5)
        similarities = []
        for vector in commit_vectors:
            similarities.append(cosine_similarity(query_vector, vector) if vector else 0.0)
        sorted_indices = np.argsort(similarities)[::-1][:top_k]
        return [
            {
                "summary": commit_candidates[i]["summary"],
                "api_url": commit_candidates[i].get("api_url"),
                "similarity": round(similarities[i], 3),
            }
            for i in sorted_indices
        ]
    except Exception as e:
        logger.warning(f"[OnlineCommit] 向量精排失败: {e}")
        return _fallback_commit_items(commit_candidates, top_k)


async def _fetch_commit_content(
    session: aiohttp.ClientSession,
    headers: Dict[str, str],
    api_url: Optional[str],
) -> str:
    if not api_url:
        return ""
    try:
        async with session.get(api_url, headers=headers) as res:
            if res.status != 200:
                return ""
            data = await res.json()
            return (data.get("commit", {}).get("message") or "").strip()
    except Exception:
        return ""


async def _enrich_commits_with_content(
    session: aiohttp.ClientSession,
    headers: Dict[str, str],
    commits: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    if not commits:
        return []
    tasks = [_fetch_commit_content(session, headers, commit.get("api_url")) for commit in commits]
    contents = await asyncio.gather(*tasks, return_exceptions=True)
    enriched = []
    for commit, content in zip(commits, contents):
        content_str = "" if isinstance(content, Exception) else content
        enriched.append(
            {
                "summary": commit["summary"],
                "content": content_str,
                "similarity": commit["similarity"],
            }
        )
    return enriched


async def search_commits_online_or_local(
    query: str,
    top_k: int,
    session: aiohttp.ClientSession,
    headers: Dict[str, str],
) -> Tuple[List[Dict[str, Any]], Optional[Exception]]:
    try:
        local_results = await search_local_commit_vector_db(query, top_k)
        if _local_result_is_good(local_results):
            return [
                {
                    "summary": item["summary"],
                    "content": item["content"],
                    "similarity": item["similarity"],
                }
                for item in local_results[:top_k]
            ], None

        commit_candidates = await search_github_commits(query, session, headers)
        reranked_commits = await rerank_commit_candidates(query, commit_candidates, top_k)
        enriched_commits = await _enrich_commits_with_content(session, headers, reranked_commits)
        return enriched_commits, None
    except Exception as e:
        logger.exception(f"[OnlineCommit] 检索失败: {e}")
        return [], e
