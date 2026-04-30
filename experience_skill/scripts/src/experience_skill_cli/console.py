"""CLI 控制台输出工具 —— 统一所有 print 调用，提供语义化、美观的输出。"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from experience_skill_cli.schema.exprience import Experience

# ---------------------------------------------------------------------------
# 内部基础函数
# ---------------------------------------------------------------------------


def echo(*args: Any, **kwargs: Any) -> None:
    """通用输出，等价于 print。"""
    print(*args, **kwargs)  # noqa: T201


# ---------------------------------------------------------------------------
# 语义化输出
# ---------------------------------------------------------------------------


def success(msg: str) -> None:
    """✅ 成功消息。"""
    echo(f"✅ {msg}")


def info(msg: str) -> None:
    """📋 信息消息。"""
    echo(f"📋 {msg}")


def warn(msg: str) -> None:
    """⚠️  警告消息（输出到 stderr）。"""
    echo(f"⚠️  {msg}", file=sys.stderr)


def error(msg: str) -> None:
    """❌ 错误消息（输出到 stderr）。"""
    echo(f"❌ {msg}", file=sys.stderr)


def deleted(msg: str) -> None:
    """🗑️  删除确认消息。"""
    echo(f"🗑️  {msg}")


def search_result(msg: str) -> None:
    """🔍 搜索结果标题。"""
    echo(f"🔍 {msg}")


def launch(msg: str) -> None:
    """🌐 浏览器启动消息。"""
    echo(f"🌐 {msg}")


def link(msg: str) -> None:
    """🔗 链接提示消息。"""
    echo(f"🔗 {msg}")


def rocket(msg: str) -> None:
    """🚀 服务启动横幅。"""
    echo(f"🚀 {msg}")


def blank() -> None:
    """输出一个空行。"""
    echo()


def section(title: str) -> None:
    """输出章节标题。"""
    echo(f"===== {title} =====")


# ---------------------------------------------------------------------------
# 经验打印
# ---------------------------------------------------------------------------

_EXPERIENCE_FIELDS = [
    ("ID", "id"),
    ("类型", "type"),
    ("名称", "name"),
    ("状态", "status"),
    ("描述", "description"),
    ("关键词", "keywords"),
    ("来源", "source"),
    ("是否热门", "is_hot"),
    ("创建时间", "created_at"),
    ("更新时间", "updated_at"),
]


def print_experience(exp: Experience, index: int | None = None) -> None:
    """格式化打印一条经验的所有字段。"""
    if index is not None:
        section(f"第 {index} 条经验")
    else:
        section("经验详情")
    for label, attr in _EXPERIENCE_FIELDS:
        echo(f"{label:<12}: {getattr(exp, attr, '')}")


def print_experience_list(exps: list[Experience], total: int | None = None) -> None:
    """批量打印经验列表。"""
    if total is not None:
        info(f"总计：{total} 条")
    elif exps:
        info(f"共 {len(exps)} 条")
    for idx, exp in enumerate(exps, 1):
        if idx > 1:
            blank()
        print_experience(exp, idx)
