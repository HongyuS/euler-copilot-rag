"""
枚举类型
Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""

from enum import Enum


class LogicOperator(str, Enum):
    """逻辑运算符枚举"""

    AND = "and"
    OR = "or"
    AND_NOT = "and_not"
    OR_NOT = "or_not"


class OperationType(str, Enum):
    """比较操作符枚举"""

    EQ = "eq"
    NE = "ne"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    LIKE = "like"
    LIKE_LEFT = "like_left"
    LIKE_RIGHT = "like_right"
    IN = "in"
    NOT_IN = "not_in"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    BETWEEN = "between"


class FieldType(str, Enum):
    """
    完整字段类型枚举（JSON查询 + 数据库 + 接口全场景通用）
    支持多层嵌套查询的类型校验
    """

    # 基础类型
    STRING = "string"  # 字符串
    number = "number"  # 数字（整数或浮点数）
    BOOLEAN = "boolean"  # 布尔

    # 时间日期
    TIMESTAMP = "timestamp"  # 时间戳（毫秒/秒）

    # 集合/数组
    ARRAY = "array"  # 数组/列表
    OBJECT = "object"  # 嵌套对象（用于嵌套JSON字段）
