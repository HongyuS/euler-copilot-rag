"""经验管理 Web 服务"""

import os
import re
import webbrowser
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse

from manager.keyword_manager import KeyWordManager
from schema.enum import ExperienceType
from service.experience_service import ExperienceService

TEMPLATES_DIR = Path(__file__).parent / "templates"

# Skill 安装根目录（SKILL.md 所在目录 = scripts/ 的父目录）
SKILL_ROOT = Path(__file__).parent.parent

app = FastAPI(title="经验管理", docs_url=None, redoc_url=None)


# ------------------------------
# 静态页面
# ------------------------------
@app.get("/", response_class=HTMLResponse)
async def index():
    index_path = TEMPLATES_DIR / "index.html"
    if index_path.exists():
        return index_path.read_text(encoding="utf-8")
    return HTMLResponse("<h1>index.html not found</h1>", status_code=404)


# ------------------------------
# API：获取所有关键词
# ------------------------------
@app.get("/api/keywords")
async def list_keywords(
    type: str | None = Query(None, description="类型过滤：SKILL / WIKI"),
):
    experience_type = ExperienceType[type.upper()] if type else None
    keywords = KeyWordManager.get_all_keywords(experience_type)
    return JSONResponse({"keywords": keywords})


# ------------------------------
# API：列出经验
# ------------------------------
@app.get("/api/experiences")
async def list_experiences(
    type: str | None = Query(None, description="类型过滤：SKILL / WIKI"),
    name: str | None = Query(None, description="名称模糊匹配"),
    is_hot: bool | None = Query(None, description="是否热门"),
    kw: list[str] = Query(None, description="关键词过滤（多选）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    experience_type = ExperienceType[type.upper()] if type else None

    # 关键词过滤：先查出命中的经验 ID，再传给列表查询
    keyword_ids = KeyWordManager.get_experience_ids_by_keywords(kw) if kw else None

    from manager.experience_manager import ExperienceManager

    total, exps = ExperienceManager.list_experiences(
        experience_type=experience_type,
        keywords=None,
        name=name,
        is_hot=is_hot,
        page=page,
        page_size=page_size,
        experience_ids=keyword_ids,
    )
    # 补回 keywords 字段
    for exp in exps:
        exp.keywords = KeyWordManager.get_keywords_by_experience_id(exp.id)
    return JSONResponse(
        {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [_exp_to_dict(e) for e in exps],
        }
    )


# ------------------------------
# API：热门 Top 20
# ------------------------------
@app.get("/api/experiences/hot")
async def list_hot_experiences(
    type: str | None = Query(None, description="类型过滤：SKILL / WIKI"),
):
    experience_type = ExperienceType[type.upper()] if type else None
    total, exps = ExperienceService.list_experiences(
        experience_type=experience_type,
        name=None,
        is_hot=True,
        page=1,
        page_size=20,
    )
    return JSONResponse(
        {
            "total": total,
            "items": [_exp_to_dict(e) for e in exps],
        }
    )


# ------------------------------
# API：搜索经验（FTS）
# ------------------------------
@app.get("/api/experiences/search")
async def search_experiences(
    query: str = Query(..., min_length=1, description="搜索关键词"),
    type: str = Query(..., description="类型：SKILL / WIKI"),
    top_k: int = Query(20, ge=1, le=100, description="返回条数"),
    is_hot: bool | None = Query(None, description="是否热门"),
):
    experience_type = ExperienceType[type.upper()]
    exps = ExperienceService.search_experiences(
        query=query,
        exp_type=experience_type,
        top_k=top_k,
        is_hot=is_hot,
    )
    return JSONResponse(
        {
            "items": [_exp_to_dict(e) for e in exps],
        }
    )


# ------------------------------
# API：获取单条经验详情（含文件内容）
# ------------------------------


def _strip_yaml_header(md_content: str) -> str:
    """去除 Markdown 文件开头的 YAML front matter（--- ... ---）。"""
    return re.sub(
        r"^---\s*\n.*?\n---\s*\n", "", md_content, count=1, flags=re.DOTALL
    ).lstrip("\n")


@app.get("/api/experiences/{experience_id}")
async def get_experience(experience_id: str):
    from manager.experience_manager import ExperienceManager

    exps = ExperienceManager.query_experience_by_ids([experience_id])
    if not exps:
        return JSONResponse({"error": "Experience not found"}, status_code=404)

    exp = exps[0]
    exp.keywords = KeyWordManager.get_keywords_by_experience_id(exp.id)

    # 读取源文件内容（skill_hub / wiki_hub 均位于 SKILL_ROOT 下）
    content = ""
    try:
        if exp.type == ExperienceType.SKILL:
            skill_md = SKILL_ROOT / exp.source / "SKILL.md"
            if skill_md.exists():
                content = skill_md.read_text(encoding="utf-8")
        elif exp.type == ExperienceType.WIKI:
            wiki_md = SKILL_ROOT / exp.source
            if wiki_md.exists():
                content = wiki_md.read_text(encoding="utf-8")
    except Exception:
        content = "无法读取文件内容"

    # 剥离 YAML header，正文区域不展示冗余元信息
    content = _strip_yaml_header(content)

    result = _exp_to_dict(exp)
    result["content"] = content
    return JSONResponse(result)


# ------------------------------
# 辅助函数
# ------------------------------
def _exp_to_dict(exp) -> dict:
    return {
        "id": exp.id,
        "type": exp.type.value,
        "name": exp.name,
        "description": exp.description,
        "keywords": exp.keywords,
        "source": exp.source,
        "is_hot": exp.is_hot,
        "status": exp.status.value,
        "created_at": exp.created_at,
        "updated_at": exp.updated_at,
    }


def start_web_server(
    host: str = "127.0.0.1", port: int = 8080, open_browser: bool = True
):
    """启动 Web 服务并可选自动打开浏览器"""
    import uvicorn

    url = f"http://{host}:{port}"

    # 判断是否有图形环境
    has_display = os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
    is_macos = os.uname().sysname == "Darwin"

    if open_browser and (has_display or is_macos):
        try:
            webbrowser.open(url)
            print(f"🌐 浏览器已打开: {url}")
        except Exception:
            print(f"⚠️  无法自动打开浏览器，请手动访问: {url}")
    else:
        print(f"🔗 请访问: {url}")

    print(f"🚀 Web 服务启动于 {host}:{port}，按 Ctrl+C 停止")
    uvicorn.run(app, host=host, port=port, log_level="warning")
