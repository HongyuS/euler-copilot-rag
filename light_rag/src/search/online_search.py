"""
线上检索模块
支持在GitHub上搜索相关的Issues和Commits，并使用向量相似度进行精排
"""
import asyncio
import re
import logging

from typing import List, Dict, Any, Optional, Tuple

import aiohttp
import numpy as np
from common.config import (
    get_github_token,
    get_github_issue_repos,
    get_github_commit_repo,
    get_github_max_candidates,
    get_github_request_timeout,
    get_github_rate_limit_delay,
)
from common.embedding import Embedding

logger = logging.getLogger(__name__)


def preprocess_text(raw_text: str) -> str:
    """
    预处理文本：移除特殊符号，保留核心语义
    :param raw_text: 原始文本
    :return: 预处理后的文本
    """
    # 移除 <num>/[ ]/:/'/() 等特殊符号
    text = re.sub(r'<[^>]+>', '', raw_text)
    text = re.sub(r'[\[\]:\'(),.]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    # 过滤无意义停用词
    stop_words = {"info", "none", "the", "a", "an", "is", "in", "on", "for", "with"}
    words = [w for w in text.split() if w not in stop_words]
    return " ".join(words) if words else text


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    计算两个向量的余弦相似度
    :param vec1: 向量1
    :param vec2: 向量2
    :return: 相似度分数（0-1之间）
    """
    try:
        vec1_array = np.array(vec1)
        vec2_array = np.array(vec2)
        dot_product = np.dot(vec1_array, vec2_array)
        norm1 = np.linalg.norm(vec1_array)
        norm2 = np.linalg.norm(vec2_array)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot_product / (norm1 * norm2))
    except Exception as e:
        logger.warning(f"[OnlineSearch] 计算余弦相似度失败: {e}")
        return 0.0


def build_fuzzy_query(core_words: List[str]) -> str:
    """
    构建模糊查询字符串
    :param core_words: 核心关键词列表
    :return: 模糊查询字符串
    """
    return " OR ".join([f"{w}*" for w in core_words])


def extract_core_words(processed_text: str, max_words: int = 5) -> List[str]:
    """
    提取核心关键词
    :param processed_text: 预处理后的文本
    :param max_words: 最大关键词数量
    :return: 核心关键词列表
    """
    words = processed_text.split()[:max_words]
    return words if words else []


async def fetch_github_issues_page(
    session: aiohttp.ClientSession,
    headers: Dict[str, str],
    repo: str,
    query: str,
    per_page: int,
    rate_limit_delay: int
) -> List[Dict[str, Any]]:
    """
    获取GitHub Issues的一页结果
    :param session: aiohttp会话
    :param headers: HTTP请求头
    :param repo: 仓库名称
    :param query: 查询字符串
    :param per_page: 每页数量
    :param rate_limit_delay: 请求间隔
    :return: Issue列表
    """
    params = {
        "q": f"{query} repo:{repo} type:issue",
        "per_page": per_page,
        "sort": "relevance"
    }
    
    try:
        await asyncio.sleep(rate_limit_delay)
        async with session.get(
            "https://api.github.com/search/issues",
            headers=headers,
            params=params
        ) as res:
            if res.status != 200:
                logger.warning(f"[OnlineSearch] Issue搜索失败，状态码: {res.status}, repo: {repo}")
                return []
            
            data = await res.json()
            issues = []
            for item in data.get("items", []):
                issues.append({
                    "repo": repo,
                    "title": item["title"],
                    # GitHub API 详情地址，用于后续获取完整内容
                    "api_url": item["url"],
                    # 向量检索使用的文本：标题 + 正文前100字符
                    "text": item["title"] + " " + (item.get("body", "")[:100] if item.get("body") else "")
                })
            return issues
    except Exception as e:
        logger.warning(f"[OnlineSearch] Issue搜索异常，repo: {repo}, 错误: {str(e)[:50]}")
        return []


async def search_github_issues(
    query: str,
    session: aiohttp.ClientSession,
    headers: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    搜索GitHub Issues
    :param query: 查询文本
    :param session: aiohttp会话
    :param headers: HTTP请求头
    :return: Issue候选列表
    """
    processed_text = preprocess_text(query)
    core_words = extract_core_words(processed_text)
    if not core_words:
        return []
    
    fuzzy_query = build_fuzzy_query(core_words)
    issue_repos = get_github_issue_repos()
    max_candidates = get_github_max_candidates()
    rate_limit_delay = get_github_rate_limit_delay()
    
    candidates = []
    for repo in issue_repos:
        if len(candidates) >= max_candidates:
            break
        
        per_page = min(max_candidates - len(candidates), 10)
        issues = await fetch_github_issues_page(
            session, headers, repo, fuzzy_query, per_page, rate_limit_delay
        )
        candidates.extend(issues)
    
    return candidates


async def fetch_github_commits_page(
    session: aiohttp.ClientSession,
    headers: Dict[str, str],
    repo: str,
    query: str,
    per_page: int,
    rate_limit_delay: int
) -> List[Dict[str, Any]]:
    """
    获取GitHub Commits的一页结果
    :param session: aiohttp会话
    :param headers: HTTP请求头
    :param repo: 仓库名称
    :param query: 查询字符串
    :param per_page: 每页数量
    :param rate_limit_delay: 请求间隔
    :return: Commit列表
    """
    params = {
        "q": f"{query} repo:{repo} type:commit",
        "per_page": per_page,
        "sort": "updated"
    }
    
    try:
        await asyncio.sleep(rate_limit_delay)
        async with session.get(
            "https://api.github.com/search/commits",
            headers=headers,
            params=params
        ) as res:
            if res.status != 200:
                logger.warning(f"[OnlineSearch] Commit搜索失败，状态码: {res.status}")
                return []
            
            data = await res.json()
            commits = []
            for item in data.get("items", []):
                commit_msg = item["commit"]["message"]
                commits.append({
                    "summary": commit_msg[:60],
                    # GitHub API 详情地址，用于后续获取完整内容
                    "api_url": item["url"],
                    # 向量检索使用的文本：完整提交信息
                    "text": commit_msg
                })
            return commits
    except Exception as e:
        logger.warning(f"[OnlineSearch] Commit搜索异常，错误: {str(e)[:50]}")
        return []


async def search_github_commits(
    query: str,
    session: aiohttp.ClientSession,
    headers: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    搜索GitHub Commits
    :param query: 查询文本
    :param session: aiohttp会话
    :param headers: HTTP请求头
    :return: Commit候选列表
    """
    processed_text = preprocess_text(query)
    core_words = extract_core_words(processed_text)
    if not core_words:
        return []
    
    fuzzy_query = build_fuzzy_query(core_words)
    commit_repo = get_github_commit_repo()
    max_candidates = get_github_max_candidates()
    rate_limit_delay = get_github_rate_limit_delay()
    
    candidates = []
    per_page = min(max_candidates, 10)
    commits = await fetch_github_commits_page(
        session, headers, commit_repo, fuzzy_query, per_page, rate_limit_delay
    )
    candidates.extend(commits)
    
    return candidates


def calculate_similarities(
    query_vector: List[float],
    candidate_vectors: List[Optional[List[float]]]
) -> List[float]:
    """
    计算候选向量与查询向量的相似度列表
    :param query_vector: 查询向量
    :param candidate_vectors: 候选向量列表
    :return: 相似度列表
    """
    similarities = []
    for vector in candidate_vectors:
        if vector:
            sim = cosine_similarity(query_vector, vector)
            similarities.append(sim)
        else:
            similarities.append(0.0)
    return similarities


async def rerank_issues(
    query_vector: List[float],
    issue_candidates: List[Dict[str, Any]],
    top_k: int
) -> List[Dict[str, Any]]:
    """
    对Issue候选进行向量精排
    :param query_vector: 查询向量
    :param issue_candidates: Issue候选列表
    :param top_k: 返回数量
    :return: 精排后的Issue列表
    """
    if not issue_candidates:
        return []
    
    issue_texts = [preprocess_text(issue["text"]) for issue in issue_candidates]
    issue_vectors = await Embedding.vectorize_embeddings_batch(issue_texts, max_concurrent=5)
    similarities = calculate_similarities(query_vector, issue_vectors)
    
    sorted_indices = np.argsort(similarities)[::-1][:top_k]
    return [
        {
            "repo": issue_candidates[i]["repo"],
            "title": issue_candidates[i]["title"],
            # 保留 api_url，后续用于获取完整内容
            "api_url": issue_candidates[i].get("api_url"),
            "similarity": round(similarities[i], 3)
        }
        for i in sorted_indices
    ]


async def rerank_commits(
    query_vector: List[float],
    commit_candidates: List[Dict[str, Any]],
    top_k: int
) -> List[Dict[str, Any]]:
    """
    对Commit候选进行向量精排
    :param query_vector: 查询向量
    :param commit_candidates: Commit候选列表
    :param top_k: 返回数量
    :return: 精排后的Commit列表
    """
    if not commit_candidates:
        return []
    
    commit_texts = [preprocess_text(commit["text"]) for commit in commit_candidates]
    commit_vectors = await Embedding.vectorize_embeddings_batch(commit_texts, max_concurrent=5)
    similarities = calculate_similarities(query_vector, commit_vectors)
    
    sorted_indices = np.argsort(similarities)[::-1][:top_k]
    return [
        {
            "summary": commit_candidates[i]["summary"],
            # 保留 api_url，后续用于获取完整内容
            "api_url": commit_candidates[i].get("api_url"),
            "similarity": round(similarities[i], 3)
        }
        for i in sorted_indices
    ]


async def vector_rerank_github(
    query: str,
    issue_candidates: List[Dict[str, Any]],
    commit_candidates: List[Dict[str, Any]],
    top_k: int
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    使用向量相似度对GitHub搜索结果进行精排
    :param query: 查询文本
    :param issue_candidates: Issue候选列表
    :param commit_candidates: Commit候选列表
    :param top_k: 返回数量
    :return: (精排后的Issue列表, 精排后的Commit列表)
    """
    if not Embedding.is_configured():
        logger.warning("[OnlineSearch] Embedding未配置，跳过向量精排")
        return issue_candidates[:top_k], commit_candidates[:top_k]
    
    try:
        query_vector = await Embedding.vectorize_embedding(preprocess_text(query))
        if not query_vector:
            logger.warning("[OnlineSearch] 查询文本向量化失败")
            return issue_candidates[:top_k], commit_candidates[:top_k]
        
        reranked_issues = await rerank_issues(query_vector, issue_candidates, top_k)
        reranked_commits = await rerank_commits(query_vector, commit_candidates, top_k)
        
        return reranked_issues, reranked_commits
    except Exception as e:
        logger.exception(f"[OnlineSearch] 向量精排失败: {e}")
        return issue_candidates[:top_k], commit_candidates[:top_k]


async def _fetch_issue_content(
    session: aiohttp.ClientSession,
    headers: Dict[str, str],
    api_url: Optional[str]
) -> str:
    """
    根据 Issue 的 API 地址获取完整内容（标题 + 正文）
    """
    if not api_url:
        return ""
    try:
        async with session.get(api_url, headers=headers) as res:
            if res.status != 200:
                logger.warning(f"[OnlineSearch] 获取Issue详情失败，状态码: {res.status}")
                return ""
            data = await res.json()
            title = data.get("title") or ""
            body = data.get("body") or ""
            content_parts = [part for part in [title, body] if part]
            return "\n\n".join(content_parts).strip()
    except Exception as e:
        logger.warning(f"[OnlineSearch] 获取Issue详情异常: {str(e)[:50]}")
        return ""


async def _fetch_commit_content(
    session: aiohttp.ClientSession,
    headers: Dict[str, str],
    api_url: Optional[str]
) -> str:
    """
    根据 Commit 的 API 地址获取完整提交信息（commit message）
    """
    if not api_url:
        return ""
    try:
        async with session.get(api_url, headers=headers) as res:
            if res.status != 200:
                logger.warning(f"[OnlineSearch] 获取Commit详情失败，状态码: {res.status}")
                return ""
            data = await res.json()
            message = data.get("commit", {}).get("message") or ""
            return message.strip()
    except Exception as e:
        logger.warning(f"[OnlineSearch] 获取Commit详情异常: {str(e)[:50]}")
        return ""


async def _enrich_issues_with_content(
    session: aiohttp.ClientSession,
    headers: Dict[str, str],
    issues: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    为 Issue 结果补充 content 字段（使用 GitHub API 获取详情）
    """
    if not issues:
        return []
    
    tasks = [
        _fetch_issue_content(session, headers, issue.get("api_url"))
        for issue in issues
    ]
    contents = await asyncio.gather(*tasks, return_exceptions=True)
    
    enriched = []
    for issue, content in zip(issues, contents):
        if isinstance(content, Exception):
            logger.warning(f"[OnlineSearch] 获取Issue内容任务异常: {content}")
            content_str = ""
        else:
            content_str = content
        enriched.append({
            "repo": issue["repo"],
            "title": issue["title"],
            "content": content_str,
            "similarity": issue["similarity"],
        })
    return enriched


async def _enrich_commits_with_content(
    session: aiohttp.ClientSession,
    headers: Dict[str, str],
    commits: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    为 Commit 结果补充 content 字段（使用 GitHub API 获取详情）
    """
    if not commits:
        return []
    
    tasks = [
        _fetch_commit_content(session, headers, commit.get("api_url"))
        for commit in commits
    ]
    contents = await asyncio.gather(*tasks, return_exceptions=True)
    
    enriched = []
    for commit, content in zip(commits, contents):
        if isinstance(content, Exception):
            logger.warning(f"[OnlineSearch] 获取Commit内容任务异常: {content}")
            content_str = ""
        else:
            content_str = content
        enriched.append({
            "summary": commit["summary"],
            "content": content_str,
            "similarity": commit["similarity"],
        })
    return enriched


async def search_github_online(query: str, top_k: int = 2) -> Dict[str, Any]:
    """
    GitHub线上检索主函数
    :param query: 查询文本
    :param top_k: 返回数量
    :return: 检索结果字典
    """
    token = get_github_token()
    if not token:
        return {
            "success": False,
            "error_message": "GitHub Token未配置",
            "issues": [],
            "commits": []
        }
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "RAG-GitHub-Search/1.0",
        "Authorization": f"token {token}"
    }
    
    timeout = aiohttp.ClientTimeout(total=get_github_request_timeout())
    connector = aiohttp.TCPConnector(ssl=False)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            issue_candidates, commit_candidates = await asyncio.gather(
                search_github_issues(query, session, headers),
                search_github_commits(query, session, headers),
                return_exceptions=True
            )
            
            if isinstance(issue_candidates, Exception):
                logger.exception(f"[OnlineSearch] Issue搜索异常: {issue_candidates}")
                issue_candidates = []
            if isinstance(commit_candidates, Exception):
                logger.exception(f"[OnlineSearch] Commit搜索异常: {commit_candidates}")
                commit_candidates = []
            
            reranked_issues, reranked_commits = await vector_rerank_github(
                query, issue_candidates, commit_candidates, top_k
            )
            # 使用 GitHub API 获取每个 Issue / Commit 的具体内容
            enriched_issues = await _enrich_issues_with_content(session, headers, reranked_issues)
            enriched_commits = await _enrich_commits_with_content(session, headers, reranked_commits)
            
            return {
                "success": True,
                "error_message": None,
                "issues": enriched_issues,
                "commits": enriched_commits
            }
    except Exception as e:
        logger.exception(f"[OnlineSearch] GitHub检索失败: {e}")
        return {
            "success": False,
            "error_message": str(e),
            "issues": [],
            "commits": []
        }
