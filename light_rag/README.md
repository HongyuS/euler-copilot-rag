# RAG MCP Server

基于 SQLite 的 RAG 知识库 MCP 服务，提供知识库管理、文档导入、混合检索（关键词+向量）及 GitHub 在线检索。

## 传输方式

stdio（由 MCP 客户端按需启动）

## 配置

配置文件 `src/config.toml`，支持环境变量 `RAG_CONFIG` 指定配置文件路径。

## 工具

- **Knowledge_base_manager**: 知识库管理（创建、列出）
- **document_manager**: 文档管理（导入、获取解析结果）
- **search**: 混合检索

## 测试

运行测试客户端（需先安装 mcp 及 src/requirements.txt 中的依赖）：

```bash
cd servers/rag_mcp
python mcp_client.py
```
