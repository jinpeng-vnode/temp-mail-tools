"""backend/app/cleaner.py — 过期邮件定时清理任务

定期扫描并清理已过期的邮箱数据（Redis TTL 兜底，此为主动清理）。
"""
from __future__ import annotations

import asyncio

from loguru import logger

from app.config import settings
from app.storage import get_expired_tokens, delete_mailbox
from app.ws_manager import ws_manager


async def cleanup_expired() -> None:
    """清理已过期的邮箱"""
    try:
        expired = await get_expired_tokens()
        for token in expired:
            # 通知 WebSocket 客户端邮箱已过期
            await ws_manager.send_to_token(token, {
                "type": "mailbox_expired",
                "data": None,
            })
            await delete_mailbox(token)
        if expired:
            logger.info(f"清理了 {len(expired)} 个过期邮箱")
    except Exception as e:
        logger.error(f"清理任务异常: {e}")


async def start_cleaner() -> None:
    """启动定时清理任务"""
    logger.info(f"清理任务启动，间隔 {settings.cleaner_interval}s")
    while True:
        await asyncio.sleep(settings.cleaner_interval)
        await cleanup_expired()
