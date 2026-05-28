"""backend/app/config.py — 环境变量配置管理

使用 Pydantic Settings 从环境变量读取配置。
"""
from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置，从环境变量或 .env 文件读取"""

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # 邮箱域名（逗号分隔）
    mail_domains: str = "tempmail.dev"
    # 邮箱过期时间（分钟）
    mail_expire_minutes: int = 60

    # SMTP
    smtp_host: str = "0.0.0.0"
    smtp_port: int = 25

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "*"

    # 清理任务间隔（秒）
    cleaner_interval: int = 60

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def domains_list(self) -> list[str]:
        """返回域名列表"""
        return [d.strip() for d in self.mail_domains.split(",") if d.strip()]

    @property
    def cors_origins_list(self) -> list[str]:
        """返回CORS允许的源列表"""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
