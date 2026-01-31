from apps.enum.task import TaskTypeEnum


class LogDectionService:
    name = TaskTypeEnum.LOG_DETECTION.value

    @staticmethod
    async def stop(task_id: str) -> None:
        """停止日志检测服务"""
        # 这里实现停止日志检测的具体逻辑
        pass

    @staticmethod
    async def run(task_id: str) -> None:
        """日志检测服务"""
        # 这里实现日志检测的具体逻辑
        pass
