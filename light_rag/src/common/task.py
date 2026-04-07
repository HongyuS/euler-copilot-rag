"""任务调度与进程管理"""
import asyncio
import logging
import os
import signal

from enums.task import TaskStatusEnum
from manager.task_manager import TaskManager
from worker.document_import_worker import run as run_document_import

logger = logging.getLogger(__name__)
_mp_ctx = __import__("multiprocessing").get_context("spawn")


def _subprocess_target(target, *args, **kwargs):
    """子进程入口：创建新事件循环并运行异步 target"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(target(*args, **kwargs))
    finally:
        loop.close()


def _get_cpu_limit() -> int:
    from common.config import get_task_cpu_limit
    return get_task_cpu_limit()


async def _add_task(task_id: str, target, *args, **kwargs) -> bool:
    """添加任务到进程池"""
    running = await TaskManager.get_tasks_by_status([TaskStatusEnum.RUNNING])
    if len(running) >= _get_cpu_limit():
        logger.warning("当前运行任务数已达限制 %s", _get_cpu_limit())
        return False
    task = await TaskManager.get_task_by_id(task_id)
    if not task or task.get("status") != TaskStatusEnum.RUNNING.value:
        logger.info("任务 %s 状态异常，跳过", task_id)
        return False
    try:
        proc = _mp_ctx.Process(target=_subprocess_target, args=(target,) + args, kwargs=kwargs)
        proc.start()
        await TaskManager.update_task_by_id(task_id, {"pid": proc.pid})
        return True
    except Exception as e:
        logger.error("添加任务 %s 失败: %s", task_id, e)
        return False


async def remove_task(task_id: str) -> None:
    """移除任务进程"""
    task = await TaskManager.get_task_by_id(task_id)
    if not task or not task.get("pid"):
        return
    try:
        sig = getattr(signal, "SIGKILL", signal.SIGTERM)
        os.kill(task["pid"], sig)
        logger.info("进程 %s (%s) 已终止", task_id, task["pid"])
    except Exception as e:
        logger.warning("终止进程 %s 失败: %s", task_id, e)


async def _process_successful_or_failed() -> None:
    """处理 SUCCESSFUL_PENDING_REMOVE / FAILED_PENDING_REMOVE"""
    tasks = await TaskManager.get_tasks_by_status([
        TaskStatusEnum.SUCCESSFUL_PENDING_REMOVE,
        TaskStatusEnum.FAILED_PENDING_REMOVE,
    ])
    for t in tasks:
        await remove_task(t["task_id"])
        if t["status"] == TaskStatusEnum.SUCCESSFUL_PENDING_REMOVE.value:
            await TaskManager.update_task_by_id(t["task_id"], {"status": TaskStatusEnum.SUCCESSFUL.value})
        else:
            await TaskManager.update_task_by_id(t["task_id"], {"status": TaskStatusEnum.FAILED.value})


async def _process_pending_tasks() -> None:
    """处理 PENDING 任务"""
    tasks = await TaskManager.get_tasks_by_status([TaskStatusEnum.PENDING])
    for t in tasks:
        await TaskManager.update_task_by_id(t["task_id"], {"status": TaskStatusEnum.RUNNING.value})
        ok = await _add_task(t["task_id"], run_document_import, t["task_id"])
        if not ok:
            await TaskManager.update_task_by_id(t["task_id"], {"status": TaskStatusEnum.PENDING.value})


async def listen_and_process_tasks() -> None:
    """监听循环"""
    while True:
        try:
            await _process_successful_or_failed()
            await _process_pending_tasks()
        except Exception as e:
            logger.error("任务处理循环异常: %s", e)
        await asyncio.sleep(2)


def _run_async_loop() -> None:
    """子进程内运行异步循环（spawn 子进程需独立初始化 task.db）"""
    from common.config import get_task_db_path
    from sqlite.task_sqlite import init_task_db
    init_task_db(get_task_db_path())
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(listen_and_process_tasks())
    except KeyboardInterrupt:
        logger.info("任务监听进程已停止")
    except Exception as e:
        logger.error("任务监听进程异常: %s", e)


def run_task_listener_in_process():
    """在独立进程中启动任务监听"""
    proc = _mp_ctx.Process(target=_run_async_loop, name="TaskListenerProcess")
    proc.start()
    logger.info("任务监听进程已启动, pid=%s", proc.pid)
    return proc
