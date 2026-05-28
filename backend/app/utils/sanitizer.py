"""backend/app/utils/sanitizer.py — HTML 内容净化

使用 bleach 过滤危险标签和属性，防止 XSS 攻击。
"""
from __future__ import annotations

import bleach

# 允许的 HTML 标签
ALLOWED_TAGS = [
    "a", "abbr", "acronym", "b", "blockquote", "br", "code",
    "div", "em", "h1", "h2", "h3", "h4", "h5", "h6", "hr",
    "i", "img", "li", "ol", "p", "pre", "span", "strong",
    "table", "tbody", "td", "th", "thead", "tr", "u", "ul",
]

# 允许的属性
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "width", "height"],
    "td": ["colspan", "rowspan"],
    "th": ["colspan", "rowspan"],
    "*": ["style", "class"],
}

# 允许的协议
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def sanitize_html(html: str) -> str:
    """净化 HTML 内容，移除危险标签和属性"""
    if not html:
        return ""
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
