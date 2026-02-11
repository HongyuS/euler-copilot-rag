
import re
from apps.parser.base_parser import BaseParser
from apps.enum.log import LogTypeEnum


class BashParser(BaseParser):
    """
    BashParser
    """
    log_type: LogTypeEnum = LogTypeEnum.BASH
    prio = 60
    pass
