"""backend/app/storage.py — Redis 存储层

封装邮箱/邮件的 CRUD 操作，使用 Redis Hash + Sorted Set。
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import redis.asyncio as aioredis
from loguru import logger

from app.config import settings


# Redis 连接池（延迟初始化）
_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """获取 Redis 连接"""
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis


async def close_redis() -> None:
    """关闭 Redis 连接"""
    global _redis
    if _redis:
        await _redis.close()
        _redis = None


async def create_mailbox(address: str, token: str, ttl_seconds: int) -> dict:
    """创建临时邮箱"""
    r = await get_redis()
    now = datetime.now(timezone.utc)
    expires_at = datetime.fromtimestamp(now.timestamp() + ttl_seconds, tz=timezone.utc)

    mailbox_data = {
        "address": address,
        "token": token,
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
    }

    pipe = r.pipeline()
    # 邮箱信息
    pipe.hset(f"mailbox:{token}", mapping=mailbox_data)
    pipe.expire(f"mailbox:{token}", ttl_seconds)
    # 地址到token的映射
    pipe.set(f"addr:{address}", token, ex=ttl_seconds)
    await pipe.execute()

    logger.info(f"创建邮箱: {address} (token={token[:8]}..., ttl={ttl_seconds}s)")
    return mailbox_data


async def get_mailbox(token: str) -> dict | None:
    """查询邮箱信息"""
    r = await get_redis()
    data = await r.hgetall(f"mailbox:{token}")
    return data if data else None


async def get_token_by_address(address: str) -> str | None:
    """通过邮箱地址获取token"""
    r = await get_redis()
    return await r.get(f"addr:{address}")


async def delete_mailbox(token: str) -> bool:
    """删除邮箱及所有邮件"""
    r = await get_redis()
    mailbox = await get_mailbox(token)
    if not mailbox:
        return False

    # 获取所有邮件ID
    email_ids = await r.zrange(f"emails:{token}", 0, -1)

    pipe = r.pipeline()
    # 删除邮箱
    pipe.delete(f"mailbox:{token}")
    pipe.delete(f"addr:{mailbox['address']}")
    pipe.delete(f"emails:{token}")
    # 删除所有邮件和附件
    for eid in email_ids:
        pipe.delete(f"email:{eid}")
        # 获取附件列表并删除
        attachments_json = await r.hget(f"email:{eid}", "attachments_json")
        if attachments_json:
            for att in json.loads(attachments_json):
                pipe.delete(f"attachment:{eid}:{att['filename']}")
    await pipe.execute()

    logger.info(f"删除邮箱: {mailbox['address']} (含 {len(email_ids)} 封邮件)")
    return True


async def store_email(
    token: str,
    from_addr: str,
    to_addr: str,
    subject: str,
    text_body: str | None,
    html_body: str | None,
    attachments: list[dict],
) -> str | None:
    """存储邮件，返回邮件ID"""
    r = await get_redis()

    # 检查邮箱是否存在
    if not await r.exists(f"mailbox:{token}"):
        return None

    email_id = uuid.uuid4().hex[:16]
    now = datetime.now(timezone.utc)
    ttl = await r.ttl(f"mailbox:{token}")
    if ttl <= 0:
        return None

    # 附件元数据（不含二进制内容）
    att_meta = [
        {"filename": a["filename"], "content_type": a["content_type"], "size": a["size"]}
        for a in attachments
    ]

    email_data = {
        "id": email_id,
        "from_addr": from_addr,
        "to_addr": to_addr,
        "subject": subject,
        "text_body": text_body or "",
        "html_body": html_body or "",
        "received_at": now.isoformat(),
        "attachments_json": json.dumps(att_meta),
    }

    pipe = r.pipeline()
    pipe.hset(f"email:{email_id}", mapping=email_data)
    pipe.expire(f"email:{email_id}", ttl)
    pipe.zadd(f"emails:{token}", {email_id: now.timestamp()})
    pipe.expire(f"emails:{token}", ttl)

    # 存储附件二进制数据
    for a in attachments:
        pipe.set(f"attachment:{email_id}:{a['filename']}", a["content"], ex=ttl)

    await pipe.execute()
    logger.info(f"存储邮件: {from_addr} -> {to_addr}, subject={subject[:30]}")
    return email_id


async def get_emails(token: str, page: int = 1, size: int = 20) -> tuple[list[dict], int]:
    """获取邮件列表（分页，按时间倒序）"""
    r = await get_redis()
    total = await r.zcard(f"emails:{token}")
    start = (page - 1) * size
    end = start + size - 1

    # 倒序获取
    email_ids = await r.zrevrange(f"emails:{token}", start, end)
    emails = []
    for eid in email_ids:
        data = await r.hgetall(f"email:{eid}")
        if data:
            emails.append(data)
    return emails, total


async def get_email(email_id: str) -> dict | None:
    """获取邮件详情"""
    r = await get_redis()
    data = await r.hgetall(f"email:{email_id}")
    return data if data else None


async def get_attachment(email_id: str, filename: str) -> bytes | None:
    """获取附件二进制数据"""
    r = await get_redis()
    # 附件用非decode模式读取
    r_bin = aioredis.from_url(settings.redis_url, decode_responses=False)
    try:
        data = await r_bin.get(f"attachment:{email_id}:{filename}")
        return data
    finally:
        await r_bin.close()


async def get_expired_tokens() -> list[str]:
    """获取已过期的邮箱token列表（用于清理）"""
    r = await get_redis()
    # Redis TTL 自动过期，此方法用于主动扫描
    cursor = 0
    expired = []
    while True:
        cursor, keys = await r.scan(cursor, match="mailbox:*", count=100)
        for key in keys:
            ttl = await r.ttl(key)
            if ttl <= 0:
                expired.append(key.replace("mailbox:", ""))
        if cursor == 0:
            break
    return expired
