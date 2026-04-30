"""
线上检索编排模块
- issue 检索由 online_issue_search 负责
- commit 检索由 online_commit_search 负责（本地向量库优先）
"""
import asyncio
import logging
from typing import Any, Dict

import aiohttp

from common.config import get_github_request_timeout, get_github_token
from .online_commit_search import search_commits_online_or_local
from .online_issue_search import search_issues_online

logger = logging.getLogger(__name__)


async def search_github_online(query: str, top_k: int = 2) -> Dict[str, Any]:
    token = get_github_token()
    if not token:
        return {
            "success": False,
            "error_message": "GitHub Token未配置",
            "issues": [],
            "commits": [],
        }

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "RAG-GitHub-Search/1.0",
        "Authorization": f"token {token}",
    }

    timeout = aiohttp.ClientTimeout(total=get_github_request_timeout())
    connector = aiohttp.TCPConnector(ssl=False)

    try:
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            issue_task = search_issues_online(query, top_k, session, headers)
            commit_task = search_commits_online_or_local(query, top_k, session, headers)
            (issues, issue_err), (commits, commit_err) = await asyncio.gather(
                issue_task, commit_task, return_exceptions=False
            )

            errors = []
            if issue_err:
                errors.append(f"issues: {issue_err}")
            if commit_err:
                errors.append(f"commits: {commit_err}")

            return {
                "success": len(errors) == 0,
                "error_message": "; ".join(errors) if errors else None,
                "issues": issues,
                "commits": commits,
            }
    except Exception as e:
        logger.exception(f"[OnlineSearch] GitHub检索失败: {e}")
        return {
            "success": False,
            "error_message": str(e),
            "issues": [],
            "commits": [],
        }
