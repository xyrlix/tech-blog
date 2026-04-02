#!/usr/bin/env python
"""一键启动脚本（本地开发用）"""
import subprocess, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, "backend")

print("=" * 50)
print("  TechBlog 启动中...")
print("=" * 50)

# 检查依赖
print("\n[1/2] 安装 Python 依赖...")
subprocess.run([sys.executable, "-m", "pip", "install", "-r",
                os.path.join(BACKEND, "requirements.txt"), "-q",
                "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"], check=True)

# 启动服务
print("\n[2/2] 启动 FastAPI 服务...")
print("\n访问地址：")
print("  博客首页:  http://localhost:8000/pages/index.html")
print("  后台管理:  http://localhost:8000/pages/admin/dashboard.html")
print("  API 文档:  http://localhost:8000/docs")
print("  默认账号:  admin / admin123\n")

os.chdir(BACKEND)
os.execv(sys.executable, [sys.executable, "-m", "uvicorn", "main:app",
                           "--host", "0.0.0.0", "--port", "8000", "--reload"])
