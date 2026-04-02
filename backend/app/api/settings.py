"""博客设置 API"""
import json, os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.security import get_current_user, get_password_hash, verify_password
from app.models.user import User
from app.core.database import SessionLocal
from app.core.config import settings

router = APIRouter(prefix="/settings", tags=["设置"])

# 设置文件路径（保存在 backend/ 目录下，与 main.py 同级）
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "../../..", "backend", "blog_settings.json")
SETTINGS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "blog_settings.json"))


def _load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_settings(data: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class BlogSettingsIn(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    author: Optional[str] = None
    footer: Optional[str] = None
    github: Optional[str] = None
    icp: Optional[str] = None


class PasswordChangeIn(BaseModel):
    old_password: str
    new_password: str


@router.get("", summary="获取博客设置")
def get_settings():
    """公开接口，返回博客公开配置"""
    saved = _load_settings()
    return {
        "title": saved.get("title", settings.BLOG_TITLE),
        "subtitle": saved.get("subtitle", settings.BLOG_SUBTITLE),
        "author": saved.get("author", settings.BLOG_AUTHOR),
        "footer": saved.get("footer", f"© {settings.BLOG_AUTHOR}"),
        "github": saved.get("github", ""),
        "icp": saved.get("icp", ""),
    }


@router.put("", summary="更新博客设置（需登录）")
def update_settings(
    data: BlogSettingsIn,
    current_user: User = Depends(get_current_user)
):
    saved = _load_settings()
    update_data = data.model_dump(exclude_none=True)
    saved.update(update_data)
    _save_settings(saved)
    return {"message": "设置已保存", **saved}


@router.put("/password", summary="修改密码")
def change_password(
    data: PasswordChangeIn,
    current_user: User = Depends(get_current_user)
):
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(400, "原密码错误")
    if len(data.new_password) < 6:
        raise HTTPException(400, "新密码至少6位")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == current_user.id).first()
        user.hashed_password = get_password_hash(data.new_password)
        db.commit()
    finally:
        db.close()

    return {"message": "密码修改成功"}
