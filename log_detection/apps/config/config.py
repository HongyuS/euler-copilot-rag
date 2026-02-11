# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
"""配置文件处理模块"""

import os
from copy import deepcopy

from apps.schemas.config import ConfigModel


class Config():
    """配置文件读取和使用Class"""

    _config: ConfigModel

    def __init__(self) -> None:
        """从ConfigModel中获取所有键值，并从环境变量中覆盖它们（如果存在）"""
        config_model_dict = ConfigModel().model_dump(exclude_none=True, by_alias=True)
        for key in config_model_dict.keys():
            env_value = os.getenv(key)
            if env_value is not None:
                config_model_dict[key] = env_value
        self._config = ConfigModel.model_validate(config_model_dict)

    def get_config(self) -> ConfigModel:
        """获取配置文件内容"""
        return deepcopy(self._config)
