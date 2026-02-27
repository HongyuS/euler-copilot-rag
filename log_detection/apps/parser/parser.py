
import re
from datetime import datetime, timedelta
from apps.service.embedding import Embedding
from apps.parser.log_feature import log_feature_class_mapping
from apps.enum.log import LogTypeEnum, LogValueEnum
from apps.schemas.log import LogModel, LogTemplateModel


class LogParser:
    """
    日志解析器，负责从日志文件中提取日志信息，并进行日志类型分类
    """
    @staticmethod
    def get_log_line_type(log_line: str) -> LogTypeEnum:
        """
        获取单行日志的类型
        """
        score_dict = {}
        for log_type in LogTypeEnum:
            if log_type in log_feature_class_mapping:
                keywrods_regex_and_scores = log_feature_class_mapping[
                    log_type].keywords_regex_and_scores
                score = 0
                for keyword_regex, keyword_score in keywrods_regex_and_scores["normal"]:
                    if re.search(keyword_regex, log_line):
                        score += keyword_score
                for keyword_regex, keyword_score in keywrods_regex_and_scores["anomalous"]:
                    if re.search(keyword_regex, log_line):
                        score += keyword_score
                score_dict[log_type] = score
        # 如果所有的日志类型得分都为0，则默认为unknown类型
        if all(score == 0 for score in score_dict.values()):
            return LogTypeEnum.UNKNOWN
        # 获取得分最高的日志类型
        best_log_type = max(score_dict, key=score_dict.get)
        return best_log_type

    @staticmethod
    def read_log_file(file_path: str) -> list[str]:
        """
        读取日志文件，返回日志模型列表
        """
        log_lines = []
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                log_lines.append(line.strip())
        return log_lines

    @staticmethod
    async def get_log_template(log: LogModel) -> LogModel:
        """获取日志模板"""
        # 这里实现获取日志模板的具体逻辑
        log_type: LogTypeEnum = log.log_type
        value_mask = {

            LogValueEnum.TIMESTAMP: "<timestamp>",
            LogValueEnum.LEVEL: "<level>",
            LogValueEnum.IP: "<ip>",
            LogValueEnum.PORT: "<port>",
            LogValueEnum.PID: "<pid>",
            LogValueEnum.TID: "<tid>"
        }
        template = log.content
        for log_value_enum in LogValueEnum:
            regex = log_feature_class_mapping[log_type].capture_patterns.get(
                log_value_enum.value, None)
            if regex is not None:
                template = re.sub(regex, value_mask[log_value_enum], template)
        log_template = LogTemplateModel(
            log_id=log.id,
            template=template,
        )
        return log_template

    @staticmethod
    async def filter_log_models_not_in_time_range(log_models: list[LogModel], time_start: datetime | None, time_end: datetime | None) -> list[LogModel]:
        """获取日志模型的时间戳"""
        # 这里实现获取日志模型时间戳的具体逻辑
        log_models_in_time_range = []
        for log_model in log_models:
            start_time = None
            end_time = None
            log_type: LogTypeEnum = log_model.log_type
            tiemstamp_regex = log_feature_class_mapping[log_type].capture_patterns.get(
                LogValueEnum.TIMESTAMP.value, None)
            if tiemstamp_regex is not None:
                timestamp = re.search(tiemstamp_regex, log_model.content)
                if timestamp is not None:
                    # 获取第一个匹配的时间戳字符串
                    timestamp_str = timestamp.group(0)
                    # 将时间戳字符串转换为datetime对象
                    time_fromat_list = [
                        "%Y-%m-%d %H:%M:%S",
                        "%Y/%m/%d %H:%M:%S",
                        "%Y-%m-%d %H:%M:%S,%f",
                        "%Y/%m/%d %H:%M:%S,%f",
                        "%b %d %H:%M:%S",
                        "%b %d %H:%M:%S,%f"

                    ]
                    for time_fromat in time_fromat_list:
                        try:
                            timestamp_dt = datetime.strptime(
                                timestamp_str, time_fromat)
                            start_time = min(
                                start_time, timestamp_dt) if start_time is not None else timestamp_dt
                            end_time = max(
                                end_time, timestamp_dt) if end_time is not None else timestamp_dt
                            break
                        except ValueError:
                            continue
            delta = timedelta(minutes=5)
            if time_start is not None and start_time is not None and start_time > time_end + delta:
                continue
            if time_end is not None and end_time is not None and end_time < time_start - delta:
                continue
            log_model.start_time = start_time
            log_model.end_time = end_time
            log_models_in_time_range.append(log_model)

        return log_models_in_time_range

    @staticmethod
    async def parse_log_file(file_path: str,
                             need_embedding: bool = False,
                             need_split_by_regex: bool = False,
                             time_start: datetime | None = None,
                             time_end: datetime | None = None,
                             chunk_size: int = 1024) -> list[LogModel]:
        log_lines = LogParser.read_log_file(file_path)
        log_models = []
        current = ""
        offset = 0
        if need_split_by_regex:
            index = 0
            while index < len(log_lines):
                log_line = log_lines[index]
                # 提取时间戳
                log_type = LogParser.get_log_line_type(log_line)
                if log_type == LogTypeEnum.UNKNOWN:
                    log_models.append(LogModel(
                        file_path=file_path,
                        log_type=log_type,
                        offset=offset,
                        content=log_line
                    ))
                    offset += 1
                    index += 1
                    continue
                # 判断是否为连续日志的开头，
                match_header_regex = None
                for header_regex in log_feature_class_mapping[log_type].mandatory:
                    if re.search(header_regex, log_line):
                        match_header_regex = header_regex
                        break
                if match_header_regex is not None:
                    current = log_line+"\n"
                    index += 1
                    while index < len(log_lines):
                        is_continuous = False
                        for continuous_regex in log_feature_class_mapping[log_type].mandatory[match_header_regex]:
                            if re.search(continuous_regex, log_lines[index]):
                                is_continuous = True
                                break
                        if is_continuous:
                            current += log_lines[index] + "\n"
                            index += 1
                        else:
                            break
                    log_models.append(LogModel(
                        file_path=file_path,
                        log_type=log_type,
                        offset=offset,
                        content=current.strip()))
                    offset += 1
                else:
                    log_models.append(LogModel(
                        file_path=file_path,
                        log_type=log_type,
                        offset=offset,
                        content=log_line
                    ))
                    offset += 1
        else:
            for log_line in log_lines:
                if len(current) + len(log_line) > chunk_size:
                    log_models.append(LogModel(
                        file_path=file_path,
                        log_type=LogParser.get_log_line_type(current),
                        offset=offset,
                        content=current
                    ))
                    offset += 1
                    current = ""
                current += log_line + "\n"
        if time_start is not None or time_end is not None:
            log_models = await LogParser.filter_log_models_not_in_time_range(
                log_models, time_start, time_end)
        if need_embedding:
            embeddings = await Embedding.vectorize_embedding([log_model.content for log_model in log_models])
            for i, log_model in enumerate(log_models):
                log_model.vector = embeddings[i]
        return log_models
