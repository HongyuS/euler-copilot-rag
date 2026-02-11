
import re
from apps.parser.base_parser import BaseParser
from apps.enum.log import LogTypeEnum


class FtraceParser(BaseParser):
    """
    FtraceParser
    """
    log_type: LogTypeEnum = LogTypeEnum.FTRACE
    prio = 60
