"""backend/app/routers/mailbox.py — 邮箱生成/查询/删除 API

提供临时邮箱的创建、状态查询和删除接口。
"""
from __future__ import annotations

import random
import secrets
import string

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models import MailboxCreateRequest, MailboxCreateResponse, Mailbox
from app.storage import create_mailbox, get_mailbox, delete_mailbox

router = APIRouter(prefix="/api/mailbox", tags=["mailbox"])


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
async def generate_mailbox(body: MailboxCreateRequest | None = None):
    """生成临时邮箱"""
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
        raise HTTPException(status_code=404, detail={
            "code": "MAILBOX_NOT_FOUND",
            "message": "邮箱不存在或已过期",
        })
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
        raise HTTPException(status_code=404, detail={
            "code": "MAILBOX_NOT_FOUND",
            "message": "邮箱不存在或已过期",
        })
    return {"ok": True}
