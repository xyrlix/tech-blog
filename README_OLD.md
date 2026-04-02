# TechBlog — 个人技术博客

基于 **FastAPI + SQLite + 原生前端** 的轻量个人博客系统。

## 特性

- ✅ **前后端分离**：REST API + 静态 HTML
- ✅ **Markdown 写作**：后端渲染，代码高亮
- ✅ **多视角管理**：文章 / 分类 / 标签 / 评论
- ✅ **JWT 认证**：安全的管理员登录
- ✅ **图片上传**：直接粘贴或选择文件
- ✅ **全文搜索**：标题 + 内容搜索
- ✅ **响应式布局**：手机/平板/桌面均适配
- ✅ **Docker 部署**：一键启动

## 快速开始

### 本地开发（推荐）

```bash
cd F:/output/tech-blog
python start.py
```

访问：
- 博客首页：http://localhost:8000/pages/index.html
- 后台管理：http://localhost:8000/pages/admin/dashboard.html
- API 文档：http://localhost:8000/docs
- 默认账号：`admin` / `admin123`

### Docker 部署

```bash
cd F:/output/tech-blog/deploy
docker-compose up -d
```

## 项目结构

```
tech-blog/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/            # 路由（auth/posts/taxonomy/comments/upload）
│   │   ├── core/           # 配置/数据库/JWT认证
│   │   ├── models/         # SQLAlchemy 数据模型
│   │   ├── schemas/        # Pydantic 校验模型
│   │   └── services/       # Markdown 渲染服务
│   ├── main.py             # FastAPI 应用入口
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   ├── css/            # main.css / admin.css
│   │   ├── js/             # app.js（公共工具库）
│   │   └── img/            # 上传的图片
│   └── pages/
│       ├── index.html      # 博客首页
│       ├── post.html       # 文章详情页
│       ├── login.html      # 登录页
│       └── admin/          # 后台管理页面
│           ├── dashboard.html
│           ├── editor.html  # Markdown 编辑器
│           ├── posts.html
│           ├── taxonomy.html
│           └── comments.html
├── deploy/
│   └── docker-compose.yml
└── start.py                # 一键启动脚本
```

## API 接口

完整文档见 `http://localhost:8000/docs`（Swagger UI）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/login | 登录 |
| GET  | /api/v1/posts | 文章列表（支持分页/搜索/过滤）|
| GET  | /api/v1/posts/{slug} | 文章详情 |
| POST | /api/v1/posts | 新建文章（需登录）|
| PUT  | /api/v1/posts/{slug} | 更新文章（需登录）|
| DELETE | /api/v1/posts/{slug} | 删除文章（需登录）|
| GET  | /api/v1/categories | 分类列表 |
| GET  | /api/v1/tags | 标签列表 |
| GET  | /api/v1/posts/{slug}/comments | 评论列表 |
| POST | /api/v1/posts/{slug}/comments | 发表评论 |
| POST | /api/v1/upload/image | 上传图片（需登录）|

## 自定义配置

在 `backend/.env` 中配置（不存在时创建）：

```env
BLOG_TITLE=我的技术博客
BLOG_SUBTITLE=记录技术与思考
BLOG_AUTHOR=你的名字
ADMIN_USERNAME=admin
ADMIN_PASSWORD=你的密码
ADMIN_EMAIL=your@email.com
SECRET_KEY=随机字符串（生产环境必须修改）
```

## 扩展建议

- 添加 **RSS 订阅**：`/api/v1/rss`
- 添加 **统计分析**：接入 umami 或 Google Analytics
- 升级数据库：将 SQLite 替换为 PostgreSQL
- CDN：图片上传改为 OSS/S3
