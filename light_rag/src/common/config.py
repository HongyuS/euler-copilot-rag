"""RAG MCP 本地配置加载"""
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# 配置缓存
_config: Optional[Dict[str, Any]] = None


def _get_config_path() -> str:
    """获取配置文件路径"""
    config_file = os.getenv("RAG_CONFIG")
    if config_file and os.path.exists(config_file):
        return config_file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, "..", "config.toml")


def _load_config() -> Dict[str, Any]:
    """从本地 config.toml 加载配置"""
    global _config
    if _config is not None:
        return _config

    import toml
    config_path = _get_config_path()
    if not os.path.exists(config_path):
        _config = {
            "embedding": {
                "type": "openai",
                "api_key": "",
                "endpoint": "",
                "model_name": "text-embedding-ada-002",
                "timeout": 30,
                "vector_dimension": 1024,
            },
            "token": {
                "model": "gpt-4",
                "max_tokens": 8192,
                "default_chunk_size": 1024,
            },
            "search": {
                "default_top_k": 5,
                "max_top_k": 100,
            },
            "github": {
                "enabled": False,
                "token": os.getenv("GITHUB_TOKEN", ""),
                "issue_repos": ["raspberrypi/linux", "microsoft/WSL2-Linux-Kernel"],
                "commit_repo": "torvalds/linux",
                "default_online_top_k": 5,
                "max_candidates": 20,
                "request_timeout": 10,
                "rate_limit_delay": 1,
            },
        }
        return _config

    config_data = toml.load(config_path)
    _config = {
        "embedding": {
            "type": config_data.get("embedding", {}).get("type", "openai"),
            "api_key": config_data.get("embedding", {}).get("api_key", ""),
            "endpoint": config_data.get("embedding", {}).get("endpoint", ""),
            "model_name": config_data.get("embedding", {}).get("model_name", "text-embedding-ada-002"),
            "timeout": config_data.get("embedding", {}).get("timeout", 30),
            "vector_dimension": config_data.get("embedding", {}).get("vector_dimension", 1024),
        },
        "token": {
            "model": config_data.get("token", {}).get("model", "gpt-4"),
            "max_tokens": config_data.get("token", {}).get("max_tokens", 8192),
            "default_chunk_size": config_data.get("token", {}).get("default_chunk_size", 1024),
        },
        "search": {
            "default_top_k": config_data.get("search", {}).get("default_top_k", 5),
            "max_top_k": config_data.get("search", {}).get("max_top_k", 100),
        },
        "github": {
            "enabled": config_data.get("github", {}).get("enabled", False),
            "token": config_data.get("github", {}).get("token") or os.getenv("GITHUB_TOKEN", ""),
            "issue_repos": config_data.get("github", {}).get("issue_repos", ["raspberrypi/linux", "microsoft/WSL2-Linux-Kernel"]),
            "commit_repo": config_data.get("github", {}).get("commit_repo", "torvalds/linux"),
            "default_online_top_k": config_data.get("github", {}).get("default_online_top_k", 5),
            "max_candidates": config_data.get("github", {}).get("max_candidates", 20),
            "request_timeout": config_data.get("github", {}).get("request_timeout", 10),
            "rate_limit_delay": config_data.get("github", {}).get("rate_limit_delay", 1),
        },
    }
    return _config


def _cfg() -> Dict[str, Any]:
    """获取配置字典"""
    return _load_config()


def get_embedding_type() -> str:
    return _cfg()["embedding"]["type"]


def get_embedding_api_key() -> str:
    return _cfg()["embedding"]["api_key"]


def get_embedding_endpoint() -> str:
    return _cfg()["embedding"]["endpoint"]


def get_embedding_model_name() -> str:
    return _cfg()["embedding"]["model_name"]


def get_embedding_timeout() -> int:
    return _cfg()["embedding"]["timeout"]


def get_embedding_vector_dimension() -> int:
    return _cfg()["embedding"]["vector_dimension"]


def get_token_model() -> str:
    return _cfg()["token"]["model"]


def get_max_tokens() -> int:
    return _cfg()["token"]["max_tokens"]


def get_default_chunk_size() -> int:
    return _cfg()["token"]["default_chunk_size"]


def get_default_top_k() -> int:
    return _cfg()["search"]["default_top_k"]


def get_github_enabled() -> bool:
    return _cfg()["github"]["enabled"]


def get_github_token() -> str:
    return _cfg()["github"]["token"]


def get_github_issue_repos() -> list:
    return _cfg()["github"]["issue_repos"]


def get_github_commit_repo() -> str:
    return _cfg()["github"]["commit_repo"]


def get_github_default_online_top_k() -> int:
    return _cfg()["github"]["default_online_top_k"]


def get_github_max_candidates() -> int:
    return _cfg()["github"]["max_candidates"]


def get_github_request_timeout() -> int:
    return _cfg()["github"]["request_timeout"]


def get_github_rate_limit_delay() -> int:
    return _cfg()["github"]["rate_limit_delay"]


def get_language() -> str:
    """获取语言配置"""
    config_path = _get_config_path()
    if os.path.exists(config_path):
        import toml
        data = toml.load(config_path)
        return data.get("language", "zh")
    return "zh"


def reload_config():
    """当配置更新后重新加载缓存"""
    global _config
    _config = None
