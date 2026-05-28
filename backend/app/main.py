"""backend/app/main.py — FastAPI 应用入口

挂载路由、WebSocket、启动 SMTP 服务和清理任务。
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.cleaner import start_cleaner
from app.exceptions import AppError, app_error_handler
from app.routers import mailbox, emails, seo
from app.smtp_server import start_smtp_server, stop_smtp_server
from app.storage import close_redis, get_mailbox
from app.ws_manager import ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    await start_smtp_server()
    cleaner_task = asyncio.create_task(start_cleaner())
    logger.info("应用启动完成")
    yield
    # 关闭
    cleaner_task.cancel()
    await stop_smtp_server()
    await close_redis()
    logger.info("应用已关闭")


app = FastAPI(
    title="Temp Mail API",
    description="临时邮箱工具站后端服务",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册自定义异常处理器
app.add_exception_handler(AppError, app_error_handler)

# 挂载路由
app.include_router(mailbox.router)
app.include_router(emails.router)
app.include_router(seo.router)


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """WebSocket 实时推送新邮件"""
    # 验证 token
    data = await get_mailbox(token)
    if not data:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await ws_manager.connect(token, websocket)
    try:
        while True:
            # 接收客户端心跳
            msg = await websocket.receive_json()
            if msg.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        pass
    finally:
        ws_manager.disconnect(token, websocket)
