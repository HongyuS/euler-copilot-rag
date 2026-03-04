"""
MCP Server for Copilot-0 Knowledge Base Management
将 copilot-0 项目启动为 MCP 服务
"""
import os
import sys
import yaml
from typing import Optional, Dict, Any, List
from mcp.server import FastMCP

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 添加 mcp_center 目录到路径（用于导入配置模块）
mcp_center_dir = os.path.abspath(os.path.join(current_dir, '../../..'))
if mcp_center_dir not in sys.path:
    sys.path.insert(0, mcp_center_dir)

# 导入配置加载器
from config.public.base_config_loader import LanguageEnum
from config.private.rag.config_loader import RemoteInfoConfig as RagConfig

# 导入 tool.py 中的所有函数
from tool import (
    knowledge_base_manager,
    document_manager,
    search
)

# 加载配置文件
config_path = os.path.join(current_dir, "prompt.yaml")
with open(config_path, 'r', encoding='utf-8') as f:
    tool_configs = yaml.safe_load(f)["tools"]

# 获取语言配置
_config = RagConfig().get_config()
_language = _config.public_config.language

# 辅助函数：根据语言获取工具描述
def get_tool_description(tool_name: str) -> str:
    """根据配置的语言获取工具描述"""
    tool_desc = tool_configs.get(tool_name, {})
    if _language == LanguageEnum.ZH:
        return tool_desc.get("zh", tool_desc.get("en", ""))
    else:
        return tool_desc.get("en", tool_desc.get("zh", ""))

# 创建 MCP 服务器
_config = RagConfig().get_config()
port = _config.private_config.port  # 从配置读取端口 12311
host = "0.0.0.0"  # 或从配置读取

mcp = FastMCP("Copilot-0 Knowledge Base MCP Server", host=host, port=port)

# 注册同步函数
@mcp.tool(
    name="Knowledge_base_manager",
    description=get_tool_description("Knowledge_base_manager")
)
def mcp_knowledge_base_manager(
    action: str,
    kb_name: Optional[str] = None,
    chunk_size: Optional[int] = None,
    embedding_model: Optional[str] = None,
    embedding_endpoint: Optional[str] = None,
    embedding_api_key: Optional[str] = None,
    keyword: Optional[str] = None
) -> Dict[str, Any]:
    """知识库管理器"""
    return knowledge_base_manager(action, kb_name, chunk_size, embedding_model, embedding_endpoint, embedding_api_key, keyword)


# 注册异步函数
@mcp.tool(
    name="document_manager",
    description=get_tool_description("document_manager")
)
async def mcp_document_manager(
    action: str,
    file_paths: Optional[List[str]] = None,
    kb_name: Optional[str] = None,
    chunk_size: Optional[int] = None,
    doc_name: Optional[str] = None
) -> Dict[str, Any]:
    """文档管理器"""
    return await document_manager(action, file_paths, kb_name, chunk_size, doc_name)


@mcp.tool(
    name="search",
    description=get_tool_description("search")
)
async def mcp_search(query: str, kb_names: List[str], top_k: Optional[int] = None, keyword_weight: Optional[float] = None, banned_chunk_ids: Optional[List[str]] = None, online: bool = False, online_top_k: Optional[int] = None) -> Dict[str, Any]:
    """搜索（异步）"""
    return await search(query, kb_names, top_k, keyword_weight, banned_chunk_ids, online, online_top_k)


if __name__ == "__main__":
    # 启动 MCP 服务器
    mcp.run(transport='sse')

