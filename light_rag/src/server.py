"""
MCP Server for RAG Knowledge Base Management
基于 SSE 传输的 RAG 知识库 MCP 服务
"""
import asyncio
import os
import sys
import yaml
from typing import Optional, Dict, Any, List
from mcp.server.fastmcp import FastMCP

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 导入 tool.py 中的所有函数
from tool import (
    knowledge_base_manager,
    document_manager,
    search
)

# 导入本地配置
from common.config import get_language, get_task_db_path
from sqlite.task_sqlite import init_task_db
from manager.task_manager import TaskManager
from common.task import run_task_listener_in_process

# 加载 prompt 配置
config_path = os.path.join(current_dir, "prompt.yaml")
with open(config_path, 'r', encoding='utf-8') as f:
    tool_configs = yaml.safe_load(f)["tools"]

_language = get_language()


def get_tool_description(tool_name: str) -> str:
    """根据配置的语言获取工具描述"""
    tool_desc = tool_configs.get(tool_name, {})
    if _language == "zh":
        return tool_desc.get("zh", tool_desc.get("en", ""))
    return tool_desc.get("en", tool_desc.get("zh", ""))


# SSE 服务配置（host/port）
_host = "0.0.0.0"
_port = 12311
mcp = FastMCP("RAG Knowledge Base MCP Server", host=_host, port=_port)


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


@mcp.tool(
    name="document_manager",
    description=get_tool_description("document_manager")
)
async def mcp_document_manager(
    action: str,
    file_paths: Optional[List[str]] = None,
    kb_name: Optional[str] = None,
    chunk_size: Optional[int] = None,
    doc_name: Optional[str] = None,
    task_id: Optional[str] = None,
) -> Dict[str, Any]:
    """文档管理器"""
    return await document_manager(action, file_paths, kb_name, chunk_size, doc_name, task_id)


@mcp.tool(
    name="search",
    description=get_tool_description("search")
)
async def mcp_search(
    query: str,
    kb_names: List[str],
    top_k: Optional[int] = None,
    keyword_weight: Optional[float] = None,
    banned_chunk_ids: Optional[List[str]] = None,
    online: bool = False,
    online_top_k: Optional[int] = None
) -> Dict[str, Any]:
    """搜索"""
    return await search(query, kb_names, top_k, keyword_weight, banned_chunk_ids, online, online_top_k)


if __name__ == "__main__":
    init_task_db(get_task_db_path())
    asyncio.run(TaskManager.update_running_tasks_to_pending_tasks())
    run_task_listener_in_process()
    mcp.run(transport='sse')
