"""backend/app/utils/email_parser.py — MIME 邮件解析

解析原始邮件数据，提取发件人、主题、正文和附件。
"""
from __future__ import annotations

import email
from datetime import datetime, timezone
from email import policy
from email.message import EmailMessage


def parse_email(raw_data: bytes) -> dict:
    """解析原始 MIME 邮件数据

    返回:
        {
            "from_addr": str,
            "subject": str,
            "text_body": str | None,
            "html_body": str | None,
            "received_at": str (ISO 8601),
            "attachments": [{"filename": str, "content_type": str, "size": int, "content": bytes}]
        }
    """
    msg: EmailMessage = email.message_from_bytes(raw_data, policy=policy.default)

    from_addr = msg.get("From", "unknown@unknown")
    subject = msg.get("Subject", "(无主题)")

    text_body = None
    html_body = None
    attachments = []

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))

            # 附件
            if "attachment" in disposition:
                content = part.get_payload(decode=True) or b""
                attachments.append({
                    "filename": part.get_filename() or "unnamed",
                    "content_type": content_type,
                    "size": len(content),
                    "content": content,
                })
            # 正文
            elif content_type == "text/plain" and text_body is None:
                text_body = part.get_payload(decode=True).decode("utf-8", errors="replace")
            elif content_type == "text/html" and html_body is None:
                html_body = part.get_payload(decode=True).decode("utf-8", errors="replace")
    else:
        content_type = msg.get_content_type()
        payload = msg.get_payload(decode=True)
        if payload:
            decoded = payload.decode("utf-8", errors="replace")
            if content_type == "text/html":
                html_body = decoded
            else:
                text_body = decoded

    return {
        "from_addr": from_addr,
        "subject": subject,
        "text_body": text_body,
        "html_body": html_body,
        "received_at": datetime.now(timezone.utc).isoformat(),
        "attachments": attachments,
    }
