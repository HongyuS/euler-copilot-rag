import argparse


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="rag-server 命令行工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 创建知识库
    create_kb_parser = subparsers.add_parser("create_kb", help="创建知识库")
    create_kb_parser.add_argument("--kb_name", required=True, help="知识库名称")
    create_kb_parser.add_argument("--chunk_size", type=int, required=True, help="chunk大小（token数）")
    create_kb_parser.add_argument("--embedding_model", help="向量化模型名称")
    create_kb_parser.add_argument("--embedding_endpoint", help="向量化服务端点URL")
    create_kb_parser.add_argument("--embedding_api_key", help="向量化服务API Key")

    # 删除知识库
    delete_kb_parser = subparsers.add_parser("delete_kb", help="删除知识库")
    delete_kb_parser.add_argument("--kb_names", nargs="+", required=True, help="知识库名称列表")

    # 列出知识库
    list_kb_parser = subparsers.add_parser("list_kb", help="列出所有知识库")
    list_kb_parser.add_argument("--keyword", help="关键词（可选），用于模糊查询知识库名称")

    # 导入文档
    import_doc_parser = subparsers.add_parser("import_doc", help="导入文档")
    import_doc_parser.add_argument("--file_paths", nargs="+", required=True, help="文件路径列表（绝对路径）")
    import_doc_parser.add_argument("--kb_name", required=True, help="知识库名称")
    import_doc_parser.add_argument("--chunk_size", type=int, help="chunk大小（可选，默认使用知识库的chunk_size）")

    # 列出文档
    list_doc_parser = subparsers.add_parser("list_doc", help="列出文档")
    list_doc_parser.add_argument("--kb_names", nargs="+", required=True, help="知识库名称列表")
    list_doc_parser.add_argument("--keyword", help="关键词（可选），用于模糊查询文档名称")

    # 删除文档
    delete_doc_parser = subparsers.add_parser("delete_doc", help="删除文档")
    delete_doc_parser.add_argument("--doc_names", nargs="+", required=True, help="文档名称列表")
    delete_doc_parser.add_argument("--kb_name", required=True, help="知识库名称")

    # 获取文档解析结果
    get_doc_chunks_parser = subparsers.add_parser("get_doc_chunks", help="获取文档解析结果")
    get_doc_chunks_parser.add_argument("--doc_name", required=True, help="文档名称")
    get_doc_chunks_parser.add_argument("--kb_name", required=True, help="知识库名称")

    # 搜索
    search_parser = subparsers.add_parser("search", help="搜索文档")
    search_parser.add_argument("--query", required=True, help="查询文本")
    search_parser.add_argument("--kb_names", nargs="+", required=True, help="知识库名称列表")
    search_parser.add_argument("--top_k", type=int, help="返回数量（可选，默认5）")
    search_parser.add_argument("--keyword_weight", type=float, help="关键词搜索权重（可选，默认0.3，范围0-1）")
    search_parser.add_argument("--banned_chunk_ids", nargs="*", default=None, help="被禁用的chunk ID列表（可选），用于过滤掉不想要的chunk")
    search_parser.add_argument(
        "--online",
        action="store_true",
        help="是否启用GitHub线上检索（可选，默认False）"
    )
    search_parser.add_argument(
        "--online_top_k",
        type=int,
        help="GitHub检索的返回数量（可选，默认按配置，一般为2）"
    )

    return parser.parse_args()

