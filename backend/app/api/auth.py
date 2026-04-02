"""认证 API"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_current_user
from app.models.user import User
from app.schemas import LoginRequest, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["认证"])


class ProfileUpdateIn(BaseModel):
    email: Optional[str] = None
    bio: Optional[str] = None


@router.post("/login", response_model=TokenOut, summary="登录")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = create_access_token({"sub": user.username})
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut, summary="获取当前用户信息")
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserOut, summary="更新个人信息")
def update_me(
    data: ProfileUpdateIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == current_user.id).first()
    if data.email is not None:
        user.email = data.email
    if data.bio is not None:
        user.bio = data.bio
    db.commit()
    db.refresh(user)
    return user

