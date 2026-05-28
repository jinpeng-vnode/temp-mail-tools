# PROJECT_BOOTSTRAP.md — 临时邮箱工具站

> 项目启动/部署快速指南，供全栈工程师和后续维护者参考。

## 项目概述

临时邮箱工具站，提供一次性匿名邮箱服务。用户无需注册即可获取临时邮箱地址，实时接收邮件。

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python 3.11 + FastAPI + aiosmtpd + Redis |
| 前端 | Vue 3 + TypeScript + Ant Design Vue 4 + Pinia + vue-i18n |
| 基础设施 | Docker Compose + Nginx + Redis |
| 包管理 | 后端: uv / 前端: yarn |

## 目录结构

```
temp-mail-tools/
├── backend/          # 后端服务（FastAPI + SMTP）
├── frontend/         # 前端应用（Vue 3 SPA）
├── infra/            # 基础设施配置
│   ├── docker-compose.yml
│   ├── nginx/nginx.conf
│   └── redis/redis.conf
└── design/           # 设计文档
```

## 一键启动

```bash
cd infra
cp .env.example .env  # 按需修改配置
docker compose up -d --build
```

启动后访问：`http://localhost:8080`

## 服务端口

| 服务 | 容器内端口 | 宿主机端口 | 说明 |
|------|-----------|-----------|------|
| Nginx | 80 | 8080 | HTTP 入口 |
| Backend API | 8000 | — | 通过 Nginx 代理 |
| SMTP | 25 | 2525 | 邮件接收 |
| Redis | 6379 | — | 仅内部访问 |

## 环境变量

参见 `infra/.env.example` 和 `backend/.env.example`。

关键配置：
- `MAIL_DOMAINS`: 接收邮件的域名（逗号分隔）
- `MAIL_EXPIRE_MINUTES`: 邮箱过期时间
- `HTTP_PORT`: 对外 HTTP 端口

## 常用命令

```bash
# 启动所有服务
cd infra && docker compose up -d --build

# 查看日志
docker compose logs -f backend

# 重启后端（代码修改后）
docker compose restart backend

# 重建前端（前端代码修改后）
docker compose up -d --build frontend

# 停止所有服务
docker compose down

# 清理数据
docker compose down -v
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/mailbox | 生成临时邮箱 |
| GET | /api/mailbox/{token} | 查询邮箱状态 |
| DELETE | /api/mailbox/{token} | 删除邮箱 |
| GET | /api/mailbox/{token}/emails | 邮件列表 |
| GET | /api/mailbox/{token}/emails/{id} | 邮件详情 |
| GET | /api/mailbox/{token}/emails/{id}/attachments/{file} | 下载附件 |
| WS | /ws/{token} | WebSocket 实时推送 |
| GET | /api/health | 健康检查 |

## 健康检查

```bash
curl http://localhost:8080/api/health
# 期望: {"status":"ok"}
```

## 注意事项

1. SMTP 端口 25 在很多 ISP 被封锁，开发环境映射到 2525
2. 生产环境需配置真实域名的 MX 记录指向服务器
3. Redis 配置了 256MB 内存限制 + LRU 淘汰策略
4. 前端构建产物通过 Docker volume 共享给 Nginx
