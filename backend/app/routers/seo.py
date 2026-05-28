"""backend/app/routers/seo.py — SEO 相关 API

提供 sitemap.xml 动态生成和落地页数据接口。
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import Response

from app.config import settings
from app.exceptions import AppError

router = APIRouter(tags=["seo"])

# 落地页数据文件路径
_DATA_DIR = Path(__file__).resolve().parent.parent / "seo" / "data"


def _load_use_cases() -> list[dict]:
    """加载用途分类数据"""
    path = _DATA_DIR / "use_cases.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@router.get("/api/sitemap.xml")
async def sitemap():
    """动态生成 sitemap.xml"""
    base_url = f"https://{settings.domains_list[0]}"
    use_cases = _load_use_cases()

    urls = [f"  <url><loc>{base_url}/</loc></url>"]
    for uc in use_cases:
        urls.append(f"  <url><loc>{base_url}/temp-email-for-{uc['slug']}</loc></url>")

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>"
    )
    return Response(content=xml, media_type="application/xml")


@router.get("/api/seo/landing/{slug}")
async def get_landing_data(slug: str):
    """获取落地页数据"""
    use_cases = _load_use_cases()
    for uc in use_cases:
        if uc["slug"] == slug:
            return uc
    raise AppError(404, "LANDING_NOT_FOUND", "落地页不存在")
