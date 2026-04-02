"""应用配置"""
from pydantic_settings import BaseSettings
from typing import Optional
import secrets


class Settings(BaseSettings):
    # 应用
    APP_NAME: str = "TechBlog"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 安全
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # 数据库
    DATABASE_URL: str = "sqlite:///./blog.db"

    # 博主信息（可在 .env 中覆盖）
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    ADMIN_EMAIL: str = "admin@example.com"
    BLOG_TITLE: str = "我的技术博客"
    BLOG_SUBTITLE: str = "记录技术与思考"
    BLOG_AUTHOR: str = "Admin"

    # 分页
    PAGE_SIZE: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
