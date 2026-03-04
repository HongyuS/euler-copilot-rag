#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP客户端测试脚本
用于自动化测试MCP服务器能否成功启动且使用其中的工具
"""

import os
import sys
import asyncio
import json
import logging
import socket
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import AsyncExitStack

# 添加路径以便导入MCP相关模块
current_dir = os.path.dirname(os.path.abspath(__file__))
mcp_center_dir = os.path.abspath(os.path.join(current_dir, '../..'))
if mcp_center_dir not in sys.path:
    sys.path.insert(0, mcp_center_dir)

try:
    from mcp import ClientSession
    from mcp.client.sse import sse_client
except ImportError:
    print("错误: 无法导入MCP模块，请确保已安装 mcp 库")
    print("安装命令: pip install mcp")
    sys.exit(1)


class TestLogger:
    """测试日志记录器"""
    
    def __init__(self, log_dir: str):
        """初始化日志记录器"""
        self.log_dir = log_dir
        self.log_file = None
        self._setup_logger()
    
    def _setup_logger(self):
        """设置日志"""
        # 确保日志目录存在
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
        
        # 生成日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"mcp_test_{timestamp}.txt"
        self.log_file = os.path.join(self.log_dir, log_filename)
        
        # 配置日志 - 先清除已有的handlers避免重复
        logging.getLogger().handlers = []
        
        # 创建文件handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8', mode='w')
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                                         datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        
        # 创建控制台handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(file_formatter)
        
        # 配置根logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        self.logger = logging.getLogger(__name__)
        
        # 确保立即刷新
        file_handler.flush()
    
    def log_step(self, step_num: int, step_name: str, success: bool, result: Dict[str, Any]):
        """记录测试步骤"""
        self.logger.info("="*80)
        self.logger.info(f"步骤 {step_num}: {step_name}")
        self.logger.info("="*80)
        self.logger.info(f"执行状态: {'成功' if success else '失败'}")
        
        # 记录完整的返回结果
        self.logger.info("完整返回结果:")
        try:
            result_str = json.dumps(result, indent=2, ensure_ascii=False, default=str)
            self.logger.info(result_str)
        except Exception as e:
            self.logger.info(f"JSON序列化失败: {e}")
            self.logger.info(f"原始结果: {result}")
        
        # 单独记录关键字段
        if 'message' in result:
            self.logger.info(f"返回消息: {result.get('message', '')}")
        if 'data' in result:
            self.logger.info("返回数据:")
            try:
                data_str = json.dumps(result.get('data', {}), indent=2, ensure_ascii=False, default=str)
                self.logger.info(data_str)
            except Exception as e:
                self.logger.info(f"数据序列化失败: {e}")
                self.logger.info(f"原始数据: {result.get('data', {})}")
        
        self.logger.info("")


def check_server_available(host: str, port: int, timeout: int = 2) -> bool:
    """检查服务器是否可访问"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


