import asyncio
import json
import os
import sys
from typing import Any, Dict  # noqa: UP035

from tool import (
    create_knowledge_base,
    delete_document,
    delete_knowledge_base,
    get_document_chunks,
    import_document,
    list_documents,
    list_knowledge_bases,
    search,
)

# 添加路径
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 添加 mcp_center 目录到路径
mcp_center_dir = os.path.abspath(os.path.join(current_dir, '../../..'))
if mcp_center_dir not in sys.path:
    sys.path.insert(0, mcp_center_dir)




def print_result(result: Dict[str, Any]):
    """打印结果"""
    if result.get("success"):
        print(f"✅ {result.get('message', '操作成功')}")
        if result.get("data"):
            print(json.dumps(result["data"], ensure_ascii=False, indent=2))
    else:
        print(f"❌ {result.get('message', '操作失败')}")

def handle_create_kb(args):
    """创建知识库"""
    if not args.kb_name or not args.chunk_size:
        print("❌ 缺少参数：--kb_name 和 --chunk_size 必填")
        return False
    result = create_knowledge_base(
        kb_name=args.kb_name,
        chunk_size=args.chunk_size,
        embedding_model=args.embedding_model,
        embedding_endpoint=args.embedding_endpoint,
        embedding_api_key=args.embedding_api_key
    )
    print_result(result)
    return result.get("success", False)

def handle_delete_kb(args):
    """删除知识库"""
    if not args.kb_names:
        print("❌ 缺少参数：--kb_names 必填（知识库名称列表）")
        return False
    
    result = delete_knowledge_base(args.kb_names)
    print_result(result)
    return result.get("success", False)

def handle_list_kb(args):
    """列出知识库"""
    result = list_knowledge_bases(keyword=args.keyword)
    print_result(result)
    return result.get("success", False)

async def handle_import_doc_async(args):
    """导入文档（异步）"""
    if not args.file_paths:
        print("❌ 缺少参数：--file_paths 必填（文件路径列表）")
        return False
    if not args.kb_name:
        print("❌ 缺少参数：--kb_name 必填（知识库名称）")
        return False
    
    result = await import_document(
        file_paths=args.file_paths,
        kb_name=args.kb_name,
        chunk_size=args.chunk_size
    )
    print_result(result)
    return result.get("success", False)

def handle_import_doc(args):
    """导入文档（同步包装）"""
    return asyncio.run(handle_import_doc_async(args))

def handle_list_doc(args):
    """列出文档"""
    if not args.kb_names:
        print("❌ 缺少参数：--kb_names 必填（知识库名称列表）")
        return False
    
    result = list_documents(args.kb_names, keyword=args.keyword)
    print_result(result)
    return result.get("success", False)

def handle_delete_doc(args):
    """删除文档"""
    if not args.doc_names:
        print("❌ 缺少参数：--doc_names 必填（文档名称列表）")
        return False
    if not args.kb_name:
        print("❌ 缺少参数：--kb_name 必填（知识库名称）")
        return False
    
    result = delete_document(args.doc_names, args.kb_name)
    print_result(result)
    return result.get("success", False)

def handle_get_doc_chunks(args):
    """获取文档解析结果"""
    if not args.doc_name:
        print("❌ 缺少参数：--doc_name 必填")
        return False
    if not args.kb_name:
        print("❌ 缺少参数：--kb_name 必填（知识库名称）")
        return False
    
    result = get_document_chunks(args.doc_name, args.kb_name)
    print_result(result)
    return result.get("success", False)

async def handle_search_async(args):
    """搜索（异步）"""
    if not args.query:
        print("❌ 缺少参数：--query 必填")
        return False
    if not args.kb_names:
        print("❌ 缺少参数：--kb_names 必填（知识库名称列表）")
        return False
    
    result = await search(
        query=args.query,
        kb_names=args.kb_names,
        top_k=args.top_k,
        keyword_weight=args.keyword_weight,
        banned_chunk_ids=args.banned_chunk_ids,
        online=args.online,
        online_top_k=args.online_top_k
    )
    print_result(result)
    return result.get("success", False)

def handle_search(args):
    """搜索（同步包装）"""
    return asyncio.run(handle_search_async(args))


