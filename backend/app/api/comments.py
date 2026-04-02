"""评论 API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import Comment, Post, User
from app.schemas import CommentCreate, CommentOut

router = APIRouter(tags=["评论"])


@router.get("/posts/{slug}/comments", response_model=List[CommentOut], summary="获取文章评论")
def list_comments(slug: str, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.slug == slug).first()
    if not post:
        raise HTTPException(404, "文章不存在")
    # 只返回顶级评论，回复通过 replies 嵌套
    comments = (db.query(Comment)
                .filter(Comment.post_id == post.id, Comment.parent_id == None, Comment.is_approved == True)
                .order_by(Comment.created_at.asc())
                .all())
    return [CommentOut.model_validate(c) for c in comments]


@router.post("/posts/{slug}/comments", response_model=CommentOut, status_code=201, summary="发表评论")
def create_comment(slug: str, data: CommentCreate, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.slug == slug, Post.is_published == True).first()
    if not post:
        raise HTTPException(404, "文章不存在")
    comment = Comment(
        post_id=post.id,
        nickname=data.nickname,
        email=data.email or "",
        content=data.content,
        parent_id=data.parent_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    # 手动构建 CommentOut，避免 replies=None 问题
    return CommentOut(
        id=comment.id,
        nickname=comment.nickname,
        content=comment.content,
        created_at=comment.created_at,
        parent_id=comment.parent_id,
        replies=[],
    )


@router.delete("/comments/{comment_id}", status_code=204, summary="删除评论")
def delete_comment(comment_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    c = db.query(Comment).filter(Comment.id == comment_id).first()
    if not c:
        raise HTTPException(404, "评论不存在")
    db.delete(c)
    db.commit()


@router.get("/comments", summary="管理员获取所有评论（含未审核）")
def list_all_comments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """管理员查看全部评论，含未审核评论，按创建时间倒序"""
    from math import ceil
    query = db.query(Comment).options(joinedload(Comment.post))
    total = query.count()
    comments = query.order_by(Comment.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = []
    for c in comments:
        items.append({
            "id": c.id,
            "nickname": c.nickname,
            "email": c.email,
            "content": c.content,
            "is_approved": c.is_approved,
            "created_at": c.created_at.isoformat(),
            "post_slug": c.post.slug if c.post else "",
            "post_title": c.post.title if c.post else "",
            "parent_id": c.parent_id,
        })
    return {"items": items, "total": total, "page": page, "pages": ceil(total / page_size) if total else 1}


@router.put("/comments/{comment_id}/approve", summary="审核评论（通过/驳回）")
def approve_comment(
    comment_id: int,
    approved: bool = True,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    c = db.query(Comment).filter(Comment.id == comment_id).first()
    if not c:
        raise HTTPException(404, "评论不存在")
    c.is_approved = approved
    db.commit()
    return {"id": c.id, "is_approved": c.is_approved}

