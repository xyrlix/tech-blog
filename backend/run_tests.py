"""完整功能测试脚本"""
import sys, os, io, json
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from main import app, _init_db

# 清理测试残留（跳过占用中的文件）
for f in ['blog_settings.json', 'blog.db']:
    try:
        if os.path.exists(f):
            os.remove(f)
    except Exception:
        pass

_init_db()
client = TestClient(app)

results = []

def test(name, cond, detail=''):
    status = 'PASS' if cond else 'FAIL'
    results.append((status, name, detail))
    mark = 'v' if cond else 'X'
    msg = f'[{mark}] {name}'
    if detail:
        msg += f' | {detail}'
    print(msg)

# === Pages ===
pages = [
    ('/pages/index.html',           'index'),
    ('/pages/post.html',            'post'),
    ('/pages/archive.html',         'archive'),
    ('/pages/login.html',           'login'),
    ('/pages/admin/dashboard.html', 'admin/dashboard'),
    ('/pages/admin/posts.html',     'admin/posts'),
    ('/pages/admin/editor.html',    'admin/editor'),
    ('/pages/admin/taxonomy.html',  'admin/taxonomy'),
    ('/pages/admin/comments.html',  'admin/comments'),
    ('/pages/admin/settings.html',  'admin/settings'),
]
for path, name in pages:
    r = client.get(path)
    test(f'Page: {name}', r.status_code == 200, f'HTTP {r.status_code}')

# === Static ===
for path, name in [('/css/main.css','main.css'), ('/js/app.js','app.js'), ('/js/admin.js','admin.js')]:
    r = client.get(path)
    test(f'Static: {name}', r.status_code == 200, f'HTTP {r.status_code}')

# === API basic ===
r = client.get('/api/v1/info')
test('API /info', r.status_code == 200, r.json().get('title',''))

r = client.get('/api/v1/posts?page=1&size=10')
test('API posts list', r.status_code == 200)

r = client.get('/api/v1/categories')
test('API categories', r.status_code == 200, str(len(r.json())) + ' items')

r = client.get('/api/v1/tags')
test('API tags', r.status_code == 200, str(len(r.json())) + ' items')

# === Auth ===
r = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'admin123'})
test('API login', r.status_code == 200)
token = r.json().get('access_token', '')
H = {'Authorization': f'Bearer {token}'}

r = client.get('/api/v1/auth/me', headers=H)
test('API GET /auth/me', r.status_code == 200, r.json().get('username'))

r = client.put('/api/v1/auth/me', json={'bio': 'tech blogger'}, headers=H)
test('API PUT /auth/me', r.status_code == 200)

# === Post CRUD ===
r = client.post('/api/v1/posts', json={
    'title': 'Test Post',
    'content': '# Hello\nThis is test content with enough length.',
    'is_published': True,
    'tag_ids': [],
    'category_id': None,
}, headers=H)
test('API create post', r.status_code in (200, 201), f'HTTP {r.status_code}')
post_slug = r.json().get('slug', '')

r = client.get(f'/api/v1/posts/{post_slug}')
test('API get post detail', r.status_code == 200, post_slug)

r = client.put(f'/api/v1/posts/{post_slug}', json={'title': 'Test Post (Updated)'}, headers=H)
test('API update post', r.status_code == 200)

# === Comments (Admin) ===
r = client.get('/api/v1/comments', headers=H)
test('API GET /comments (admin)', r.status_code == 200, f"total={r.json().get('total',0)}")

# create a comment for approve test (need published post)
r_post = client.post('/api/v1/posts', json={
    'title': 'Comment Test Post', 'content': 'content', 'is_published': True
}, headers=H)
ctest_slug = r_post.json().get('slug', '')
r_c = client.post(f'/api/v1/posts/{ctest_slug}/comments', json={
    'nickname': 'tester', 'content': 'hello'
})
cid = r_c.json().get('id', 0)
r = client.put(f'/api/v1/comments/{cid}/approve?approved=true', headers=H)
test('API approve comment', r.status_code == 200 and r.json().get('is_approved') == True)
r = client.put(f'/api/v1/comments/{cid}/approve?approved=false', headers=H)
test('API reject comment', r.status_code == 200 and r.json().get('is_approved') == False)
client.delete(f'/api/v1/posts/{ctest_slug}', headers=H)


r = client.post(f'/api/v1/posts/{post_slug}/comments', json={
    'nickname': 'visitor',
    'email': 'test@test.com',
    'content': 'Great article!'
})
test('API post comment', r.status_code in (200, 201), f'HTTP {r.status_code}')

r = client.get(f'/api/v1/posts/{post_slug}/comments')
test('API get comments', r.status_code == 200)

# === Settings ===
r = client.get('/api/v1/settings')
test('API GET /settings', r.status_code == 200, r.json().get('title'))

r = client.put('/api/v1/settings', json={'title': 'My New Blog Title'}, headers=H)
test('API PUT /settings', r.status_code == 200, r.json().get('title'))

r = client.get('/api/v1/info')
synced = r.json().get('title') == 'My New Blog Title'
test('API /info title sync', synced, r.json().get('title'))

# === Search ===
r = client.get('/api/v1/posts?q=Test')
test('API search posts', r.status_code == 200)

# === Upload ===
fake_img = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
r = client.post('/api/v1/upload/image',
    files={'file': ('test.png', io.BytesIO(fake_img), 'image/png')},
    headers=H)
test('API upload image', r.status_code == 200, r.json().get('url', ''))

# === Password change ===
r = client.put('/api/v1/settings/password',
    json={'old_password': 'admin123', 'new_password': 'newpass456'},
    headers=H)
test('API change password', r.status_code == 200)
# restore
r2 = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'newpass456'})
t2 = r2.json().get('access_token', '')
client.put('/api/v1/settings/password',
    json={'old_password': 'newpass456', 'new_password': 'admin123'},
    headers={'Authorization': f'Bearer {t2}'})
test('API restore password', r2.status_code == 200)

# === Delete ===
r = client.delete(f'/api/v1/posts/{post_slug}', headers=H)
test('API delete post', r.status_code in (200, 204), f'HTTP {r.status_code}')

# === Summary ===
fails = [x for x in results if x[0] == 'FAIL']
passes = [x for x in results if x[0] == 'PASS']
print()
print(f'====== Result: {len(passes)} PASS, {len(fails)} FAIL ======')
if fails:
    print('FAILED:')
    for _, name, detail in fails:
        print(f'  X {name}: {detail}')
else:
    print('ALL TESTS PASSED!')
