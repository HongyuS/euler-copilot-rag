"""经验管理 & 文档解析 CLI 工具。"""

import argparse

from experience_skill_cli.console import (
    blank,
    deleted,
    print_experience,
    print_experience_list,
    search_result,
    success,
)
from experience_skill_cli.schema.enum import ExperienceType
from experience_skill_cli.service.experience_service import ExperienceService
from experience_skill_cli.sqlite import AsyncSQLiteSingleton
from experience_skill_cli.web_server import start_web_server


def add_experiences_cli(args: argparse.Namespace) -> None:
    """添加经验：支持 SKILL / WIKI"""
    experience_type = ExperienceType[args.type.upper()]
    ExperienceService.add_experiences(experience_type, args.source)
    success(f"成功添加 {args.type} 经验，来源：{args.source}")


def list_experiences_cli(args: argparse.Namespace) -> None:
    """列出经验"""
    experience_type = ExperienceType[args.type.upper()] if args.type else None
    total, exps = ExperienceService.list_experiences(
        experience_type=experience_type,
        name=args.name,
        is_hot=args.is_hot,
        page=args.page,
        page_size=args.page_size,
    )
    print_experience_list(exps, total)


def delete_experience_ids_cli(args: argparse.Namespace) -> None:
    """按 ID 删除经验"""
    ExperienceService.delete_experience_by_ids(args.ids)
    deleted(f"已删除经验 ID：{args.ids}")


def delete_experience_source_cli(args: argparse.Namespace) -> None:
    """按来源路径删除经验"""
    ExperienceService.delete_experience_by_source(args.source)
    deleted(f"已删除来源为 {args.source} 的经验")


def search_experiences_cli(args: argparse.Namespace) -> None:
    """搜索经验"""
    experience_type = ExperienceType[args.type.upper()]
    exps = ExperienceService.search_experiences(
        query=args.query,
        exp_type=experience_type,
        top_k=args.top_k,
        fields=args.fields if args.fields is not None else None,
        is_hot=args.is_hot,
        banned_experience_ids=args.banned_ids if args.banned_ids is not None else None,
        experience_ids=(args.experience_ids if args.experience_ids is not None else None),
    )
    search_result(f"搜索「{args.query}」找到 {len(exps)} 条结果")
    blank()

    for idx, exp in enumerate(exps, 1):
        if idx > 1:
            blank()
        print_experience(exp, idx)


def delete_all_experiences_cli(_args: argparse.Namespace) -> None:
    """删除所有经验"""
    sqlite_manager = AsyncSQLiteSingleton()
    sqlite_manager.clear_database()
    sqlite_manager.init()
    deleted("已删除所有经验数据")


def init_db() -> None:
    """初始化数据库"""
    sqlite_manager = AsyncSQLiteSingleton()
    sqlite_manager.init()


def web_cli(args: argparse.Namespace) -> None:
    """启动 Web 管理界面"""
    start_web_server(
        host=args.host,
        port=args.port,
        open_browser=not args.no_browser,
    )


def main() -> None:
    """解析命令行参数并分发到对应子命令。"""
    init_db()
    parser = argparse.ArgumentParser(description="经验管理 & 文档解析 CLI 工具")
    subparsers = parser.add_subparsers(dest="command", required=True, help="子命令")

    # add-experiences
    add_parser = subparsers.add_parser("add-experiences", help="添加经验")
    add_parser.add_argument(
        "--type",
        required=True,
        choices=["SKILL", "WIKI"],
        help="经验类型",
    )
    add_parser.add_argument("--source", required=True, help="文件/目录路径")
    add_parser.set_defaults(func=add_experiences_cli)

    # list-experiences
    list_parser = subparsers.add_parser("list-experiences", help="列出经验")
    list_parser.add_argument("--type", choices=["SKILL", "WIKI"], help="类型过滤")
    list_parser.add_argument("--name", default=None, help="名称模糊匹配")
    list_parser.add_argument(
        "--is-hot",
        type=lambda x: str(x).lower() == "true",
        default=None,
        help="是否热门",
    )
    list_parser.add_argument("--page", type=int, default=1, help="页码")
    list_parser.add_argument("--page-size", type=int, default=10, help="每页数量")
    list_parser.set_defaults(func=list_experiences_cli)

    # delete-by-ids
    del_ids_parser = subparsers.add_parser("delete-by-ids", help="按ID删除经验")
    del_ids_parser.add_argument(
        "--ids",
        nargs="+",
        required=True,
        help="经验ID列表，空格分隔",
    )
    del_ids_parser.set_defaults(func=delete_experience_ids_cli)

    # delete-by-source
    del_source_parser = subparsers.add_parser(
        "delete-by-source",
        help="按来源路径删除经验",
    )
    del_source_parser.add_argument("--source", required=True, help="来源路径")
    del_source_parser.set_defaults(func=delete_experience_source_cli)

    # search-experiences
    search_parser = subparsers.add_parser("search-experiences", help="搜索经验")
    search_parser.add_argument("--query", required=True, help="搜索关键词")
    search_parser.add_argument(
        "--type",
        required=True,
        choices=["SKILL", "WIKI"],
        help="经验类型",
    )
    search_parser.add_argument(
        "--fields",
        nargs="+",
        help="搜索字段列表，空格分隔，默认为全部字段",
    )
    search_parser.add_argument(
        "--is-hot",
        type=lambda x: str(x).lower() == "true",
        default=None,
        help="是否热门",
    )
    search_parser.add_argument(
        "--banned-ids",
        nargs="+",
        help="被禁用的经验ID列表，空格分隔，默认为空",
    )
    search_parser.add_argument(
        "--experience-ids",
        nargs="+",
        help="仅搜索指定经验ID列表，空格分隔，默认为全部",
    )
    search_parser.add_argument("--top-k", type=int, default=5, help="返回条数")
    search_parser.set_defaults(func=search_experiences_cli)

    # delete-all
    del_all_parser = subparsers.add_parser("delete-all", help="删除所有经验")
    del_all_parser.set_defaults(func=delete_all_experiences_cli)

    # web
    web_parser = subparsers.add_parser("web", help="启动 Web 管理界面")
    web_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="监听地址，默认 127.0.0.1",
    )
    web_parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="监听端口，默认 8080",
    )
    web_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="不自动打开浏览器",
    )
    web_parser.set_defaults(func=web_cli)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
