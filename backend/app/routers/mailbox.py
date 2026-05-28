"""backend/app/routers/mailbox.py — 邮箱生成/查询/删除 API

提供临时邮箱的创建、状态查询和删除接口。
"""
from __future__ import annotations

import random
import secrets
import string
import time

from fastapi import APIRouter, Request

from app.config import settings
from app.exceptions import AppError
from app.models import MailboxCreateRequest, MailboxCreateResponse, Mailbox
from app.storage import create_mailbox, get_mailbox, delete_mailbox, get_redis

router = APIRouter(prefix="/api/mailbox", tags=["mailbox"])

# 限流配置：10次/分钟/IP
_RATE_LIMIT = 10
_RATE_WINDOW = 60


def _generate_address(domain: str | None = None) -> tuple[str, str]:
    """生成随机邮箱地址和token"""
    # 随机用户名：8位字母数字
    username = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    # 选择域名
    if not domain or domain not in settings.domains_list:
        domain = random.choice(settings.domains_list)
    address = f"{username}@{domain}"
    token = secrets.token_urlsafe(16)
    return address, token


@router.post("", response_model=MailboxCreateResponse)
async def generate_mailbox(request: Request, body: MailboxCreateRequest | None = None):
    """生成临时邮箱"""
    # Rate Limiting: 10次/分钟/IP
    client_ip = request.client.host if request.client else "unknown"
    r = await get_redis()
    rate_key = f"rate:{client_ip}"
    now = time.time()
    pipe = r.pipeline()
    pipe.zremrangebyscore(rate_key, 0, now - _RATE_WINDOW)
    pipe.zcard(rate_key)
    pipe.zadd(rate_key, {str(now): now})
    pipe.expire(rate_key, _RATE_WINDOW)
    results = await pipe.execute()
    if results[1] >= _RATE_LIMIT:
        raise AppError(429, "RATE_LIMITED", "请求过于频繁，请稍后再试")

    domain = body.domain if body else None
    address, token = _generate_address(domain)
    ttl = settings.mail_expire_minutes * 60

    data = await create_mailbox(address, token, ttl)
    return MailboxCreateResponse(
        address=data["address"],
        token=data["token"],
        expires_at=data["expires_at"],
    )


@router.get("/{token}", response_model=Mailbox)
async def get_mailbox_status(token: str):
    """查询邮箱状态"""
    data = await get_mailbox(token)
    if not data:
        raise AppError(404, "MAILBOX_NOT_FOUND", "邮箱不存在或已过期")
    return Mailbox(
        address=data["address"],
        token=data["token"],
        created_at=data["created_at"],
        expires_at=data["expires_at"],
    )


@router.delete("/{token}")
async def remove_mailbox(token: str):
    """删除邮箱及所有邮件"""
    success = await delete_mailbox(token)
    if not success:
        raise AppError(404, "MAILBOX_NOT_FOUND", "邮箱不存在或已过期")
    return {"ok": True}
