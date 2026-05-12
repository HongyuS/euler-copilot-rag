"""
枚举类型
Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""

from enum import Enum


class LogicOperatorType(str, Enum):
    """逻辑运算符枚举"""

    AND = "and"
    OR = "or"
    AND_NOT = "and_not"
    OR_NOT = "or_not"


class SchemaType(str, Enum):
    """
    完整字段类型枚举（JSON查询 + 数据库 + 接口全场景通用）
    支持多层嵌套查询的类型校验
    """

    # 基础类型
    STRING = "string"  # 字符串
    number = "number"  # 数字（整数或浮点数）
    INTEGER = "integer"  # 整数
    BOOLEAN = "boolean"  # 布尔

    # 集合/数组
    ARRAY = "array"  # 数组/列表
    OBJECT = "object"  # 嵌套对象（用于嵌套JSON字段）

    def check_type(self, value: any) -> bool:
        """检查值是否符合枚举定义的类型"""
        if self == SchemaType.STRING:
            return isinstance(value, str)
        elif self == SchemaType.number:
            return isinstance(value, (int, float))
        elif self == SchemaType.INTEGER:
            return isinstance(value, int)
        elif self == SchemaType.BOOLEAN:
            return isinstance(value, bool)
        elif self == SchemaType.ARRAY:
            return isinstance(value, list)
        elif self == SchemaType.OBJECT:
            return isinstance(value, dict)
        else:
            return False


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
    LENGTH_EQ = "length_eq"
    LENGTH_GT = "length_gt"
    LENGTH_GTE = "length_gte"
    LENGTH_LT = "length_lt"
    LENGTH_LTE = "length_lte"

    def check_operation(self, schema_type: SchemaType) -> bool:
        """检查操作符是否适用于给定的SchemaType"""
        if self in {OperationType.EQ, OperationType.NE}:
            return True  # 所有类型都支持等于和不等于
        elif self in {
            OperationType.GT,
            OperationType.GTE,
            OperationType.LT,
            OperationType.LTE,
        }:
            return schema_type in {
                SchemaType.number,
                SchemaType.INTEGER,
                SchemaType.STRING,
            }  # 数字和字符串支持比较大小
        elif self in {
            OperationType.LIKE,
            OperationType.LIKE_LEFT,
            OperationType.LIKE_RIGHT,
        }:
            return schema_type == SchemaType.STRING  # 仅字符串支持模糊匹配
        elif self in {OperationType.IN, OperationType.NOT_IN}:
            return True  # 所有类型都支持包含和不包含
        elif self in {OperationType.IS_NULL, OperationType.IS_NOT_NULL}:
            return True  # 所有类型都支持空值检查
        elif self == OperationType.BETWEEN:
            return schema_type in {
                SchemaType.number,
                SchemaType.INTEGER,
                SchemaType.STRING,
            }  # 数字和字符串支持范围查询
        elif self in {
            OperationType.LENGTH_EQ,
            OperationType.LENGTH_GT,
            OperationType.LENGTH_GTE,
            OperationType.LENGTH_LT,
            OperationType.LENGTH_LTE,
        }:
            return schema_type in {
                SchemaType.ARRAY,
                SchemaType.STRING,
            }  # 数组和字符串支持长度比较
        else:
            return False