async def call_mcp_tool(client: ClientSession, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """调用MCP工具"""
    try:
        result = await client.call_tool(tool_name, params)
        # 将MCP返回结果转换为标准格式
        if hasattr(result, 'content'):
            # 提取content中的文本
            content_text = ""
            if result.content:
                for item in result.content:
                    if hasattr(item, 'text'):
                        content_text += item.text
                    elif isinstance(item, str):
                        content_text += item
            
            # 尝试解析JSON
            try:
                parsed = json.loads(content_text) if content_text else {}
                return parsed
            except json.JSONDecodeError:
                # 如果不是JSON，返回原始文本
                return {
                    "success": True,
                    "message": "工具调用成功",
                    "data": {"raw_content": content_text}
                }
        else:
            return {
                "success": True,
                "message": "工具调用成功",
                "data": {"result": str(result)}
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"工具调用失败: {str(e)}",
            "data": {"error": str(e)}
        }


async def run_mcp_tests():
    """执行所有MCP测试步骤"""
    # 配置路径
    log_dir = r"C:\Users\28167\Desktop\mcp"
    doc_path = r"C:\Users\28167\Desktop\openEuler intelligence\糖尿病2.docx"
    
    # MCP服务器配置
    mcp_url = "http://127.0.0.1:12311/sse"
    mcp_headers = {}
    
    # 初始化日志
    logger = TestLogger(log_dir)
    logger.logger.info("开始MCP服务器自动测试")
    logger.logger.info(f"MCP服务器URL: {mcp_url}")
    logger.logger.info(f"日志文件: {logger.log_file}")
    logger.logger.info("")
    
    kb_name = "test"
    doc_name = "糖尿病2.docx"
    
    client: Optional[ClientSession] = None
    exit_stack = AsyncExitStack()
    
    try:
        # 检查服务器是否可访问
        logger.logger.info("检查MCP服务器是否可访问...")
        server_host = "127.0.0.1"
        server_port = 12311
        
        if not check_server_available(server_host, server_port):
            logger.logger.error("="*80)
            logger.logger.error("MCP服务器连接失败！")
            logger.logger.error("="*80)
            logger.logger.error(f"无法连接到 {server_host}:{server_port}")
            logger.logger.error("")
            logger.logger.error("可能的原因：")
            logger.logger.error("1. MCP服务器未启动")
            logger.logger.error("   请先启动MCP服务器：")
            logger.logger.error("   cd mcp_center/servers/rag/src")
            logger.logger.error("   python server.py")
            logger.logger.error("")
            logger.logger.error("2. 端口被占用或配置错误")
            logger.logger.error(f"   请检查服务器配置，确认端口为 {server_port}")
            logger.logger.error("")
            logger.logger.error("3. 防火墙阻止了连接")
            logger.logger.error("   请检查防火墙设置")
            logger.logger.error("="*80)
            logger.logger.error(f"测试失败，日志已保存到: {logger.log_file}")
            return
        
        logger.logger.info(f"服务器 {server_host}:{server_port} 可访问，开始连接...")
        
        # 连接MCP服务器
        logger.logger.info("正在连接MCP服务器...")
        try:
            client_transport = sse_client(url=mcp_url, headers=mcp_headers)
            read, write = await exit_stack.enter_async_context(client_transport)
            client = ClientSession(read, write)
            session = await exit_stack.enter_async_context(client)
            await session.initialize()
            logger.logger.info("MCP服务器连接成功！")
            
            # 列出可用工具
            tools = await client.list_tools()
            logger.logger.info(f"可用工具数量: {len(tools.tools)}")
            for tool in tools.tools:
                logger.logger.info(f"  - {tool.name}: {tool.description[:50] if tool.description else '无描述'}...")
            logger.logger.info("")
        except Exception as e:
            logger.logger.exception(f"MCP服务器连接失败: {e}")
            logger.logger.error("")
            logger.logger.error("连接失败的可能原因：")
            logger.logger.error("1. 服务器未正确启动或已崩溃")
            logger.logger.error("2. URL配置错误（当前URL: {})".format(mcp_url))
            logger.logger.error("3. 服务器不支持SSE传输")
            logger.logger.error("")
            logger.logger.error("请检查：")
            logger.logger.error("- 服务器日志是否有错误信息")
            logger.logger.error("- 服务器是否正在运行")
            logger.logger.error("- 端口和URL配置是否正确")
            logger.logger.error(f"测试失败，日志已保存到: {logger.log_file}")
            return
        
        # 步骤1: 创建test知识库（使用 Knowledge_base_manager action="add"）
        logger.logger.info("执行步骤1: 创建test知识库")
        try:
            result1 = await call_mcp_tool(
                client,
                "Knowledge_base_manager",
                {
                    "action": "add",
                    "kb_name": kb_name,
                    "chunk_size": 512
                }
            )
            if not isinstance(result1, dict):
                result1 = {"success": False, "message": f"返回结果格式错误: {type(result1)}", "data": {"raw_result": str(result1)}}
        except Exception as e:
            logger.logger.exception(f"步骤1执行异常: {e}")
            result1 = {"success": False, "message": f"执行异常: {str(e)}", "data": {"error": str(e)}}
        logger.log_step(1, "创建test知识库", result1.get('success', False), result1)
        
        # 步骤2: 列出所有知识库（使用 Knowledge_base_manager action="list"）
        logger.logger.info("执行步骤2: 列出所有知识库")
        try:
            result2 = await call_mcp_tool(
                client,
                "Knowledge_base_manager",
                {
                    "action": "list",
                    "keyword": None
                }
            )
            if not isinstance(result2, dict):
                result2 = {"success": False, "message": f"返回结果格式错误: {type(result2)}", "data": {"raw_result": str(result2)}}
        except Exception as e:
            logger.logger.exception(f"步骤2执行异常: {e}")
            result2 = {"success": False, "message": f"执行异常: {str(e)}", "data": {"error": str(e)}}
        logger.log_step(2, "列出所有知识库", result2.get('success', False), result2)
        
        # 步骤3: 检查test知识库是否存在
        logger.logger.info("执行步骤3: 检查test知识库是否存在")
        try:
            exists = False
            if result2.get("success") and result2.get("data", {}).get("knowledge_bases"):
                for kb in result2["data"]["knowledge_bases"]:
                    if kb.get("name") == kb_name:
                        exists = True
                        break
            result3 = {
                "success": exists,
                "message": "test知识库已存在" if exists else "test知识库不存在",
                "data": {"kb_name": kb_name}
            }
        except Exception as e:
            logger.logger.exception(f"步骤3执行异常: {e}")
            result3 = {"success": False, "message": f"执行异常: {str(e)}", "data": {"error": str(e)}}
        logger.log_step(3, "检查test知识库是否存在", result3.get('success', False), result3)
        
        # 步骤4: 导入文档（使用 document_manager action="add"）
        logger.logger.info("执行步骤4: 导入文档")
        try:
            if not os.path.exists(doc_path):
                logger.logger.error(f"文档不存在: {doc_path}")
                result4 = {
                    "success": False,
                    "message": f"文档不存在: {doc_path}",
                    "data": {}
                }
            else:
                result4 = await call_mcp_tool(
                    client,
                    "document_manager",
                    {
                        "action": "add",
                        "file_paths": [doc_path],
                        "kb_name": kb_name,
                        "chunk_size": 512
                    }
                )
                if not isinstance(result4, dict):
                    result4 = {"success": False, "message": f"返回结果格式错误: {type(result4)}", "data": {"raw_result": str(result4)}}
        except Exception as e:
            logger.logger.exception(f"步骤4执行异常: {e}")
            result4 = {"success": False, "message": f"执行异常: {str(e)}", "data": {"error": str(e)}}
        logger.log_step(4, f"导入文档 {doc_path}", result4.get('success', False), result4)
        
        # 步骤5: 获取文档解析结果（使用 document_manager action="getchunks"）
        logger.logger.info("执行步骤5: 获取文档解析结果")
        try:
            result5 = await call_mcp_tool(
                client,
                "document_manager",
                {
                    "action": "getchunks",
                    "doc_name": doc_name,
                    "kb_name": kb_name
                }
            )
            if not isinstance(result5, dict):
                result5 = {"success": False, "message": f"返回结果格式错误: {type(result5)}", "data": {"raw_result": str(result5)}}
        except Exception as e:
            logger.logger.exception(f"步骤5执行异常: {e}")
            result5 = {"success": False, "message": f"执行异常: {str(e)}", "data": {"error": str(e)}}
        logger.log_step(5, f"获取文档 {doc_name} 的解析结果", result5.get('success', False), result5)
        
        # 步骤6: 搜索"糖尿病怎么预防"
        logger.logger.info("执行步骤6: 搜索")
        query = "糖尿病怎么预防"
        try:
            result6 = await call_mcp_tool(
                client,
                "search",
                {
                    "query": query,
                    "kb_names": [kb_name],
                    "top_k": 5,
                    "banned_chunk_ids": []
                }
            )
            if not isinstance(result6, dict):
                result6 = {"success": False, "message": f"返回结果格式错误: {type(result6)}", "data": {"raw_result": str(result6)}}
        except Exception as e:
            logger.logger.exception(f"步骤6执行异常: {e}")
            result6 = {"success": False, "message": f"执行异常: {str(e)}", "data": {"error": str(e)}}
        logger.log_step(6, f"搜索 '{query}'", result6.get('success', False), result6)
        
        # 步骤7: GitHub线上检索"memory leak"
        logger.logger.info("执行步骤7: GitHub线上检索")
        query_github = "memory leak"
        try:
            result7 = await call_mcp_tool(
                client,
                "search",
                {
                    "query": query_github,
                    "kb_names": [kb_name],
                    "top_k": 5,
                    "online": True,
                    "online_top_k": 5
                }
            )
            if not isinstance(result7, dict):
                result7 = {"success": False, "message": f"返回结果格式错误: {type(result7)}", "data": {"raw_result": str(result7)}}
        except Exception as e:
            logger.logger.exception(f"步骤7执行异常: {e}")
            result7 = {"success": False, "message": f"执行异常: {str(e)}", "data": {"error": str(e)}}
        logger.log_step(7, f"GitHub线上检索 '{query_github}'", result7.get('success', False), result7)
        
        # 步骤8: 清理database目录下的所有文件
        logger.logger.info("执行步骤8: 清理database目录下的所有文件")
        cleanup_success = True
        cleanup_message = ""
        cleanup_data = {}
        
        try:
            # 获取database目录路径
            database_dir = os.path.join(current_dir, "src", "database")
            logger.logger.info(f"清理目录: {database_dir}")
            
            if os.path.exists(database_dir):
                # 列出所有文件
                all_files = []
                for root, dirs, files in os.walk(database_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        all_files.append(file_path)
                
                logger.logger.info(f"找到 {len(all_files)} 个文件需要清理")
                
                # 删除所有文件
                deleted_files = []
                failed_files = []
                for file_path in all_files:
                    try:
                        os.remove(file_path)
                        deleted_files.append(file_path)
                        logger.logger.info(f"已删除: {file_path}")
                    except Exception as e:
                        failed_files.append({"file": file_path, "error": str(e)})
                        logger.logger.error(f"删除失败 {file_path}: {e}")
                
                cleanup_message = f"成功删除 {len(deleted_files)} 个文件，失败 {len(failed_files)} 个"
                cleanup_data = {
                    "database_dir": database_dir,
                    "deleted_count": len(deleted_files),
                    "failed_count": len(failed_files),
                    "deleted_files": deleted_files,
                    "failed_files": failed_files
                }
                
                if failed_files:
                    cleanup_success = False
            else:
                cleanup_message = f"database目录不存在: {database_dir}"
                cleanup_data = {"database_dir": database_dir, "exists": False}
                
        except Exception as e:
            cleanup_success = False
            cleanup_message = f"清理过程发生异常: {str(e)}"
            cleanup_data = {"error": str(e)}
            logger.logger.exception(f"清理异常: {e}")
        
        result8 = {
            "success": cleanup_success,
            "message": cleanup_message,
            "data": cleanup_data
        }
        logger.log_step(8, "清理database目录下的所有文件", cleanup_success, result8)
        
        # 总结
        logger.logger.info("="*80)
        logger.logger.info("测试总结")
        logger.logger.info("="*80)
        steps = [
            ("创建test知识库 (Knowledge_base_manager action=add)", result1.get('success', False)),
            ("列出所有知识库 (Knowledge_base_manager action=list)", result2.get('success', False)),
            ("检查test知识库是否存在", result3.get('success', False)),
            ("导入文档 (document_manager action=add)", result4.get('success', False)),
            ("获取文档解析结果 (document_manager action=getchunks)", result5.get('success', False)),
            ("搜索 (search)", result6.get('success', False)),
            ("GitHub线上检索 (search online=true)", result7.get('success', False)),
            ("清理文件", result8.get('success', False)),
        ]
        
        success_count = sum(1 for _, success in steps if success)
        total_count = len(steps)
        
        for step_name, success in steps:
            status = "✓" if success else "✗"
            logger.logger.info(f"{status} {step_name}")
        
        logger.logger.info("")
        logger.logger.info(f"总计: {success_count}/{total_count} 步骤成功")
        logger.logger.info(f"测试完成，日志已保存到: {logger.log_file}")
        
        # 刷新所有日志handlers
        for handler in logging.getLogger().handlers:
            handler.flush()
        
    except Exception as e:
        logger.logger.exception(f"测试过程中发生异常: {e}")
        logger.logger.error(f"测试失败，日志已保存到: {logger.log_file}")
        
        # 刷新所有日志handlers
        for handler in logging.getLogger().handlers:
            handler.flush()
    
    finally:
        # 关闭MCP客户端连接
        try:
            await exit_stack.aclose()
            logger.logger.info("MCP客户端连接已关闭")
        except Exception as e:
            logger.logger.warning(f"关闭MCP客户端连接时出错: {e}")


if __name__ == "__main__":
    print("="*80)
    print("MCP服务器客户端测试工具")
    print("="*80)
    print("")
    print("使用前请确保：")
    print("1. MCP服务器已启动")
    print("   启动命令：")
    print("   cd mcp_center/servers/rag/src")
    print("   python server.py")
    print("")
    print("2. 服务器运行在 http://127.0.0.1:12311/sse")
    print("")
    print("="*80)
    print("")
    
    try:
        asyncio.run(run_mcp_tests())
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n测试启动失败: {e}")
        import traceback
        traceback.print_exc()

