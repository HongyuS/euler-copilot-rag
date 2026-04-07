
import json
import logging
import numpy as np
import jieba
import re
import asyncio
from datetime import datetime
from src.worker.base import BaseWorker
from src.parser.parser import LogParser
from src.parser.log_feature_loader import log_feature_class_mapping
from src.sqlite.manager.task import TaskManager
from src.schemas.task import TaskRelatedParamsModel
from src.enum.log import LogTypeEnum
from src.enum.task import TaskTypeEnum, TaskStatusEnum
from src.schemas.log import LogModel
from src.service.embedding import Embedding

logger = logging.getLogger(__name__)


class LogDetectionBasedOnEmbeddingWorker(BaseWorker):
    """
    基于 Embedding 聚类和关键字匹配的日志检测 Worker
    """
    name = TaskTypeEnum.LOG_DETECTION_BASE_ON_EMBEDDING.value

    @staticmethod
    async def cal_keyword_similarity(str1: str, keywords: list[str]) -> float:
        """计算jaccard相似度"""
        words = list(jieba.cut(str1))
        new_keywords = []
        for keyword in keywords:
            new_keywords.extend(jieba.cut(keyword)) 
        keywords = set(new_keywords)
        words_set = set(words)
        intersection = words_set & keywords
        return (len(intersection) / len(keywords) if len(keywords) > 0 else 0.0)*100

    @staticmethod
    async def cal_sentiment_score(log_type: LogTypeEnum, log_content: str) -> float:
        """计算日志的情感分数"""
        log_class = log_feature_class_mapping.get(log_type, None)
        if log_class is None:
            return 0.0
        sum = 0.0
        score = 0.0
        for anomalous_keywords, _ in log_class.keywords_regex_and_scores["anomalous"].items():
            sum += _
            if re.search(anomalous_keywords, log_content):
                score += _
        return score/sum * 100 if sum > 0 else 0.0
    
    @staticmethod
    def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """计算两个向量的余弦相似度"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        similarity = np.dot(vec1_np, vec2_np) / (norm1 * norm2)
        return max(0.0, similarity) * 100  # 归一化到0-100分
    
    @staticmethod
    def classify_query_intent(query: str) -> str:
        """识别query意图类型"""
        query_lower = query.lower()
        
        # 特定类型问题关键词
        specific_type_keywords = {
            "oom": ["内存溢出", "oom", "out of memory", "内存不足"],
            "timeout": ["超时", "timeout", "time out", "连接超时", "请求超时"],
            "crash": ["崩溃", "crash", "宕机", "挂了", "退出", "重启"],
            "network": ["网络", "连接失败", "断开", "丢包", "延迟高"],
            "error": ["错误", "error", "exception", "fail", "failed"]
        }
        
        # 异常排查类关键词
        anomaly_keywords = [
            "分析", "排查", "看看", "检查", "有没有问题", "是否正常",
            "异常", "错误", "故障", "问题", "帮忙看", "帮我看看"
        ]
        
        # 先判断是否是特定类型查询
        for type_, keywords in specific_type_keywords.items():
            for kw in keywords:
                if kw in query_lower:
                    return "specific_type"
        
        # 再判断是否是异常排查类
        for kw in anomaly_keywords:
            if kw in query_lower:
                return "anomaly_detection"
        
        # 其他情况属于精确检索
        return "precise_search"
    
    @staticmethod
    def smart_decide_template_usage(query: str) -> bool:
        """根据query内容智能判断是否需要开启模板生成"""
        # 包含具体特征关键词，说明要搜索具体内容，关闭模板
        concrete_patterns = [
            r'\d+\.\d+\.\d+\.\d+',  # IP地址
            r'0x[0-9a-fA-F]+',      # 十六进制错误码
            r'[A-Z]+-\d+',          # 错误码格式如ERR-123
            r'\d{4,}',              # 4位以上数字（端口号、错误码等）
            r'([a-zA-Z0-9_-]+)\.[a-zA-Z]{2,}',  # 域名
        ]
        
        for pattern in concrete_patterns:
            if re.search(pattern, query):
                return False
        
        # 其他情况默认开启模板，匹配语义模式
        return True

    @staticmethod
    async def handle_single_log_file(
        file_path: str, 
        max_anomaly_log_count: int, 
        anomaly_keywords: list[str], 
        time_start: str, 
        time_end: str,
        query_vector: list[float],
        intent: str,
        enable_template: bool
    ) -> tuple[list[LogModel], list[LogModel]]:
        """处理单个日志文件的逻辑：直接计算embedding相似度和关键字匹配"""
        # 解析日志文件
        log_models: list[LogModel] = await LogParser.parse_log_file(file_path=file_path, need_split_by_regex=True, time_start=time_start, time_end=time_end)
        
        if len(log_models) == 0:
            return log_models, []
        
        # 获取日志模板和 embedding
        await LogParser.get_log_templates(log_models=log_models, need_embedding=True)
        
        # 多维度评分
        candidate_unnormal_log_models: list[LogModel] = []
        for log_model in log_models:
            # 1. 计算语义相似度
            semantic_similarity = 0.0
            if log_model.template_vector:
                semantic_similarity = LogDetectionBasedOnEmbeddingWorker.cosine_similarity(
                    log_model.template_vector, query_vector
                )
            
            # 2. 计算关键字相似度
            keyword_similarity = await LogDetectionBasedOnEmbeddingWorker.cal_keyword_similarity(
                log_model.content, anomaly_keywords
            )
            
            # 3. 计算情感分数
            sentiment_score = await LogDetectionBasedOnEmbeddingWorker.cal_sentiment_score(
                log_model.log_type, log_model.content
            )
            
            # 动态权重调整
            if intent == "precise_search":
                # 精确检索：语义相似度权重最高
                final_score = semantic_similarity * 0.6 + keyword_similarity * 0.3 + sentiment_score * 0.1
            elif intent == "anomaly_detection":
                # 异常排查：异常分数权重最高
                final_score = sentiment_score * 0.5 + keyword_similarity * 0.3 + semantic_similarity * 0.2
            else:  # specific_type
                # 特定类型：语义相似度和异常分数权重相当
                final_score = semantic_similarity * 0.5 + sentiment_score * 0.35 + keyword_similarity * 0.15
            
            # 过滤低分日志
            if final_score >= 20:  # 最低阈值20分
                log_model.anomaly_score = final_score
                candidate_unnormal_log_models.append(log_model)
        
        # 排序并返回Top N
        candidate_unnormal_log_models = sorted(
            candidate_unnormal_log_models, key=lambda x: x.anomaly_score, reverse=True)[:max_anomaly_log_count]
        
        return log_models, candidate_unnormal_log_models
    
    @staticmethod
    async def run(task_id: str) -> None:
        """日志检测服务"""
        try:
            task_entity = await TaskManager.get_task_by_id(task_id)
            if task_entity is None:
                await TaskManager.update_task_by_id(task_id, {"status": TaskStatusEnum.FAILED.value})
                raise ValueError(f"任务 {task_id} 不存在")
            
            # 解析任务参数
            task_related_params_js = json.loads(
                task_entity.task_related_params)
            if "time_start" in task_related_params_js and task_related_params_js["time_start"]:
                task_related_params_js["time_start"] = datetime.strptime(task_related_params_js["time_start"],
                                                                         '%Y-%m-%d %H:%M')
            else:
                task_related_params_js["time_start"] = None
            if "time_end" in task_related_params_js and task_related_params_js["time_end"]:
                task_related_params_js["time_end"] = datetime.strptime(task_related_params_js["time_end"],
                                                                       '%Y-%m-%d %H:%M')
            else:
                task_related_params_js["time_end"] = None
            
            task_related_params_model = TaskRelatedParamsModel(
                **task_related_params_js)
            
            # 获取任务参数
            query = task_related_params_model.query
            file_path_list = task_related_params_model.file_path_list
            max_anomaly_log_count = task_related_params_model.max_anomaly_log_count
            anomaly_keywords: list[str] = task_related_params_model.anomaly_keywords
            time_start = task_related_params_model.time_start
            time_end = task_related_params_model.time_end
            
            # 前置处理：query向量化和意图识别（只执行一次）
            logger.info(f"[任务准备] 开始处理query: {query}")
            query_vectors = await Embedding.vectorize_embedding([query])
            query_vector = query_vectors[0]
            intent = LogDetectionBasedOnEmbeddingWorker.classify_query_intent(query)
            enable_template = LogDetectionBasedOnEmbeddingWorker.smart_decide_template_usage(query)
            logger.info(f"[任务准备] query意图识别结果: {intent}, 是否启用模板: {enable_template}")
            
            # 准备工作
            log_models = []
            candidate_unnormal_log_models: list[LogModel] = []
            file_path_list = await BaseWorker.get_files_from_file_path_list(file_path_list)
            total_files = len(file_path_list)
            processed_files = 0
            
            # 更新任务进度为5%
            progress = 5.0
            logger.info(f"[进度更新] task_id={task_id}, total={progress:.1f}%")
            await TaskManager.update_task_by_id(task_id, {"completion_precent": progress})
            
            # 批量处理文件
            batch_size = 8
            for i in range(0, len(file_path_list), batch_size):
                batch_file_path_list = file_path_list[i:i + batch_size]
                
                # 异步批量处理
                handle_tasks = []
                for file_path in batch_file_path_list:
                    handle_tasks.append(LogDetectionBasedOnEmbeddingWorker.handle_single_log_file(
                        file_path, 
                        max_anomaly_log_count, 
                        anomaly_keywords, 
                        time_start, 
                        time_end,
                        query_vector,
                        intent,
                        enable_template
                    ))
                
                batch_results = await asyncio.gather(*handle_tasks)
                
                # 合并结果
                for log_model_list, candidate_unnormal_log_model_list in batch_results:
                    log_models.extend(log_model_list)
                    candidate_unnormal_log_models.extend(candidate_unnormal_log_model_list)
                
                # 更新进度
                processed_files += len(batch_file_path_list)
                progress = 5.0 + (processed_files / total_files) * 90.0
                logger.info(f"[进度更新] task_id={task_id}, total={progress:.1f}%")
                await TaskManager.update_task_by_id(task_id, {"completion_precent": min(progress, 95.0)})
            
            # 最终处理：全局排序
            candidate_unnormal_log_models.sort(
                key=lambda x: x.anomaly_score, reverse=True)
            candidate_unnormal_log_models = candidate_unnormal_log_models[:max_anomaly_log_count]
            await TaskManager.update_task_by_id(task_id, {"completion_precent": 97.5})
            
            await LogDetectionBasedOnEmbeddingWorker.add_log_parse_results(candidate_unnormal_log_models, log_models, task_id)
            
            # 任务完成
            progress = 100.0
            await TaskManager.update_task_by_id(task_id, {"completion_precent": progress, "status": TaskStatusEnum.SUCCESSFUL_PENDING_REMOVE.value})
            logger.info(f"[进度更新] task_id={task_id}, total=100.0%")
            logger.info(f"[任务完成] 共处理日志{len(log_models)}条, 检出异常{len(candidate_unnormal_log_models)}条")
        except Exception as e:
            await TaskManager.update_task_by_id(task_id, {"status": TaskStatusEnum.FAILED_PENDING_REMOVE.value})
            logger.exception(f"[任务失败] task_id={task_id}, 错误信息: {str(e)}")
            raise e
