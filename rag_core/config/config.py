import os
from copy import deepcopy
from dotenv import dotenv_values
from rag_core.schema.config import ConfigModel


class Config:
    config: ConfigModel

    def __init__(self):
        if os.getenv("CONFIG"):
            config_file = os.getenv("CONFIG")
        else:
            config_file = "rag_core/.env"
        self.config = ConfigModel(**(dotenv_values(config_file)))
        if os.getenv("PROD"):
            os.remove(config_file)

    def get_config(self) -> ConfigModel:
        """获取配置文件内容"""
        return deepcopy(self.config)
