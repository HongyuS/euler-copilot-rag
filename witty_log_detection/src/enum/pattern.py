from enum import Enum


class PreciseSearchPatternEnum(str, Enum):
    """精确检索特征模式枚举"""
    IP_ADDRESS = r'\d+\.\d+\.\d+\.\d+'  # IP地址
    HEX_CODE = r'0x[0-9a-fA-F]+'      # 十六进制错误码
    ERROR_CODE_FORMAT = r'[A-Z]+-\d+'  # 错误码格式如ERR-123
    ERROR_CODE = r'错误码\s*\d+'         # 错误码XXX格式
    PORT = r'端口\s*\d+'                 # 端口XXX格式
    NUMBER_DIGITS = r'\d{3,}'            # 3位以上数字（端口号、错误码等）
    DOMAIN = r'([a-zA-Z0-9_-]+)\.[a-zA-Z]{2,}'  # 域名

    @classmethod
    def get_all_patterns(cls) -> list[str]:
        """获取所有精确检索模式列表"""
        return [pattern.value for pattern in cls]


class QueryIntentEnum(str, Enum):
    """查询意图类型枚举"""
    PRECISE_SEARCH = "precise_search"
    SPECIFIC_TYPE = "specific_type"
    ANOMALY_DETECTION = "anomaly_detection"
