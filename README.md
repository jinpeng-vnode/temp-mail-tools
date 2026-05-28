# Temp Mail Tools — 临时邮箱工具站

## 功能全景图 — 完成度: 85%

> 项目定义：临时邮箱工具站，对标 Temp-Mail.org（46M月流量），提供一次性匿名邮箱服务，核心通过 Programmatic SEO 获取搜索流量
> 当前阶段：开发中（待部署）
> 下一步优先级：
> 1. 部署到 Mac Mini（Docker Compose 一键启动）
> 2. SSL/TLS 证书配置
> 3. 域名 DNS 配置
> 禁止：
> - 修改 Mac Mini 宿主机系统配置
> - 使用非 Docker 方式部署
> - 硬编码敏感信息

temp-mail-tools
├── 后端服务（backend/）
│   ├── SMTP 邮件接收服务（aiosmtpd） — ✅
│   ├── REST API（邮箱生成/查询/删除） — ✅
│   ├── 邮件存储与自动过期清理（Redis） — ✅
│   ├── WebSocket 实时推送新邮件 — ✅
│   ├── SEO API（sitemap/landing） — ✅
│   └── Rate Limiting（滑动窗口） — ✅
├── 前端应用（frontend/）
│   ├── 首页（一键生成临时邮箱） — ✅
│   ├── 收件箱（实时显示邮件列表） — ✅
│   ├── 邮件详情（HTML渲染+附件下载） — ✅
│   ├── 中英文双语切换 — ✅
│   ├── 广告位预留组件 — ✅
│   └── SEO落地页 — ✅
├── SEO 模块
│   ├── Programmatic SEO 落地页生成 — ✅
│   ├── sitemap.xml 动态生成 — ✅
│   ├── robots.txt — ✅
│   ├── Schema.org 结构化数据 — ❌
│   ├── Open Graph 元标签 — ✅
│   └── hreflang 多语言标记 — ❌
├── 基础设施（infra/）
│   ├── Docker Compose 编排 — ✅
│   ├── Nginx 反向代理（容器内） — ✅
│   └── SSL/TLS 证书管理 — ❌
└── 待完成
    └── 部署到 Mac Mini — ❌
