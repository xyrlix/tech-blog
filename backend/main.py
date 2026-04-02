"""FastAPI 应用入口"""
import os, sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# 确保 app 包可被找到
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, Category, Tag
from app.api import auth, posts, taxonomy, comments, upload, settings as settings_api


# ─── 启动时初始化 ────────────────────────────────────────

def _init_db():
    """建表 + 创建默认管理员"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == settings.ADMIN_USERNAME).first():
            admin = User(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                bio="博客管理员",
            )
            db.add(admin)

        # 默认分类
        if db.query(Category).count() == 0:
            for name, slug in [("技术", "tech"), ("随笔", "essay"), ("项目", "project")]:
                db.add(Category(name=name, slug=slug))

        # 默认标签
        if db.query(Tag).count() == 0:
            for name, slug in [("Python", "python"), ("Go", "go"), ("C++", "cpp"), ("算法", "algorithm")]:
                db.add(Tag(name=name, slug=slug))

        db.commit()
        print(f"[Init] Admin user: {settings.ADMIN_USERNAME} / {settings.ADMIN_PASSWORD}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _init_db()
    yield


# ─── 创建 App ────────────────────────────────────────────

app = FastAPI(
    title=settings.BLOG_TITLE,
    version=settings.APP_VERSION,
    description="个人技术博客 REST API",
    lifespan=lifespan,
)

# CORS（开发环境放行所有来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── 注册路由 ─────────────────────────────────────────────

API_PREFIX = "/api/v1"
app.include_router(auth.router,     prefix=API_PREFIX)
app.include_router(posts.router,    prefix=API_PREFIX)
app.include_router(taxonomy.router, prefix=API_PREFIX)
app.include_router(comments.router, prefix=API_PREFIX)
app.include_router(upload.router,       prefix=API_PREFIX)
app.include_router(settings_api.router, prefix=API_PREFIX)


# ─── 博客元信息接口 ───────────────────────────────────────

@app.get("/api/v1/info", tags=["系统"])
def blog_info():
    import json, os
    settings_file = Path(__file__).parent / "blog_settings.json"
    saved = {}
    if settings_file.exists():
        try:
            saved = json.loads(settings_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "title": saved.get("title", settings.BLOG_TITLE),
        "subtitle": saved.get("subtitle", settings.BLOG_SUBTITLE),
        "author": saved.get("author", settings.BLOG_AUTHOR),
        "footer": saved.get("footer", f"© {settings.BLOG_AUTHOR}"),
        "github": saved.get("github", ""),
        "icp": saved.get("icp", ""),
    }


# ─── 静态文件 / SPA 回退 ──────────────────────────────────

FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "public"

if FRONTEND_DIR.exists():
    app.mount("/img",   StaticFiles(directory=str(FRONTEND_DIR / "img")),   name="img")
    app.mount("/css",   StaticFiles(directory=str(FRONTEND_DIR / "css")),   name="css")
    app.mount("/js",    StaticFiles(directory=str(FRONTEND_DIR / "js")),    name="js")
    app.mount("/pages", StaticFiles(directory=str(FRONTEND_DIR.parent / "pages"), html=True), name="pages")

    @app.get("/", include_in_schema=False)
    async def serve_root():
        return FileResponse(str(FRONTEND_DIR.parent / "pages" / "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
