from apps.schemas.log import LogParseResultModel
from apps.sqlite.sqlite import AsyncSQLiteSingleton


class LogParseResultManager:
    """日志解析结果管理类"""
    @staticmethod
    async def get_log_parse_results_by_task_id(task_id: str, limit: int | None = None, offset: int | None = None, is_anomalous: bool | None = None) -> tuple[int, list[LogParseResultModel]]:
        """根据任务ID获取日志解析结果列表"""
        # 统计总数
        sql_str = """
            SELECT COUNT(*) as count
            FROM log_parse_result_table
            WHERE task_id = :task_id
        """
        params = {"task_id": task_id}
        if is_anomalous is not None:
            sql_str += " AND is_anomalous = :is_anomalous"
            params["is_anomalous"] = is_anomalous
        count_result = await AsyncSQLiteSingleton().execute_query(sql_str, params)
        total_count = count_result[0]["count"] if count_result else 0
        # 获取分数最高的前limit条日志解析结果
        sql_str = """
            SELECT id, file_path,offset, file_path, is_anomalous, task_id, content, anomaly_reason, anomaly_score
            FROM log_parse_result_table
            WHERE task_id = :task_id
        """
        params = {"task_id": task_id}
        if is_anomalous is not None:
            sql_str += " AND is_anomalous = :is_anomalous"
            params["is_anomalous"] = is_anomalous
        sql_str += " ORDER BY anomaly_score DESC"
        if limit is not None:
            sql_str += " LIMIT :limit"
            params["limit"] = limit
        if offset is not None:
            sql_str += " OFFSET :offset"
            params["offset"] = offset
        results = await AsyncSQLiteSingleton().execute_query(sql_str, params)
        for i in range(len(results)):
            results[i] = LogParseResultModel(**results[i])

        # 根据file_path和offset对结果进行排序，保证日志的原始顺序
        results.sort(key=lambda x: (x.file_path, x.offset))
        return total_count, results

    @staticmethod
    async def add_log_parse_results(log_parse_result_models: list[LogParseResultModel]) -> bool:
        """批量添加日志解析结果"""
        if not log_parse_result_models:
            return False
        # 每次插入 1024 条数据，避免一次性插入过多数据导致性能问题
        batch_size = 1024
        for i in range(0, len(log_parse_result_models), batch_size):
            batch_models = log_parse_result_models[i:i + batch_size]
            sql_str = """
                INSERT INTO log_parse_result_table (id, file_path, offset, is_anomalous, task_id, content, anomaly_reason, anomaly_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params = [(model.id, model.file_path, model.is_anomalous, model.task_id, model.content,
                       model.anomaly_reason, model.anomaly_score) for model in batch_models]
            result = await AsyncSQLiteSingleton().execute_non_query(sql_str, params)
            if not result:
                return False
        return result
