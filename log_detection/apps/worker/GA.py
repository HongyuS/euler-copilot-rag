from apps.enum.task import TaskTypeEnum


class GA:
    name = TaskTypeEnum.GA.value

    @staticmethod
    async def stop(task_id: str) -> None:
        """停止GA服务"""
        # 这里实现停止GA的具体逻辑
        pass

    @staticmethod
    async def run(task_id: str) -> None:
        """GA服务"""
        # 这里实现GA的具体逻辑
        pass
