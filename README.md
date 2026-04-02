# TechBlog — 个人技术博客

基于 **FastAPI + SQLite + 原生前端** 的轻量个人博客系统。

## ✨ 特性

- ✅ **前后端分离**：REST API + 静态 HTML（无需框架，纯原生 JS）
- ✅ **Markdown 写作**：后端渲染 + 代码高亮 + 实时预览
- ✅ **多视角管理**：文章 / 分类 / 标签 / 评论 / 系统设置
- ✅ **JWT 认证**：安全的登录 + 权限控制
- ✅ **图片上传**：直接粘贴或选择文件（自动压缩 + 随机命名）
- ✅ **全文搜索**：标题 + 内容 + 摘要模糊搜索
- ✅ **评论审核**：新评论待审核 → 管理员通过/驳回
- ✅ **博客设置**：动态修改博客标题/副标题/作者/页脚/GitHub/ICP备案
- ✅ **响应式布局**：手机/平板/桌面均适配（深色/浅色主题）
- ✅ **一键启动**：Python 脚本自动安装依赖 + 启动服务
- ✅ **Docker 部署**：Nginx 反代 + 数据库持久化
- ✅ **归档系统**：按年/月分组，文章统计总览

## 🚀 快速开始

### 本地开发（推荐）

**方法一：一键启动（推荐）**
```bash
cd tech-blog
python start.py
```

**方法二：手动启动**
```bash
cd tech-blog/backend
pip install -r requirements.txt
python main.py
```

