"""backend/app/routers/emails.py — 邮件列表/详情/附件 API

提供邮件的分页查询、详情获取和附件下载接口。
"""
from __future__ import annotations

import json

from fastapi import APIRouter
from fastapi.responses import Response

from app.exceptions import AppError
from app.models import EmailListResponse, EmailSummary, EmailDetail, EmailAttachment
from app.storage import get_mailbox, get_emails, get_email, get_attachment
from app.utils.sanitizer import sanitize_html

router = APIRouter(prefix="/api/mailbox/{token}/emails", tags=["emails"])


@router.get("", response_model=EmailListResponse)
async def list_emails(token: str, page: int = 1, size: int = 20):
    """获取邮件列表（分页）"""
    mailbox = await get_mailbox(token)
    if not mailbox:
        raise AppError(404, "MAILBOX_NOT_FOUND", "邮箱不存在或已过期")

    emails_data, total = await get_emails(token, page, size)
    items = []
    for e in emails_data:
        attachments = json.loads(e.get("attachments_json", "[]"))
        preview = (e.get("text_body") or "")[:100]
        items.append(EmailSummary(
            id=e["id"],
            from_addr=e["from_addr"],
            subject=e["subject"],
            received_at=e["received_at"],
            has_attachments=len(attachments) > 0,
            preview=preview,
        ))

    return EmailListResponse(items=items, total=total)


@router.get("/{email_id}", response_model=EmailDetail)
async def get_email_detail(token: str, email_id: str):
    """获取邮件详情"""
    mailbox = await get_mailbox(token)
    if not mailbox:
        raise AppError(404, "MAILBOX_NOT_FOUND", "邮箱不存在或已过期")

    data = await get_email(email_id)
    if not data:
        raise AppError(404, "EMAIL_NOT_FOUND", "邮件不存在")

    # 净化 HTML 内容
    html_body = sanitize_html(data.get("html_body") or "") or None

    # 构建附件列表
    att_meta = json.loads(data.get("attachments_json", "[]"))
    attachments = [
        EmailAttachment(
            filename=a["filename"],
            content_type=a["content_type"],
            size=a["size"],
            download_url=f"/api/mailbox/{token}/emails/{email_id}/attachments/{a['filename']}",
        )
        for a in att_meta
    ]

    return EmailDetail(
        id=data["id"],
        from_addr=data["from_addr"],
        to_addr=data["to_addr"],
        subject=data["subject"],
        text_body=data.get("text_body") or None,
        html_body=html_body,
        received_at=data["received_at"],
        attachments=attachments,
    )


@router.get("/{email_id}/attachments/{filename}")
async def download_attachment(token: str, email_id: str, filename: str):
    """下载附件"""
    mailbox = await get_mailbox(token)
    if not mailbox:
        raise AppError(404, "MAILBOX_NOT_FOUND", "邮箱不存在或已过期")

    content = await get_attachment(email_id, filename)
    if not content:
        raise AppError(404, "ATTACHMENT_NOT_FOUND", "附件不存在")

    # 从邮件元数据获取 content_type
    data = await get_email(email_id)
    content_type = "application/octet-stream"
    if data:
        att_meta = json.loads(data.get("attachments_json", "[]"))
        for a in att_meta:
            if a["filename"] == filename:
                content_type = a["content_type"]
                break

    return Response(
        content=content,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
