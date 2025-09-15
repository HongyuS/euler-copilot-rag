# Copyright (c) Huawei Technologies Co., Ltd. 2023-2024. All rights reserved.
import os

from dotenv import dotenv_values
from pydantic import BaseModel, Field


class ConfigModel(BaseModel):

    # LLM
    LLM_KEY: str = Field(None, description="语言模型访问密钥")
    LLM_URL: str = Field(None, description="语言模型服务的基础URL")
    LLM_MAX_TOKENS: int = Field(None, description="单次请求中允许的最大Token数")
    LLM_MODEL: str = Field(None, description="使用的语言模型名称或版本")

class Config:
    config: ConfigModel

    def __init__(self):
        if os.getenv("CONFIG"):
            config_file = os.getenv("CONFIG")
        else:
            config_file = "chat2db/common/.env"
        self.config = ConfigModel(**(dotenv_values(config_file)))
        if os.getenv("PROD"):
            os.remove(config_file)

    def __getitem__(self, key):
        if key in self.config.__dict__:
            return self.config.__dict__[key]
        return None


config = Config()
