# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""配置文件处理模块"""
import toml
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
from pathlib import Path
from copy import deepcopy
import sys
import os


class LLMConfig(BaseModel):
    """LLM配置模型"""
    llm_endpoint: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1", description="LLM远程主机地址")
    llm_api_key: str = Field(default="", description="LLM API Key")
    llm_model_name: str = Field(default="qwen3-coder-480b-a35b-instruct", description="LLM模型名称")
    max_tokens: int = Field(default=8192, description="LLM最大Token数")
    temperature: float = Field(default=0.7, description="LLM温度参数")


class EmbeddingType(str, Enum):
    OPENAI = "openai"
    MINDIE = "mindie"


class EmbeddingConfig(BaseModel):
    """Embedding配置模型"""
    embedding_type: EmbeddingType = Field(default=EmbeddingType.OPENAI, description="向量化类型")
    embedding_endpoint: str = Field(default="", description="向量化API地址")
    embedding_api_key: str = Field(default="", description="向量化API Key")
    embedding_model_name: str = Field(default="text-embedding-3-small", description="向量化模型名称")


class ConfigModel(BaseModel):
    """公共配置模型"""
    embedding: EmbeddingConfig = Field(default=EmbeddingConfig(), description="向量化配置")
    llm: LLMConfig = Field(default=LLMConfig(), description="LLM配置")


class BaseConfig():
    """配置文件读取和使用Class"""

    def __init__(self) -> None:
        """读取配置文件；当PROD环境变量设置时，配置文件将在读取后删除"""
        config_file = os.path.join("config.toml")
        self._config = ConfigModel.model_validate(toml.load(config_file))

    def get_config(self) -> ConfigModel:
        """获取配置文件内容"""
        return deepcopy(self._config)
