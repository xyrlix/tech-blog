"""分类 & 标签 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import Category, Tag, Post, User
from app.schemas import CategoryCreate, CategoryOut, TagCreate, TagOut
from app.services.markdown_service import make_slug
from typing import List

router = APIRouter(tags=["分类与标签"])


# ─── 分类 ──────────────────────────────────────────

@router.get("/categories", response_model=List[CategoryOut], summary="分类列表")
def list_categories(db: Session = Depends(get_db)):
    cats = db.query(Category).all()
    result = []
    for c in cats:
        out = CategoryOut.model_validate(c)
        out.post_count = db.query(Post).filter(Post.category_id == c.id, Post.is_published == True).count()
        result.append(out)
    return result


@router.post("/categories", response_model=CategoryOut, status_code=201, summary="新建分类")
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    if db.query(Category).filter(Category.slug == data.slug).first():
        raise HTTPException(400, "slug 已存在")
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/categories/{cat_id}", status_code=204, summary="删除分类")
def delete_category(cat_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(404, "分类不存在")
    db.delete(cat)
    db.commit()


# ─── 标签 ──────────────────────────────────────────

@router.get("/tags", response_model=List[TagOut], summary="标签列表")
def list_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()


@router.post("/tags", response_model=TagOut, status_code=201, summary="新建标签")
def create_tag(
    data: TagCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    if db.query(Tag).filter(Tag.slug == data.slug).first():
        raise HTTPException(400, "slug 已存在")
    tag = Tag(**data.model_dump())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/tags/{tag_id}", status_code=204, summary="删除标签")
def delete_tag(tag_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(404, "标签不存在")
    db.delete(tag)
    db.commit()
