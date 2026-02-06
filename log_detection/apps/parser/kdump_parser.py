
import re
from apps.parser.base_parser import BaseParser
from apps.enum.log import LogTypeEnum


class KudumpParser(BaseParser):
    """
    KudumpParser
    """
    log_type: LogTypeEnum = LogTypeEnum.KDUMP
    prio = 80
    pass
