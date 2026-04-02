"""Pydantic Schemas"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


# ─── Tag ────────────────────────────────────────────
class TagBase(BaseModel):
    name: str
    slug: str

class TagCreate(TagBase):
    pass

class TagOut(TagBase):
    id: int
    class Config:
        from_attributes = True


# ─── Category ───────────────────────────────────────
class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = ""

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id: int
    post_count: Optional[int] = 0
    class Config:
        from_attributes = True


# ─── User ───────────────────────────────────────────
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    bio: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[str] = None

class UserOut(UserBase):
    id: int
    bio: str = ""
    avatar: str = ""
    created_at: datetime
    class Config:
        from_attributes = True


# ─── Auth ───────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ─── Post ───────────────────────────────────────────
class PostBase(BaseModel):
    title: str
    summary: Optional[str] = ""
    content: str
    cover: Optional[str] = ""
    is_published: Optional[bool] = False
    is_top: Optional[bool] = False
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = []

class PostCreate(PostBase):
    slug: Optional[str] = None   # 不传则自动生成

class PostUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    cover: Optional[str] = None
    is_published: Optional[bool] = None
    is_top: Optional[bool] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None

class PostListItem(BaseModel):
    id: int
    title: str
    slug: str
    summary: str
    cover: str
    is_published: bool
    is_top: bool
    views: int
    author: UserOut
    category: Optional[CategoryOut] = None
    tags: List[TagOut] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class PostDetail(PostListItem):
    content: str
    content_html: str


# ─── Comment ────────────────────────────────────────
class CommentCreate(BaseModel):
    nickname: str
    email: Optional[str] = ""
    content: str
    parent_id: Optional[int] = None

class CommentOut(BaseModel):
    id: int
    nickname: str
    content: str
    created_at: datetime
    parent_id: Optional[int] = None
    replies: Optional[List["CommentOut"]] = []
    class Config:
        from_attributes = True

CommentOut.model_rebuild()


# ─── 通用分页 ────────────────────────────────────────
class Pagination(BaseModel):
    total: int
    page: int
    page_size: int
    pages: int

class PostListResponse(BaseModel):
    items: List[PostListItem]
    pagination: Pagination