访问地址：
- 🏠 **博客首页**：[http://localhost:8000/pages/index.html](http://localhost:8000/pages/index.html)
- 📝 **后台管理**：[http://localhost:8000/pages/admin/dashboard.html](http://localhost:8000/pages/admin/dashboard.html)
- 📚 **文章归档**：[http://localhost:8000/pages/archive.html](http://localhost:8000/pages/archive.html)
- 📖 **API 文档**：[http://localhost:8000/docs](http://localhost:8000/docs)（Swagger UI）
- 🔐 **默认账号**：`admin` / `admin123`

### Docker 部署（生产环境）

```bash
cd tech-blog/deploy
docker-compose up -d
```

生产环境需配置 Nginx 转发和 HTTPS。

---

## 📁 项目结构

```
tech-blog/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py      # 用户认证（登录/退出/个人信息）
│   │   │   ├── posts.py     # 文章 CRUD
│   │   │   ├── taxonomy.py  # 分类 & 标签管理
│   │   │   ├── comments.py  # 评论管理 + 审核接口
│   │   │   ├── upload.py    # 图片上传
│   │   │   └── settings.py  # 动态博客设置
│   │   ├── core/
│   │   │   ├── config.py    # 环境配置
│   │   │   ├── database.py  # SQLAlchemy 连接
│   │   │   └── security.py  # JWT 认证 + 密码哈希
│   │   ├── models/          # SQLAlchemy 数据模型
│   │   ├── schemas/         # Pydantic 校验模型
│   │   └── services/        # Markdown 渲染服务
│   ├── main.py              # FastAPI 应用入口
│   ├── requirements.txt
│   ├── blog_settings.json   # 动态设置（博客标题等）
│   └── blog.db               # SQLite 数据库（初始为空）
├── frontend/
│   ├── public/
│   │   ├── css/
│   │   │   ├── main.css     # 全局样式
│   │   │   └── admin.css    # 后台专用样式
│   │   ├── js/
│   │   │   ├── app.js       # 公共工具库（API 封装 / Auth / Toast）
│   │   │   └── admin.js     # 后台专用（动态侧边栏 / 登录检查）
│   │   └── img/             # 上传的图片目录（自动生成）
│   └── pages/
│       ├── index.html       # 博客首页（文章列表 + 侧边栏）
│       ├── post.html        # 文章详情页（Markdown 渲染 + 评论）
│       ├── archive.html     # 归档页面（按年/月分组 + 统计）
│       ├── login.html       # 登录页
│       ├── admin/           # 后台管理（需登录）
│           ├── dashboard.html      # 仪表盘（文章统计）
│           ├── editor.html         # Markdown 编辑器（双栏实时预览）
│           ├── posts.html          # 文章管理（分页/搜索/发布）
│           ├── taxonomy.html       # 分类 & 标签管理
│           ├── comments.html       # 评论管理（审核/删除）
│           └── settings.html       # 博客设置（标题/副标题/密码）
├── deploy/
│   ├── docker-compose.yml   # Docker Compose 配置
│   └── nginx.conf           # Nginx 反向代理配置
├── README.md                # 本文档
├── start.py                 # 一键启动脚本（自动安装依赖）
├── .env.example             # 环境变量示例文件
└── .gitignore
```

---

## 🔌 API 接口

所有 API 前缀为 `/api/v1`，完整交互文档见 [http://localhost:8000/docs](http://localhost:8000/docs)。

### 公共接口（无需认证）

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/info` | 博客元信息（标题/作者/自定义设置） |
| `GET` | `/posts` | 文章列表（支持 `?q=搜索词&page=1&tag=标签&category=分类`） |
| `GET` | `/posts/{slug}` | 文章详情（Markdown 渲染为 HTML） |
| `GET` | `/categories` | 分类列表（含文章数统计） |
| `GET` | `/tags` | 标签列表 |
| `GET` | `/posts/{slug}/comments` | 文章评论列表（已审核的） |
| `POST` | `/posts/{slug}/comments` | 发表新评论（自动进入待审核状态） |

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/auth/login` | 登录，返回 JWT token |
| `GET` | `/auth/me` | 获取当前用户信息 |
| `PUT` | `/auth/me` | 更新个人信息（邮箱/简介） |

### 管理员接口（需 Bearer Token）

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` `PUT` `DELETE` | `/posts[/{slug}]` | 文章 CRUD（需登录） |
| `POST` `DELETE` | `/categories[/{id}]` | 分类 CRUD |
| `POST` `DELETE` | `/tags[/{id}]` | 标签 CRUD |
| `POST` | `/upload/image` | 上传图片（支持 PNG/JPG/GIF） |
| `GET`  | `/settings` | 获取博客设置（自定义标题/副标题/页脚） |
| `PUT`  | `/settings` | 更新博客设置（需登录） |
| `PUT`  | `/settings/password` | 修改密码（需旧密码） |
| `GET`  | `/comments` | 获取所有评论（含未审核，分页） |
| `PUT`  | `/comments/{id}/approve?approved=true/false` | 审核评论（通过/驳回） |
| `DELETE` | `/comments/{id}` | 删除评论 |

---

## ⚙️ 配置说明

### 环境变量（backend/.env）

```env
# 博客信息
BLOG_TITLE=我的技术博客
BLOG_SUBTITLE=记录技术与思考
BLOG_AUTHOR=你的名字

# 管理员账户
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@example.com

# JWT 密钥（生产环境必须更换）
SECRET_KEY=随机字符串（32位以上）

# 数据库（默认 SQLite）
DATABASE_URL=sqlite:///./blog.db
```

### 动态博客设置

通过后台“设置”页面可以实时更新的配置（保存在 `backend/blog_settings.json`）：

- 博客标题
- 副标题
- 作者
- 页脚文本
- GitHub 链接
- ICP 备案号

这些设置会立即在 `/info` API 和前端导航栏生效。

---

## 🧪 测试

项目自带完整功能测试：

```bash
cd tech-blog/backend
python run_tests.py
```

测试包含：
- 所有页面 HTTP 200 ✅
- 登录/退出流程 ✅
- 文章 CRUD ✅
- 评论发表 + 审核 ✅
- 博客设置更新 ✅
- 图片上传 ✅
- 密码修改 ✅

---

## 🔧 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| **后端** | FastAPI | 高性能异步框架，自动生成 Swagger 文档 |
| **数据库** | SQLite | 轻量级，无需额外服务（可换 PostgreSQL） |
| **ORM** | SQLAlchemy | 数据库操作 |
| **模板引擎** | Python-Markdown + Pygments | Markdown 渲染 + 代码高亮 |
| **认证** | JWT + passlib | 安全登录 + 密码哈希 |
| **前端** | 原生 CSS + JavaScript | 无框架依赖，体积极小 |
| **容器化** | Docker + Docker Compose | 生产部署 |
| **Web服务器** | Uvicorn（开发） / Nginx（生产） | 高性能服务 |

---

## 🔄 更新日志

### v1.1（最新）
- ✅ 新增归档页面 `/pages/archive.html`（按年月分组 + 文章统计）
- ✅ 新增博客设置页面 `/admin/settings.html`（动态修改标题等）
- ✅ 新增评论审核功能（待审核状态 + 审核接口）
- ✅ 新增 `GET /comments` 管理接口（含未审核评论）
- ✅ 升级后台侧边栏为动态渲染（统一 admin.js 管理）
- ✅ 修复测试脚本中的参数错误
- ✅ 完善 README 文档 + 新 API 列表
- ✅ 36 项全功能测试通过 ✅

### v1.0
- ✅ 前后端分离架构
- ✅ 所有核心功能实现
- ✅ Docker 部署配置
- ✅ 一键启动脚本

---

## 📞 技术支持

1. **问题反馈**：检查浏览器控制台（F12 → Console）和 FastAPI 日志
2. **环境依赖**：确保 Python ≥3.9，pip 可正常使用
3. **权限问题**：上传目录 `frontend/public/img` 需可写权限
4. **生产部署**：请务必修改 `.env` 中的 `SECRET_KEY` 和 `ADMIN_PASSWORD`

---

## 🚧 未来规划

| 功能 | 状态 | 优先级 |
|------|------|--------|
| RSS 订阅（/api/v1/rss） | 待开发 | ⭐⭐ |
| 邮件通知（新评论） | 待开发 | ⭐⭐ |
| 全文搜索（Elasticsearch） | 待开发 | ⭐ |
| 图片 OSS 存储（腾讯云 COS） | 待开发 | ⭐ |
| 多用户/团队博客 | 待开发 | ⭐⭐⭐ |

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
