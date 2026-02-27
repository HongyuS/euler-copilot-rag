
import re
from apps.service.embedding import Embedding
from apps.parser.log_feature import log_feature_class_mapping
from apps.enum.log import LogTypeEnum
from apps.schemas.log import LogModel


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
    async def parse_log_file(file_path: str,
                             need_embedding: bool = False,
                             need_split_by_regex: bool = False,
                             chunk_size: int = 1024) -> list[LogModel]:
        log_lines = LogParser.read_log_file(file_path)
        log_models = []
        current = ""
        offset = 0
        if need_split_by_regex:
            index = 0
            while index < len(log_lines):
                log_line = log_lines[index]
                log_type = LogParser.get_log_line_type(log_line)
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
        if need_embedding:
            embeddings = await Embedding.vectorize_embedding([log_model.content for log_model in log_models])
            for i, log_model in enumerate(log_models):
                log_model.vector = embeddings[i]
        return log_models
