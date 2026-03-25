"""任务管理器 - 操作 task.db"""
from datetime import datetime
from typing import Optional

from enums.task import TaskStatusEnum, TaskTypeEnum
from sqlite.task_sqlite import execute_modify, execute_query


class TaskManager:
    """任务管理静态类"""

    @staticmethod
    async def get_task_by_id(task_id: str) -> Optional[dict]:
        """根据任务ID获取任务"""
        sql = """
            SELECT task_id, pid, task_name, task_type, completion_precent, status,
                   task_related_params, result_summary, created_at
            FROM task_table WHERE task_id = :task_id
        """
        rows = await execute_query(sql, {"task_id": task_id})
        return rows[0] if rows else None

    @staticmethod
    async def get_tasks_by_status(status_list: list[TaskStatusEnum]) -> list[dict]:
        """根据状态获取任务列表"""
        if not status_list:
            return []
        placeholders = ", ".join("?" * len(status_list))
        sql = f"""
            SELECT task_id, pid, task_name, task_type, completion_precent, status,
                   task_related_params, result_summary, created_at
            FROM task_table WHERE status IN ({placeholders})
        """
        params = tuple(s.value for s in status_list)
        return await execute_query(sql, params)

    @staticmethod
    async def update_task_by_id(task_id: str, update_data: dict) -> bool:
        """更新任务"""
        if not update_data:
            return True
        set_parts = [f"{k} = :{k}" for k in update_data.keys()]
        sql = f"UPDATE task_table SET {', '.join(set_parts)} WHERE task_id = :task_id"
        params = dict(update_data, task_id=task_id)
        return await execute_modify(sql, params)

    @staticmethod
    async def update_running_tasks_to_pending_tasks() -> bool:
        """将 RUNNING 任务改为 PENDING（服务重启恢复）"""
        sql = """
            UPDATE task_table SET status = :pending WHERE status = :running
        """
        params = {"pending": TaskStatusEnum.PENDING.value, "running": TaskStatusEnum.RUNNING.value}
        return await execute_modify(sql, params)

    @staticmethod
    async def create_task(task_id: str, task_name: str, task_related_params: str) -> bool:
        """创建任务"""
        sql = """
            INSERT INTO task_table (task_id, pid, task_name, task_type, completion_precent, status, task_related_params, result_summary, created_at)
            VALUES (:task_id, NULL, :task_name, :task_type, 0.0, :status, :task_related_params, NULL, :created_at)
        """
        params = {
            "task_id": task_id,
            "task_name": task_name,
            "task_type": TaskTypeEnum.DOCUMENT_IMPORT.value,
            "status": TaskStatusEnum.PENDING.value,
            "task_related_params": task_related_params,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        return await execute_modify(sql, params)
