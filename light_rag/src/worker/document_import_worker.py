"""文档导入任务（子进程执行）"""
import json
import logging
import os
import sys

logger = logging.getLogger(__name__)
_src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _src not in sys.path:
    sys.path.insert(0, _src)


async def run(task_id: str) -> None:
    from common.config import get_task_db_path
    from sqlite.task_sqlite import init_task_db
    from sqlite.kb_sqlite import KnowledgeBase
    from manager.task_manager import TaskManager
    from manager.database_manager import Database, get_kb_id_by_name
    from manager.document_manager import import_document
    from enums.task import TaskStatusEnum

    init_task_db(get_task_db_path())
    db = Database(os.path.join(_src, "database", "kb.db"))

    task = await TaskManager.get_task_by_id(task_id)
    if not task:
        logger.error("任务不存在: %s", task_id)
        return
    if task.get("status") == TaskStatusEnum.CANCELED.value:
        return

    params = json.loads(task["task_related_params"] or "{}")
    file_paths = params.get("file_paths", [])
    kb_name = params.get("kb_name", "")
    chunk_size = params.get("chunk_size")

    if not file_paths or not kb_name:
        await TaskManager.update_task_by_id(task_id, {
            "status": TaskStatusEnum.FAILED_PENDING_REMOVE.value,
            "result_summary": json.dumps({"error": "缺少 file_paths 或 kb_name"}),
        })
        return

    temp = {"success": False, "message": ""}
    kb_id = get_kb_id_by_name(db, kb_name, temp)
    if not kb_id:
        await TaskManager.update_task_by_id(task_id, {
            "status": TaskStatusEnum.FAILED_PENDING_REMOVE.value,
            "result_summary": json.dumps({"error": temp.get("message", "知识库不存在")}),
        })
        return

    session = db.get_session()
    try:
        kb = session.query(KnowledgeBase).filter_by(id=kb_id).first()
        if not kb:
            await TaskManager.update_task_by_id(task_id, {
                "status": TaskStatusEnum.FAILED_PENDING_REMOVE.value,
                "result_summary": json.dumps({"error": "知识库不存在"}),
            })
            return
        if chunk_size is None:
            chunk_size = kb.chunk_size
    finally:
        session.close()

    success_files, failed_files = [], []
    for i, fp in enumerate(file_paths):
        if not os.path.exists(fp):
            failed_files.append({"file_path": fp, "error": "文件不存在"})
            continue
        fs = db.get_session()
        try:
            ok, msg, data = await import_document(fs, kb_id, fp, chunk_size)
            if ok:
                success_files.append({
                    "file_path": fp,
                    "doc_name": (data or {}).get("doc_name", os.path.basename(fp)),
                    "chunk_count": (data or {}).get("chunk_count", 0),
                })
            else:
                failed_files.append({"file_path": fp, "error": msg})
        except Exception as e:
            failed_files.append({"file_path": fp, "error": str(e)})
        finally:
            fs.close()
        await TaskManager.update_task_by_id(task_id, {"completion_precent": 100.0 * (i + 1) / len(file_paths)})

    summary = json.dumps({"success_files": success_files, "failed_files": failed_files})
    st = TaskStatusEnum.SUCCESSFUL_PENDING_REMOVE.value if success_files else TaskStatusEnum.FAILED_PENDING_REMOVE.value
    await TaskManager.update_task_by_id(task_id, {"status": st, "result_summary": summary})
