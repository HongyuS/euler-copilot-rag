#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
online-search 召回率评测脚本

功能：
1) 自动从 config 中配置的 GitHub 仓库拉取 issue/commit 样本
2) 自动生成评测 query（无需手工标注）
3) 调用 light_rag 的 search_github_online 进行检索
4) 输出 Recall@1 / Recall@3 / Recall@5
5) 保存评测样本与报告到 test 目录

运行：
python test/eval_online_search_recall.py
python test/eval_online_search_recall.py --issue-per-repo 2 --commit-per-repo 2 --max-k 5
"""
import argparse
import asyncio
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp


# 允许直接从 test 目录运行
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from common.config import (  # noqa: E402
    get_github_token,
    get_github_issue_repos,
    get_github_commit_repos,
    get_github_request_timeout,
    get_commit_vector_db_path,
)
from search.online_search import search_github_online  # noqa: E402
from common.embedding import Embedding  # noqa: E402
from sqlite.commit_sqlite import init_commit_vector_db, upsert_commit_records  # noqa: E402


STOP_WORDS = {
    "the", "and", "for", "with", "from", "that", "this", "when", "while",
    "into", "after", "before", "cannot", "could", "should", "would", "have",
    "has", "had", "are", "was", "were", "not", "but", "you", "your", "its",
    "error", "issue", "fix", "fails", "failed",
}


@dataclass
class EvalSample:
    sample_type: str  # "issue" | "commit"
    repo: str
    query: str
    target_title: Optional[str] = None
    target_message: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


def _log(msg: str) -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def normalize_text(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_query(text: str, max_terms: int = 8) -> str:
    words = normalize_text(text).split()
    words = [w for w in words if len(w) >= 2 and w not in STOP_WORDS and not w.isdigit()]
    if not words:
        return (text or "").strip()[:80]
    return " ".join(words[:max_terms])


def is_issue_hit(target_title: str, returned_title: str) -> bool:
    t = normalize_text(target_title)
    r = normalize_text(returned_title)
    return bool(t and r and (t == r or t in r or r in t))


def is_commit_hit(target_message: str, returned_summary: str) -> bool:
    t = normalize_text(target_message)
    r = normalize_text(returned_summary)
    if not t or not r:
        return False
    # commit summary 可能来自线上(前60字符)或本地向量库(更长)
    if r in t or t[:100] in r:
        return True
    t_words = set(t.split())
    r_words = set(r.split())
    if not t_words or not r_words:
        return False
    inter = len(t_words & r_words)
    ratio_t = inter / max(1, len(t_words))
    ratio_r = inter / max(1, len(r_words))
    # 允许“高重合”作为命中，降低对标题截断的苛刻度
    return ratio_t >= 0.6 or ratio_r >= 0.8


async def fetch_recent_issues(
    session: aiohttp.ClientSession,
    headers: Dict[str, str],
    repo: str,
    per_repo: int,
) -> List[EvalSample]:
    url = f"https://api.github.com/repos/{repo}/issues"
    params = {"state": "all", "sort": "updated", "direction": "desc", "per_page": 30}
    samples: List[EvalSample] = []
    try:
        async with session.get(url, headers=headers, params=params) as res:
            if res.status != 200:
                _log(f"[WARN] issue样本拉取失败 repo={repo}, status={res.status}")
                return samples
            data = await res.json()
    except Exception as e:
        _log(f"[WARN] issue样本拉取异常 repo={repo}, err={e}")
        return samples

    for item in data:
        # GitHub issues API 会混入 PR，过滤掉
        if item.get("pull_request"):
            continue
        title = (item.get("title") or "").strip()
        if not title:
            continue
        samples.append(
            EvalSample(
                sample_type="issue",
                repo=repo,
                query=build_query(title),
                target_title=title,
                meta={"issue_number": item.get("number")},
            )
        )
        if len(samples) >= per_repo:
            break
    return samples


async def fetch_recent_commits(
    session: aiohttp.ClientSession,
    headers: Dict[str, str],
    repo: str,
    per_repo: int,
) -> List[EvalSample]:
    url = f"https://api.github.com/repos/{repo}/commits"
    params = {"per_page": 100}
    samples: List[EvalSample] = []
    try:
        async with session.get(url, headers=headers, params=params) as res:
            if res.status != 200:
                _log(f"[WARN] commit样本拉取失败 repo={repo}, status={res.status}")
                return samples
            data = await res.json()
    except Exception as e:
        _log(f"[WARN] commit样本拉取异常 repo={repo}, err={e}")
        return samples

    generic_prefixes = (
        "merge pull request",
        "merge tag",
        "merge branch",
        "merge remote-tracking",
    )
    for item in data:
        commit = item.get("commit") or {}
        message = (commit.get("message") or "").strip()
        if not message:
            continue
        first_line = message.splitlines()[0].strip().lower()
        # 过滤语义弱的泛化 merge 提交，避免评测失真
        if first_line.startswith(generic_prefixes):
            continue
        samples.append(
            EvalSample(
                sample_type="commit",
                repo=repo,
                query=build_query(message),
                target_message=message,
                meta={"sha": item.get("sha")},
            )
        )
        if len(samples) >= per_repo:
            break
    return samples


async def fetch_commits_for_vector_db(
    session: aiohttp.ClientSession,
    headers: Dict[str, str],
    repo: str,
    per_repo: int,
) -> List[Dict[str, Any]]:
    """为向量库构建抓取 commit 原始记录。"""
    url = f"https://api.github.com/repos/{repo}/commits"
    params = {"per_page": min(max(per_repo, 1), 100)}
    try:
        async with session.get(url, headers=headers, params=params) as res:
            if res.status != 200:
                _log(f"[WARN] 向量库commit拉取失败 repo={repo}, status={res.status}")
                return []
            data = await res.json()
    except Exception as e:
        _log(f"[WARN] 向量库commit拉取异常 repo={repo}, err={e}")
        return []

    records: List[Dict[str, Any]] = []
    for item in data:
        commit = item.get("commit") or {}
        message = (commit.get("message") or "").strip()
        if not message:
            continue
        records.append(
            {
                "repo": repo,
                "sha": item.get("sha"),
                "summary": message.splitlines()[0][:120],
                "content": message,
                "author_date": (commit.get("author") or {}).get("date"),
                "api_url": item.get("url"),
            }
        )
        if len(records) >= per_repo:
            break
    return records


async def build_commit_vector_db(
    commit_repos: List[str],
    commit_build_per_repo: int,
) -> Dict[str, Any]:
    """自动构建（或增量填充）commit向量库，供 online-search 本地优先检索。"""
    token = get_github_token()
    if not token:
        raise RuntimeError("GitHub token 未配置，无法自动构建 commit 向量库")
    if not Embedding.is_configured():
        raise RuntimeError("Embedding 未配置，无法自动构建 commit 向量库")

    db_path = get_commit_vector_db_path()
    init_commit_vector_db(db_path)
    _log(f"自动构建commit向量库: {db_path}")

    timeout = aiohttp.ClientTimeout(total=max(20, get_github_request_timeout()))
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "RAG-Online-Recall-Eval/1.0",
        "Authorization": f"token {token}",
    }

    total_raw = 0
    total_upsert = 0
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for repo in commit_repos:
            _log(f"构建向量库 - 拉取 commit: {repo}")
            records = await fetch_commits_for_vector_db(session, headers, repo, commit_build_per_repo)
            total_raw += len(records)
            if not records:
                _log(f"  -> 无可用commit")
                continue
            texts = [f"{r['repo']} {r['summary']} {r['content']}" for r in records]
            vectors = await Embedding.vectorize_embeddings_batch(texts)
            ready_records = []
            for rec, vec in zip(records, vectors):
                if not vec:
                    continue
                r = rec.copy()
                r["embedding"] = vec
                ready_records.append(r)
            inserted = upsert_commit_records(db_path, ready_records)
            total_upsert += inserted
            _log(f"  -> raw={len(records)}, embedded={len(ready_records)}, upsert={inserted}")

    return {"db_path": db_path, "raw": total_raw, "upsert": total_upsert}


async def build_eval_samples(
    issue_per_repo: int,
    commit_per_repo: int,
) -> List[EvalSample]:
    token = get_github_token()
    if not token:
        raise RuntimeError("GitHub token 未配置，无法构建评测样本")

    issue_repos = get_github_issue_repos()
    commit_repos = get_github_commit_repos()
    _log(f"准备拉取样本：issue repos={len(issue_repos)}, commit repos={len(commit_repos)}")

    timeout = aiohttp.ClientTimeout(total=max(20, get_github_request_timeout()))
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "RAG-Online-Recall-Eval/1.0",
        "Authorization": f"token {token}",
    }

    samples: List[EvalSample] = []
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for repo in issue_repos:
            _log(f"拉取 issue 样本: {repo}")
            repo_samples = await fetch_recent_issues(session, headers, repo, issue_per_repo)
            _log(f"  -> issue 样本 {len(repo_samples)} 条")
            samples.extend(repo_samples)

        for repo in commit_repos:
            _log(f"拉取 commit 样本: {repo}")
            repo_samples = await fetch_recent_commits(session, headers, repo, commit_per_repo)
            _log(f"  -> commit 样本 {len(repo_samples)} 条")
            samples.extend(repo_samples)

    return samples


def _hit_index_issue(target_title: str, issues: List[Dict[str, Any]]) -> Optional[int]:
    for idx, item in enumerate(issues):
        if is_issue_hit(target_title, item.get("title", "")):
            return idx
    return None


def _hit_index_commit(target_message: str, commits: List[Dict[str, Any]]) -> Optional[int]:
    for idx, item in enumerate(commits):
        if is_commit_hit(target_message, item.get("summary", "")):
            return idx
    return None


async def evaluate_recall(samples: List[EvalSample], max_k: int) -> Dict[str, Any]:
    ks = [1, 3, 5]
    ks = [k for k in ks if k <= max_k]
    if max_k not in ks:
        ks.append(max_k)
    ks = sorted(set(ks))

    results_by_type = {
        "issue": {"total": 0, "hits": {k: 0 for k in ks}},
        "commit": {"total": 0, "hits": {k: 0 for k in ks}},
    }
    latencies_ms: List[float] = []
    miss_cases: List[Dict[str, Any]] = []

    for idx, sample in enumerate(samples, start=1):
        _log(f"评测进度 {idx}/{len(samples)}: [{sample.sample_type}] {sample.query}")
        start = time.perf_counter()
        result = await search_github_online(sample.query, top_k=max_k)
        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies_ms.append(elapsed_ms)

        issues = result.get("issues", []) or []
        commits = result.get("commits", []) or []
        results_by_type[sample.sample_type]["total"] += 1

        if sample.sample_type == "issue":
            hit_idx = _hit_index_issue(sample.target_title or "", issues)
            returned_titles = [i.get("title", "") for i in issues[:max_k]]
            target_value = sample.target_title
        else:
            hit_idx = _hit_index_commit(sample.target_message or "", commits)
            returned_titles = [c.get("summary", "") for c in commits[:max_k]]
            target_value = sample.target_message

        for k in ks:
            if hit_idx is not None and hit_idx < k:
                results_by_type[sample.sample_type]["hits"][k] += 1

        if hit_idx is None:
            miss_cases.append(
                {
                    "type": sample.sample_type,
                    "repo": sample.repo,
                    "query": sample.query,
                    "target": target_value,
                    "top_returned": returned_titles,
                    "latency_ms": round(elapsed_ms, 2),
                }
            )

    # 汇总
    summary = {"ks": ks, "types": {}, "overall": {}, "avg_latency_ms": 0.0, "miss_cases": miss_cases}
    summary["avg_latency_ms"] = round(sum(latencies_ms) / max(1, len(latencies_ms)), 2)

    overall_total = 0
    overall_hits = {k: 0 for k in ks}
    for t in ["issue", "commit"]:
        t_total = results_by_type[t]["total"]
        overall_total += t_total
        t_metrics = {"total": t_total, "recall": {}}
        for k in ks:
            hits = results_by_type[t]["hits"][k]
            overall_hits[k] += hits
            t_metrics["recall"][k] = round(hits / t_total, 4) if t_total else 0.0
        summary["types"][t] = t_metrics

    summary["overall"]["total"] = overall_total
    summary["overall"]["recall"] = {
        k: (round(overall_hits[k] / overall_total, 4) if overall_total else 0.0) for k in ks
    }
    return summary


def save_samples(samples: List[EvalSample], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(
                json.dumps(
                    {
                        "type": s.sample_type,
                        "repo": s.repo,
                        "query": s.query,
                        "target_title": s.target_title,
                        "target_message": s.target_message,
                        "meta": s.meta or {},
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


def save_report(report: Dict[str, Any], path: str) -> None:
    ks = report["ks"]
    lines = [
        "# online-search 召回率评测报告",
        "",
        f"- 评测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 总样本数: {report['overall']['total']}",
        f"- 平均延迟: {report['avg_latency_ms']} ms",
        "",
        "## Recall",
        "",
        "| 类型 | " + " | ".join([f"Recall@{k}" for k in ks]) + " |",
        "| --- | " + " | ".join(["---"] * len(ks)) + " |",
    ]

    for t in ["issue", "commit"]:
        row = [f"{report['types'][t]['recall'][k]:.4f}" for k in ks]
        lines.append(f"| {t} | " + " | ".join(row) + " |")

    row = [f"{report['overall']['recall'][k]:.4f}" for k in ks]
    lines.append(f"| overall | " + " | ".join(row) + " |")

    lines.extend(["", "## 未命中样本（最多展示20条）", ""])
    miss_cases = report.get("miss_cases", [])[:20]
    if not miss_cases:
        lines.append("- 无")
    else:
        for i, c in enumerate(miss_cases, start=1):
            lines.append(f"- {i}. [{c['type']}] `{c['query']}`")
            lines.append(f"  - repo: `{c['repo']}`")
            lines.append(f"  - latency_ms: `{c['latency_ms']}`")
            lines.append(f"  - top_returned: {json.dumps(c['top_returned'], ensure_ascii=False)}")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


async def main_async(args: argparse.Namespace) -> None:
    _log(f"online-search 实际调用入口: {search_github_online.__module__}")
    _log(f"online-search 实际代码文件: {search_github_online.__code__.co_filename}")
    if args.auto_build_commit_db:
        _log("开始自动构建 commit 向量库...")
        commit_repos = get_github_commit_repos()
        build_stats = await build_commit_vector_db(commit_repos, args.commit_build_per_repo)
        _log(
            "commit 向量库构建完成: "
            f"path={build_stats['db_path']}, raw={build_stats['raw']}, upsert={build_stats['upsert']}"
        )

    _log("开始构建评测样本...")
    samples = await build_eval_samples(args.issue_per_repo, args.commit_per_repo)
    if not samples:
        raise RuntimeError("未获取到任何样本，请检查 token、网络或仓库配置")

    _log(f"样本准备完成，共 {len(samples)} 条（issue+commit）")
    os.makedirs(args.output_dir, exist_ok=True)
    samples_path = os.path.join(args.output_dir, "online_search_eval_samples.jsonl")
    save_samples(samples, samples_path)
    _log(f"样本已保存: {samples_path}")

    _log("开始执行召回率评测...")
    report = await evaluate_recall(samples, args.max_k)
    report_path = os.path.join(args.output_dir, "report-online-search-recall.md")
    save_report(report, report_path)

    _log("评测完成")
    _log(f"报告路径: {report_path}")
    _log(f"Overall Recall: {report['overall']['recall']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="online-search 召回率评测")
    parser.add_argument("--issue-per-repo", type=int, default=2, help="每个 issue 仓库采样数量")
    parser.add_argument("--commit-per-repo", type=int, default=2, help="每个 commit 仓库采样数量")
    parser.add_argument("--max-k", type=int, default=5, help="评测最大 top_k")
    parser.add_argument(
        "--no-auto-build-commit-db",
        action="store_true",
        help="关闭评测前自动构建commit向量库（默认开启自动构建）",
    )
    parser.add_argument(
        "--commit-build-per-repo",
        type=int,
        default=50,
        help="自动构建commit向量库时，每仓库拉取commit条数",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=os.path.join(CURRENT_DIR),
        help="输出目录（样本与报告）",
    )
    args = parser.parse_args()
    args.auto_build_commit_db = not args.no_auto_build_commit_db
    return args


if __name__ == "__main__":
    try:
        asyncio.run(main_async(parse_args()))
    except KeyboardInterrupt:
        _log("用户中断评测")
    except Exception as e:
        _log(f"[ERROR] 评测失败: {e}")
        raise
