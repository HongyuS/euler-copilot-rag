"""
更新 commit 本地向量库脚本

用法示例：
python test/update_commit_vector_db.py --full --max-pages 20
python test/update_commit_vector_db.py --since-days 7 --max-pages 5
"""
import argparse
import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import aiohttp

# 允许在 test 目录直接运行时导入 src 下模块
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from common.config import (
    get_github_commit_repos,
    get_github_token,
    get_commit_vector_db_path,
    get_embedding_batch_size,
)
from common.embedding import Embedding
from sqlite.commit_sqlite import init_commit_vector_db, upsert_commit_records


def _log(msg: str) -> None:
    """带时间戳的进度输出，立即刷新，便于长时间任务观察进度。"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def _build_since_iso(since_days: Optional[int], full: bool) -> Optional[str]:
    if full:
        return None
    days = 30 if since_days is None else max(1, since_days)
    since_dt = datetime.now(timezone.utc) - timedelta(days=days)
    return since_dt.isoformat().replace("+00:00", "Z")


async def _fetch_repo_commits(
    session: aiohttp.ClientSession,
    headers: Dict[str, str],
    repo: str,
    since: Optional[str],
    max_pages: int,
    repo_idx: int,
    repo_total: int,
) -> List[Dict[str, Any]]:
    all_items: List[Dict[str, Any]] = []
    label = f"[{repo_idx}/{repo_total}] {repo}"
    _log(f"{label} 开始拉取 commits（最多 {max_pages} 页，每页最多 100 条）…")
    for page in range(1, max_pages + 1):
        params = {"per_page": 100, "page": page}
        if since:
            params["since"] = since
        url = f"https://api.github.com/repos/{repo}/commits"
        _log(f"{label} 请求第 {page}/{max_pages} 页…")
        async with session.get(url, headers=headers, params=params) as res:
            if res.status != 200:
                text = await res.text()
                _log(f"{label} [WARN] 第 {page} 页失败 status={res.status} body={text[:160]}")
                break
            data = await res.json()
            if not data:
                _log(f"{label} 第 {page} 页无数据，结束拉取")
                break
            all_items.extend(data)
            _log(f"{label} 第 {page} 页收到 {len(data)} 条，累计 {len(all_items)} 条")
            if len(data) < 100:
                _log(f"{label} 本页不足 100 条，已到末尾")
                break
    _log(f"{label} 拉取结束，共 {len(all_items)} 条 commit")
    return all_items


def _to_record(repo: str, item: Dict[str, Any]) -> Dict[str, Any]:
    sha = item.get("sha", "")
    commit_obj = item.get("commit", {}) or {}
    message = (commit_obj.get("message") or "").strip()
    author_date = (commit_obj.get("author", {}) or {}).get("date")
    summary = message[:120] if message else sha[:12]
    api_url = item.get("url")
    return {
        "repo": repo,
        "sha": sha,
        "summary": summary,
        "content": message or summary,
        "author_date": author_date,
        "api_url": api_url,
    }


async def _embed_records(
    records: List[Dict[str, Any]],
    progress_label: str,
) -> List[Dict[str, Any]]:
    if not records:
        return records
    bs = max(1, get_embedding_batch_size())
    n = len(records)
    total_batches = (n + bs - 1) // bs
    _log(f"{progress_label} 开始向量化，共 {n} 条，每批 {bs} 条，约 {total_batches} 批…")
    result: List[Dict[str, Any]] = []
    for batch_idx, start in enumerate(range(0, n, bs), start=1):
        end = min(start + bs, n)
        batch = records[start:end]
        texts = [f"{r['repo']} {r['summary']} {r['content']}" for r in batch]
        _log(
            f"{progress_label} 向量化 第 {batch_idx}/{total_batches} 批 "
            f"（条目 {start + 1}-{end}/{n}）…"
        )
        vectors = await Embedding.vectorize_embeddings_batch(texts)
        ok = 0
        for rec, vec in zip(batch, vectors):
            if not vec:
                continue
            new_rec = rec.copy()
            new_rec["embedding"] = vec
            result.append(new_rec)
            ok += 1
        _log(f"{progress_label} 第 {batch_idx} 批完成，本批成功 {ok}/{len(batch)} 条，累计带向量 {len(result)} 条")
    return result


async def run(full: bool, since_days: Optional[int], max_pages: int) -> None:
    token = get_github_token()
    if not token:
        raise RuntimeError("GitHub token 未配置，请先设置 config.toml 或 GITHUB_TOKEN")
    if not Embedding.is_configured():
        raise RuntimeError("Embedding 未配置，无法构建 commit 向量库")

    db_path = get_commit_vector_db_path()
    repos = get_github_commit_repos()
    since = _build_since_iso(since_days, full)
    repo_total = len(repos)

    mode = "全量" if full else f"增量（最近 {since_days or 7} 天）"
    _log("========== commit 向量库更新 开始 ==========")
    _log(f"模式: {mode}")
    _log(f"向量库路径: {db_path}")
    _log(f"待处理仓库数: {repo_total}，每仓库最多页数: {max_pages}")
    if since:
        _log(f"GitHub since 参数: {since}")
    else:
        _log("GitHub since: 未设置（全量拉取可用页数内数据）")

    _log("初始化数据库表结构…")
    init_commit_vector_db(db_path)
    _log("数据库就绪")

    timeout = aiohttp.ClientTimeout(total=120)
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "RAG-Commit-Indexer/1.0",
        "Authorization": f"token {token}",
    }
    total_upserted = 0
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for repo_idx, repo in enumerate(repos, start=1):
            label = f"[{repo_idx}/{repo_total}] {repo}"
            _log(f"---------- 仓库 {repo_idx}/{repo_total}: {repo} ----------")
            items = await _fetch_repo_commits(
                session, headers, repo, since, max_pages, repo_idx, repo_total
            )
            records = [_to_record(repo, item) for item in items if item.get("sha")]
            _log(f"{label} 解析为记录 {len(records)} 条（有 sha）")
            records_with_vec = await _embed_records(records, label)
            _log(f"{label} 写入 SQLite…")
            count = upsert_commit_records(db_path, records_with_vec)
            total_upserted += count
            _log(
                f"{label} 本仓库完成：原始 {len(records)} 条，"
                f"带向量 {len(records_with_vec)} 条，写入 {count} 条；"
                f"全局累计写入 {total_upserted} 条"
            )

    _log(f"========== commit 向量库更新 结束，总写入: {total_upserted} ==========")


def main() -> None:
    parser = argparse.ArgumentParser(description="更新 commit 向量数据库")
    parser.add_argument("--full", action="store_true", help="全量更新（忽略 since-days）")
    parser.add_argument("--since-days", type=int, default=7, help="增量更新最近 N 天（默认 7）")
    parser.add_argument("--max-pages", type=int, default=10, help="每个仓库最多拉取页数（每页 100）")
    args = parser.parse_args()
    asyncio.run(run(full=args.full, since_days=args.since_days, max_pages=args.max_pages))


if __name__ == "__main__":
    main()
