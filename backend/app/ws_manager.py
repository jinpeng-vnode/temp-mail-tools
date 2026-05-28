"""backend/app/ws_manager.py — WebSocket 连接管理器

管理按 token 分组的 WebSocket 连接，支持向特定邮箱推送新邮件通知。
"""
from __future__ import annotations

from fastapi import WebSocket
from loguru import logger


class ConnectionManager:
    """WebSocket 连接管理器，按 token 分组"""

    def __init__(self) -> None:
        # token -> set of websocket connections
        self._connections: dict[str, set[WebSocket]] = {}

    async def connect(self, token: str, ws: WebSocket) -> None:
        """接受并注册连接"""
        await ws.accept()
        if token not in self._connections:
            self._connections[token] = set()
        self._connections[token].add(ws)
        logger.debug(f"WS 连接: token={token[:8]}..., 当前连接数={len(self._connections[token])}")

    def disconnect(self, token: str, ws: WebSocket) -> None:
        """移除连接"""
        if token in self._connections:
            self._connections[token].discard(ws)
            if not self._connections[token]:
                del self._connections[token]

    async def send_to_token(self, token: str, message: dict) -> None:
        """向指定 token 的所有连接推送消息"""
        if token not in self._connections:
            return
        dead = set()
        for ws in self._connections[token]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        # 清理断开的连接
        for ws in dead:
            self._connections[token].discard(ws)
        if not self._connections.get(token):
            self._connections.pop(token, None)


ws_manager = ConnectionManager()
