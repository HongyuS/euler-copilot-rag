import os
import sys
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# 添加 mcp_center 目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
mcp_center_dir = os.path.abspath(os.path.join(current_dir, '../../../../'))
if mcp_center_dir not in sys.path:
    sys.path.insert(0, mcp_center_dir)

# 导入配置加载器
from config.private.rag.config_loader import RemoteInfoConfig

# 配置加载器实例
_config_loader: Optional[RemoteInfoConfig] = None

# 配置缓存
_config: Dict[str, Any] = None


def _load_config() -> Dict[str, Any]:
    """
    加载配置文件
    仅从 mcp_center/config 系统加载（公共配置和私有配置）
    :return: 配置字典
    :raises: 如果配置加载失败，抛出异常
    """
    global _config, _config_loader
    
    if _config is not None:
        return _config
    
    # 初始化配置加载器
    if _config_loader is None:
        _config_loader = RemoteInfoConfig()
    
    # 从配置加载器获取配置
    cfg = _config_loader.get_config()
    
    # 从公共配置获取 embedding
    embedding_cfg = cfg.public_config.embedding
    config_dict = {
        "embedding": {
            "type": embedding_cfg.type,
            "api_key": embedding_cfg.api_key,
            "endpoint": embedding_cfg.endpoint,
            "model_name": embedding_cfg.model_name,
            "timeout": embedding_cfg.timeout,
            "vector_dimension": embedding_cfg.vector_dimension
        }
    }
    
    # 从私有配置获取 token 和 search
    if cfg.private_config is None:
        raise ValueError("私有配置未加载")
    
    token_cfg = cfg.private_config.token
    search_cfg = cfg.private_config.search
    config_dict["token"] = {
        "model": token_cfg.model,
        "max_tokens": token_cfg.max_tokens,
        "default_chunk_size": token_cfg.default_chunk_size
    }
    config_dict["search"] = {
        "default_top_k": search_cfg.default_top_k,
        "max_top_k": search_cfg.max_top_k
    }
    
    # 从私有配置获取 github
    github_cfg = cfg.private_config.github
    config_dict["github"] = {
        "enabled": github_cfg.enabled,
        "token": github_cfg.token,
        "issue_repos": github_cfg.issue_repos,
        "commit_repo": github_cfg.commit_repo,
        "default_online_top_k": github_cfg.default_online_top_k,
        "max_candidates": github_cfg.max_candidates,
        "request_timeout": github_cfg.request_timeout,
        "rate_limit_delay": github_cfg.rate_limit_delay
    }
    
    _config = config_dict
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


def reload_config():
    """当配置更新后重新加载缓存"""
    global _config, _config_loader
    _config = None
    _config_loader = None
