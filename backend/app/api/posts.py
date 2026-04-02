"""文章 API"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import Optional
from math import ceil

from app.core.database import get_db
from app.core.security import get_current_user, get_optional_user
from app.models.user import Post, Tag, Category, User
from app.schemas import PostCreate, PostUpdate, PostListItem, PostDetail, PostListResponse, Pagination
from app.services.markdown_service import render_markdown, make_slug

router = APIRouter(prefix="/posts", tags=["文章"])

_LOAD_OPTS = [
    joinedload(Post.author),
    joinedload(Post.category),
    joinedload(Post.tags),
]


def _get_post_or_404(db: Session, slug: str) -> Post:
    post = db.query(Post).options(*_LOAD_OPTS).filter(Post.slug == slug).first()
    if not post:
        raise HTTPException(404, "文章不存在")
    return post


# ─── 公开接口 ─────────────────────────────────────────

@router.get("", response_model=PostListResponse, summary="文章列表")
def list_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    category: Optional[str] = None,
    tag: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    query = db.query(Post).options(*_LOAD_OPTS)

    # 非管理员只看已发布
    if not current_user:
        query = query.filter(Post.is_published == True)

    if category:
        query = query.join(Category).filter(Category.slug == category)
    if tag:
        query = query.join(Post.tags).filter(Tag.slug == tag)
    if q:
        query = query.filter(or_(Post.title.contains(q), Post.summary.contains(q), Post.content.contains(q)))

    total = query.count()
    posts = (query
             .order_by(Post.is_top.desc(), Post.created_at.desc())
             .offset((page - 1) * page_size)
             .limit(page_size)
             .all())

    return PostListResponse(
        items=[PostListItem.model_validate(p) for p in posts],
        pagination=Pagination(total=total, page=page, page_size=page_size, pages=ceil(total / page_size) if total else 1)
    )


@router.get("/{slug}", response_model=PostDetail, summary="文章详情")
def get_post(
    slug: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    post = _get_post_or_404(db, slug)
    if not post.is_published and not current_user:
        raise HTTPException(403, "文章未发布")
    # 访问量 +1
    post.views += 1
    db.commit()
    db.refresh(post)
    return PostDetail.model_validate(post)


# ─── 管理员接口 ───────────────────────────────────────

@router.post("", response_model=PostDetail, status_code=201, summary="新建文章")
def create_post(
    data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    slug = data.slug or make_slug(data.title)
    # slug 唯一性：如果冲突则加随机后缀
    base_slug = slug
    counter = 1
    while db.query(Post).filter(Post.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    tags = db.query(Tag).filter(Tag.id.in_(data.tag_ids or [])).all()
    post = Post(
        title=data.title,
        slug=slug,
        summary=data.summary or data.content[:150],
        content=data.content,
        content_html=render_markdown(data.content),
        cover=data.cover or "",
        is_published=data.is_published,
        is_top=data.is_top,
        author_id=current_user.id,
        category_id=data.category_id,
        tags=tags,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return PostDetail.model_validate(post)


@router.put("/{slug}", response_model=PostDetail, summary="更新文章")
def update_post(
    slug: str,
    data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = _get_post_or_404(db, slug)
    update_data = data.model_dump(exclude_unset=True)

    if "tag_ids" in update_data:
        post.tags = db.query(Tag).filter(Tag.id.in_(update_data.pop("tag_ids"))).all()

    if "content" in update_data:
        update_data["content_html"] = render_markdown(update_data["content"])

    for k, v in update_data.items():
        setattr(post, k, v)

    db.commit()
    db.refresh(post)
    return PostDetail.model_validate(post)


@router.delete("/{slug}", status_code=204, summary="删除文章")
def delete_post(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = _get_post_or_404(db, slug)
    db.delete(post)
    db.commit()
