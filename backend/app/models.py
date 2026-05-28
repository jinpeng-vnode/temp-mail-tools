"""backend/app/models.py — Pydantic 数据模型定义

定义邮箱、邮件、WebSocket消息等数据结构。
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Mailbox(BaseModel):
    """临时邮箱"""
    address: str
    token: str
    created_at: datetime = Field(alias="createdAt")
    expires_at: datetime = Field(alias="expiresAt")

    model_config = {"populate_by_name": True}


class MailboxCreateRequest(BaseModel):
    """创建邮箱请求"""
    domain: str | None = None


class MailboxCreateResponse(BaseModel):
    """创建邮箱响应"""
    address: str
    token: str
    expires_at: datetime = Field(alias="expiresAt")

    model_config = {"populate_by_name": True}


class EmailAttachment(BaseModel):
    """邮件附件"""
    filename: str
    content_type: str = Field(alias="contentType")
    size: int
    download_url: str = Field(alias="downloadUrl")

    model_config = {"populate_by_name": True}


class EmailSummary(BaseModel):
    """邮件摘要（列表用）"""
    id: str
    from_addr: str = Field(alias="fromAddr")
    subject: str
    received_at: datetime = Field(alias="receivedAt")
    has_attachments: bool = Field(alias="hasAttachments")
    preview: str

    model_config = {"populate_by_name": True}


class EmailDetail(BaseModel):
    """邮件详情"""
    id: str
    from_addr: str = Field(alias="fromAddr")
    to_addr: str = Field(alias="toAddr")
    subject: str
    text_body: str | None = Field(None, alias="textBody")
    html_body: str | None = Field(None, alias="htmlBody")
    received_at: datetime = Field(alias="receivedAt")
    attachments: list[EmailAttachment] = []

    model_config = {"populate_by_name": True}


class EmailListResponse(BaseModel):
    """邮件列表响应"""
    items: list[EmailSummary]
    total: int


class WebSocketMessage(BaseModel):
    """WebSocket 推送消息"""
    type: str
    data: EmailSummary | None = None

    model_config = {"populate_by_name": True}


class ErrorResponse(BaseModel):
    """错误响应"""
    error: ErrorDetail


class ErrorDetail(BaseModel):
    """错误详情"""
    code: str
    message: str
