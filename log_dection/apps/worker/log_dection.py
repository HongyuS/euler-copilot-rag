from apps.enum.task import TaskTypeEnum
from apps.schemas.log import LogModel, LogTemplateModel


class LogDectionService:
    name = TaskTypeEnum.LOG_DETECTION.value

    @staticmethod
    async def load_and_split_logs(log_file_path: str) -> list[LogModel]:
        """加载并拆分日志文件"""
        # 这里实现加载和拆分日志文件的具体逻辑
        pass

    @staticmethod
    async def log_to_log_template(logs: list[LogModel]) -> list[LogTemplateModel]:
        """将日志转换为日志模板"""
        # 这里实现日志转换为日志模板的具体逻辑
        pass

    @staticmethod
    async def get_embeddings(log: list[LogModel] | list[LogTemplateModel]) -> None:
        """获取日志或日志模板的嵌入向量表示"""
        # 这里实现获取嵌入向量表示的具体逻辑
        pass

    @staticmethod
    async def DBSCAN_clustering(log_templates: list[LogTemplateModel]) -> tuple[list[LogTemplateModel], list[LogTemplateModel]]:
        """使用DBSCAN算法进行聚类"""
        # 这里调用ClusterService的DBSCAN方法
        pass

    @staticmethod
    async def KMeans_clustering(normal_log_templates: list[LogTemplateModel], unnormal_log_templates: list[LogTemplateModel]) -> list[LogTemplateModel]:
        """使用KMeans算法进行聚类"""
        # 这里调用ClusterService的KMeans方法
        pass

    @staticmethod
    async def pending_unnormal_log_templates(
        normal_log_templates: list[LogTemplateModel],
        unnormal_log_templates: list[LogTemplateModel]
    ) -> list[LogTemplateModel]:
        """增加异常日志模板的候选"""
        # 这里实现增加异常日志模板候选的具体逻辑
        pass

    @staticmethod
    async def rerank_unnormal_log_templates(
        unnormal_log_templates: list[LogTemplateModel]
    ) -> list[LogTemplateModel]:
        """重新排序异常日志模板"""
        # 这里实现重新排序异常日志模板的具体逻辑
        pass

    @staticmethod
    async def dect_unnormal_log_templates(
        unnormal_log_templates: list[LogTemplateModel]
    ) -> list[LogTemplateModel]:
        """检测异常日志模板"""
        # 这里实现检测异常日志模板的具体逻辑
        pass

    @staticmethod
    async def filter_unnormal_log_templates(
        unnormal_log_templates: list[LogTemplateModel],
        threshold: float = 0.8
    ) -> list[LogTemplateModel]:
        """过滤异常日志模板"""
        # 这里实现过滤异常日志模板的具体逻辑
        pass

    @staticmethod
    async def save_unnormal_logs_and_surroundings(
        logs: list[LogModel],
        unnormal_logs: list[LogModel],
        context_window: int = 5
    ) -> None:
        """保存异常日志及其上下文日志"""
        # 这里实现保存异常日志及其上下文日志的具体逻辑
        pass

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
