"""backend/app/smtp_server.py — aiosmtpd SMTP 接收服务

Catch-all 模式接收所有域名邮件，解析后存储到 Redis 并通过 WebSocket 推送。
"""
from __future__ import annotations

import asyncio

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import Envelope, Session, SMTP
from loguru import logger

from app.config import settings
from app.storage import get_token_by_address, store_email
from app.utils.email_parser import parse_email
from app.ws_manager import ws_manager


class MailHandler:
    """SMTP 邮件处理器"""

    async def handle_RCPT(
        self, server: SMTP, session: Session, envelope: Envelope, address: str, rcpt_options: list
    ) -> str:
        """接受所有收件人地址（catch-all）"""
        envelope.rcpt_tos.append(address)
        return "250 OK"

    async def handle_DATA(self, server: SMTP, session: Session, envelope: Envelope) -> str:
        """处理收到的邮件数据"""
        try:
            raw_data = envelope.content
            if isinstance(raw_data, bytes):
                raw_data = raw_data

            # 解析邮件
            parsed = parse_email(raw_data)

            # 为每个收件人存储邮件
            for rcpt in envelope.rcpt_tos:
                token = await get_token_by_address(rcpt)
                if not token:
                    logger.debug(f"收件人 {rcpt} 无对应邮箱，跳过")
                    continue

                email_id = await store_email(
                    token=token,
                    from_addr=parsed["from_addr"],
                    to_addr=rcpt,
                    subject=parsed["subject"],
                    text_body=parsed["text_body"],
                    html_body=parsed["html_body"],
                    attachments=parsed["attachments"],
                )

                if email_id:
                    # WebSocket 推送新邮件通知
                    preview = (parsed["text_body"] or "")[:100]
                    await ws_manager.send_to_token(token, {
                        "type": "new_email",
                        "data": {
                            "id": email_id,
                            "fromAddr": parsed["from_addr"],
                            "subject": parsed["subject"],
                            "receivedAt": parsed["received_at"],
                            "hasAttachments": len(parsed["attachments"]) > 0,
                            "preview": preview,
                        },
                    })

        except Exception as e:
            logger.error(f"处理邮件失败: {e}")
            return "500 Error processing message"

        return "250 Message accepted"


_controller: Controller | None = None


async def start_smtp_server() -> None:
    """启动 SMTP 服务"""
    global _controller
    handler = MailHandler()
    _controller = Controller(
        handler,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        data_size_limit=10485760,  # 10MB
    )
    _controller.start()
    logger.info(f"SMTP 服务启动: {settings.smtp_host}:{settings.smtp_port}")


async def stop_smtp_server() -> None:
    """停止 SMTP 服务"""
    global _controller
    if _controller:
        _controller.stop()
        _controller = None
        logger.info("SMTP 服务已停止")
