# Copyright (c) Huawei Technologies Co., Ltd. 2023-2025. All rights reserved.
from config.public.base_config_loader import BaseConfig
import os
from pydantic import BaseModel, Field
import toml


class TokenConfigModel(BaseModel):
    """Token配置模型"""
    model: str = Field(default="gpt-4", description="Token模型")
    max_tokens: int = Field(default=8192, description="最大Token数")
    default_chunk_size: int = Field(default=1024, description="默认chunk大小")


class SearchConfigModel(BaseModel):
    """检索配置模型"""
    default_top_k: int = Field(default=5, description="默认返回数量")
    max_top_k: int = Field(default=100, description="最大返回数量")


class GitHubConfigModel(BaseModel):
    """GitHub线上检索配置模型"""
    enabled: bool = Field(default=False, description="是否启用GitHub检索功能")
    token: str = Field(default="", description="GitHub Token（可从环境变量读取）")
    issue_repos: list = Field(default_factory=lambda: ["raspberrypi/linux", "microsoft/WSL2-Linux-Kernel"], description="Issue搜索仓库列表")
    commit_repo: str = Field(default="torvalds/linux", description="Commit搜索仓库")
    default_online_top_k: int = Field(default=5, description="默认返回数量")
    max_candidates: int = Field(default=20, description="粗搜候选数量")
    request_timeout: int = Field(default=10, description="GitHub API请求超时（秒）")
    rate_limit_delay: int = Field(default=1, description="请求间隔（秒，避免触发限流）")


class RemoteInfoConfigModel(BaseModel):
    """RAG私有配置模型"""
    port: int = Field(default=12311, description="MCP服务端口")
    token: TokenConfigModel = Field(default_factory=TokenConfigModel, description="Token配置")
    search: SearchConfigModel = Field(default_factory=SearchConfigModel, description="检索配置")
    github: GitHubConfigModel = Field(default_factory=GitHubConfigModel, description="GitHub检索配置")


class RemoteInfoConfig(BaseConfig):
    """顶层配置文件读取和使用Class"""

    def __init__(self) -> None:
        """读取配置文件"""
        super().__init__()
        self.load_private_config()

    def load_private_config(self) -> None:
        """加载私有配置文件"""
        from config.public.base_config_loader import project_root
        config_file = os.getenv("RAG_CONFIG")
        if config_file is None:
            config_file = os.path.join(project_root, "config", "private", "rag", "config.toml")
        if not os.path.exists(config_file):
            self._config.private_config = RemoteInfoConfigModel()
            return
        config_data = toml.load(config_file)
        if "token" in config_data and isinstance(config_data["token"], dict):
            config_data["token"] = TokenConfigModel.model_validate(config_data["token"])
        else:
            config_data["token"] = TokenConfigModel()
        if "search" in config_data and isinstance(config_data["search"], dict):
            config_data["search"] = SearchConfigModel.model_validate(config_data["search"])
        else:
            config_data["search"] = SearchConfigModel()
        if "github" in config_data and isinstance(config_data["github"], dict):
            # 支持从环境变量读取token
            if not config_data["github"].get("token") and os.getenv("GITHUB_TOKEN"):
                config_data["github"]["token"] = os.getenv("GITHUB_TOKEN")
            config_data["github"] = GitHubConfigModel.model_validate(config_data["github"])
        else:
            config_data["github"] = GitHubConfigModel()
        self._config.private_config = RemoteInfoConfigModel.model_validate(config_data)
