import json
from rag_core.ENUM.json import SchemaType
from jsonschema import validate, ValidationError
import logging

logger = logging.getLogger(__name__)


class SchemaHandler:
    """处理json schema的工具类，提供验证、转换等功能"""

    @staticmethod
    def validate_schema(data: dict, schema: dict) -> bool:
        """验证数据是否符合json schema"""
        try:
            validate(instance=data, schema=schema)
            return True
        except ValidationError as e:
            logger.error(f"Schema validation error: {e.message}")
            return False

    @staticmethod
    def get_schema_type(field: str | list[str], schema: dict) -> SchemaType | None:
        """根据字段名从json schema中获取字段类型"""
        properties = schema.get("properties", {})
        if isinstance(field, str):
            field_schema = properties.get(field)
        elif isinstance(field, list):
            for f in field:
                field_schema = properties.get(f)
                if field_schema and "properties" in field_schema:
                    properties = field_schema.get("properties", {})
                else:
                    return None
        if field_schema:
            type_ = field_schema.get("type")
            try:
                return SchemaType(type_)
            except ValueError:
                logger.error(f"Unsupported schema type: {type_}")
                return None
        return None
