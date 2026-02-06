
import re
import logging

from cv2 import line
from apps.enum.log import LogTypeEnum
from apps.schemas.log import LogModel


class BaseParser:
    """
    BaseParser
    """
    log_type: LogTypeEnum = LogTypeEnum.OTHER
    prio = 0
    postive_keywords: dict[str, int] = {}
    negative_keywords: dict[str, int] = {}
    mandatory: dict[str, list[str]] | list[str] = []

    @staticmethod
    def find_worker_class(worker_name):
        subclasses = BaseParser.__subclasses__()
        for subclass in subclasses:
            if subclass.log_type == worker_name:
                return subclass
        return None

    @staticmethod
    async def extract_message_body(line: str) -> str:
        """
        Extract message body from log line.
        :param line: log line
        :return: message body
        """
        return line

    @staticmethod
    async def get_type_confidence(log_lines: list[str]) -> dict[LogTypeEnum, float]:
        """
        Get type confidence for a given line.
        :param line: log line
        :return: dict of LogTypeEnum and confidence score
        """
        # 获得所有子类
        subclasses = BaseParser.__subclasses__()
        confidence: dict[LogTypeEnum, float] = {}
        for subclass in subclasses:
            for log_line in log_lines:
                confidence[subclass.log_type] = confidence.get(subclass.log_type, 0) + (await subclass.is_matched(log_line))
            confidence[subclass.log_type] /= len(log_lines)
        return confidence

    @staticmethod
    async def is_matched(log_line: str) -> bool:
        """
        判断单行日志是否匹配该Parser的特征
        """
        for pattern in BaseParser.negative_keywords.keys():
            if re.search(pattern, log_line):
                return False
        for pattern in BaseParser.postive_keywords.keys():
            if re.search(pattern, log_line):
                return True
        for pattern in BaseParser.mandatory.keys():
            if re.search(pattern, log_line):
                return True

    @staticmethod
    async def match_log_type(log_lines: list[str]) -> LogTypeEnum:
        confidence = await BaseParser.get_type_confidence(log_lines)
        candidates = [(t, c) for t, c in confidence.items() if c > 0]
        if not candidates:
            return LogTypeEnum.OTHER
        subclasses = BaseParser.__subclasses__()
        subclasses_ordered = []
        for subclass in subclasses:
            subclasses_ordered.append((subclass.prio, subclass))
        subclasses_ordered.sort(key=lambda x: x[0], reverse=True)
        for _, subclass in subclasses_ordered:
            if await subclass.is_matched(log_lines):
                return subclass.log_type
        if subclasses_ordered[0][0] < 60:
            return LogTypeEnum.OTHER
        return subclasses_ordered[0][1].log_type

    @staticmethod
    async def split_logs(log_text: str) -> list[LogModel]:
        result = []
        log_lines = [line.rstrip("\n") for line in log_text.splitlines()]
        log_type = await BaseParser.match_log_type(log_lines)
        if log_type == LogTypeEnum.OTHER:
            for _, line in enumerate(log_lines):
                result.append(LogModel(
                    log_type=LogTypeEnum.OTHER,
                    offset=_,
                    content=line,
                )
                )
        subclass = BaseParser.find_worker_class(log_type)
        return await subclass.split_logs(log_text) if subclass else result
