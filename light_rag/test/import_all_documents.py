"""
一键批量导入文档脚本。

用法示例：
python import_all_documents.py --kb-name my_kb --docs-dir D:\\docs --recursive --ext .md,.txt,.pdf --create-kb
"""
import argparse
import asyncio
import os
import sys
import time
from pathlib import Path
from typing import List, Set

test_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(test_dir, "..", "src"))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from common.config import get_default_chunk_size, get_task_db_path
from common.task import run_task_listener_in_process
from enums.task import TaskStatusEnum
from sqlite.task_sqlite import init_task_db
from tool import document_manager, knowledge_base_manager


TERMINAL_STATUSES: Set[str] = {
    TaskStatusEnum.SUCCESSFUL.value,
    TaskStatusEnum.FAILED.value,
    TaskStatusEnum.CANCELED.value,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量导入目录下全部文档到知识库")
    parser.add_argument("--kb-name", required=True, help="目标知识库名称（必填）")
    parser.add_argument("--docs-dir", required=True, help="待导入文档目录（必填）")
    parser.add_argument("--recursive", action="store_true", help="是否递归扫描子目录（默认不递归）")
    parser.add_argument(
        "--ext",
        default=".md,.txt,.pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.csv,.html,.htm,.json,.yaml,.yml,.xml",
        help="允许的扩展名列表，逗号分隔，如 .md,.txt,.pdf",
    )
    parser.add_argument("--chunk-size", type=int, default=None, help="导入 chunk 大小（可选，默认使用知识库配置）")
    parser.add_argument("--create-kb", action="store_true", help="若知识库不存在则自动创建")
    parser.add_argument(
        "--create-kb-chunk-size",
        type=int,
        default=None,
        help="创建知识库时使用的 chunk_size（未提供则走默认配置）",
    )
    parser.add_argument("--poll-interval", type=float, default=2.0, help="轮询任务状态间隔秒数（默认 2）")
    return parser.parse_args()


def normalize_extensions(raw_ext: str) -> Set[str]:
    exts: Set[str] = set()
    for ext in (raw_ext or "").split(","):
        ext = ext.strip().lower()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = f".{ext}"
        exts.add(ext)
    return exts


def collect_files(docs_dir: Path, recursive: bool, extensions: Set[str]) -> List[str]:
    candidates = docs_dir.rglob("*") if recursive else docs_dir.glob("*")
    files: List[str] = []
    for p in candidates:
        if not p.is_file():
            continue
        if extensions and p.suffix.lower() not in extensions:
            continue
        files.append(str(p.resolve()))
    files.sort()
    return files


def ensure_kb_exists_or_create(kb_name: str, create_kb: bool, create_kb_chunk_size: int | None) -> None:
    list_resp = knowledge_base_manager(action="list", keyword=kb_name)
    data = list_resp.get("data") or {}
    kbs = data.get("knowledge_bases") or []
    if any(kb.get("name") == kb_name for kb in kbs):
        print(f"[INFO] 知识库已存在: {kb_name}")
        return

    if not create_kb:
        raise RuntimeError(f"知识库 '{kb_name}' 不存在。可加 --create-kb 自动创建。")

    chunk_size = create_kb_chunk_size or get_default_chunk_size()
    create_resp = knowledge_base_manager(action="add", kb_name=kb_name, chunk_size=chunk_size)
    if not create_resp.get("success"):
        raise RuntimeError(f"创建知识库失败: {create_resp.get('message')}")
    print(f"[INFO] 已创建知识库: {kb_name} (chunk_size={chunk_size})")


async def create_import_and_wait(
    kb_name: str,
    file_paths: List[str],
    chunk_size: int | None,
    poll_interval: float,
) -> dict:
    add_resp = await document_manager(
        action="add",
        file_paths=file_paths,
        kb_name=kb_name,
        chunk_size=chunk_size,
    )
    if not add_resp.get("success"):
        raise RuntimeError(f"创建导入任务失败: {add_resp.get('message')}")

    task_data = add_resp.get("data") or {}
    task_id = task_data.get("task_id")
    if not task_id:
        raise RuntimeError("导入任务缺少 task_id")

    print(f"[INFO] 导入任务已创建，task_id={task_id}")
    print("[INFO] 开始轮询任务状态...")

    started = time.time()
    while True:
        status_resp = await document_manager(action="getstatus", task_id=task_id)
        if not status_resp.get("success"):
            raise RuntimeError(f"查询任务状态失败: {status_resp.get('message')}")

        data = status_resp.get("data") or {}
        status = data.get("status", "unknown")
        progress = float(data.get("completion_precent") or 0.0)
        success_count = int(data.get("success_count") or 0)
        failed_count = int(data.get("failed_count") or 0)
        elapsed = int(time.time() - started)

        print(
            f"[PROGRESS] status={status} progress={progress:.1f}% "
            f"success={success_count} failed={failed_count} elapsed={elapsed}s"
        )

        if status in TERMINAL_STATUSES:
            return status_resp
        await asyncio.sleep(poll_interval)


def print_final_summary(result: dict) -> None:
    data = (result.get("data") or {})
    status = data.get("status")
    success_files = data.get("success_files") or []
    failed_files = data.get("failed_files") or []

    print("\n================ 导入结果 ================")
    print(f"任务状态: {status}")
    print(f"成功文件数: {len(success_files)}")
    print(f"失败文件数: {len(failed_files)}")

    if success_files:
        print("\n[成功文件]")
        for item in success_files:
            fp = item.get("file_path", "")
            chunk_count = item.get("chunk_count", 0)
            print(f"- {fp} (chunks={chunk_count})")

    if failed_files:
        print("\n[失败文件]")
        for item in failed_files:
            fp = item.get("file_path", "")
            err = item.get("error", "")
            print(f"- {fp} | error={err}")

    print("==========================================")


async def main_async() -> int:
    args = parse_args()

    docs_dir = Path(args.docs_dir).resolve()
    if not docs_dir.exists() or not docs_dir.is_dir():
        print(f"[ERROR] 文档目录不存在或不是目录: {docs_dir}")
        return 1

    extensions = normalize_extensions(args.ext)
    files = collect_files(docs_dir, args.recursive, extensions)
    if not files:
        print("[ERROR] 未找到可导入文件，请检查目录/扩展名参数。")
        return 1

    print(f"[INFO] 目标知识库: {args.kb_name}")
    print(f"[INFO] 文档目录: {docs_dir}")
    print(f"[INFO] 扫描模式: {'递归' if args.recursive else '非递归'}")
    print(f"[INFO] 扩展名过滤: {', '.join(sorted(extensions))}")
    print(f"[INFO] 待导入文件数: {len(files)}")

    ensure_kb_exists_or_create(
        kb_name=args.kb_name,
        create_kb=args.create_kb,
        create_kb_chunk_size=args.create_kb_chunk_size,
    )

    init_task_db(get_task_db_path())
    listener_proc = run_task_listener_in_process()
    try:
        result = await create_import_and_wait(
            kb_name=args.kb_name,
            file_paths=files,
            chunk_size=args.chunk_size,
            poll_interval=args.poll_interval,
        )
        print_final_summary(result)
        data = result.get("data") or {}
        status = data.get("status")
        return 0 if status == TaskStatusEnum.SUCCESSFUL.value else 2
    finally:
        if listener_proc and listener_proc.is_alive():
            listener_proc.terminate()
            listener_proc.join(timeout=3)


if __name__ == "__main__":
    try:
        rc = asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n[INFO] 用户中断，脚本退出。")
        rc = 130
    except Exception as exc:
        print(f"[ERROR] 脚本执行失败: {exc}")
        rc = 1
    sys.exit(rc)
