"""API 功能测试脚本"""
import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from main import app, _init_db

# 确保数据库已初始化
_init_db()

client = TestClient(app)

def test():
    errors = []

    # 1. 博客信息
    r = client.get('/api/v1/info')
    assert r.status_code == 200, f"info failed: {r.text}"
    info = r.json()
    print(f"[OK] GET /info -> title={info['title']}")

    # 2. 分类列表
    r = client.get('/api/v1/categories')
    assert r.status_code == 200
    cats = r.json()
    print(f"[OK] GET /categories -> {len(cats)} 个分类")

    # 3. 标签列表
    r = client.get('/api/v1/tags')
    assert r.status_code == 200
    tags = r.json()
    print(f"[OK] GET /tags -> {len(tags)} 个标签")

    # 4. 登录
    r = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
    assert r.status_code == 200, f"login failed: {r.text}"
    token = r.json()['access_token']
    print(f"[OK] POST /auth/login -> token obtained")

    headers = {'Authorization': f'Bearer {token}'}

    # 5. 新建文章
    content = "## 欢迎\n\n这是我的第一篇博客！\n\n```python\nprint('Hello, Blog!')\n```"
    r = client.post('/api/v1/posts', json={
        'title': 'Hello, TechBlog!',
        'content': content,
        'is_published': True,
        'tag_ids': [1] if tags else [],
    }, headers=headers)
    assert r.status_code == 201, f"create post failed: {r.text}"
    post_slug = r.json()['slug']
    print(f"[OK] POST /posts -> slug={post_slug}")

    # 6. 文章列表
    r = client.get('/api/v1/posts')
    assert r.status_code == 200
    total = r.json()['pagination']['total']
    print(f"[OK] GET /posts -> {total} 篇文章")

    # 7. 文章详情
    r = client.get(f'/api/v1/posts/{post_slug}')
    assert r.status_code == 200
    print(f"[OK] GET /posts/{post_slug} -> views={r.json()['views']}")

    # 8. 发表评论
    r = client.post(f'/api/v1/posts/{post_slug}/comments', json={
        'nickname': '测试用户',
        'content': '第一条评论！',
    })
    assert r.status_code == 201
    print(f"[OK] POST /comments -> id={r.json()['id']}")

    # 9. 获取评论
    r = client.get(f'/api/v1/posts/{post_slug}/comments')
    assert r.status_code == 200
    print(f"[OK] GET /comments -> {len(r.json())} 条评论")

    # 10. 更新文章
    r = client.put(f'/api/v1/posts/{post_slug}', json={'is_top': True}, headers=headers)
    assert r.status_code == 200
    print(f"[OK] PUT /posts/{post_slug} -> is_top={r.json()['is_top']}")

    print()
    print("=" * 50)
    print("  ALL 10 TESTS PASSED!")
    print("=" * 50)


if __name__ == '__main__':
    test()
