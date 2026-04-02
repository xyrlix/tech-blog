/**
 * TechBlog 前端公共工具库
 */

// ─── API 基础配置 ────────────────────────────────────────
const API_BASE = '/api/v1';

// ─── Token 管理 ──────────────────────────────────────────
const Auth = {
  getToken: () => localStorage.getItem('blog_token'),
  setToken: (t) => localStorage.setItem('blog_token', t),
  removeToken: () => localStorage.removeItem('blog_token'),
  getUser: () => { try { return JSON.parse(localStorage.getItem('blog_user') || 'null'); } catch { return null; } },
  setUser: (u) => localStorage.setItem('blog_user', JSON.stringify(u)),
  removeUser: () => localStorage.removeItem('blog_user'),
  isLoggedIn: () => !!localStorage.getItem('blog_token'),
  logout: () => { Auth.removeToken(); Auth.removeUser(); window.location.href = '/pages/index.html'; },
};

// ─── HTTP 请求封装 ────────────────────────────────────────
async function request(method, path, data = null, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  const token = Auth.getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const cfg = { method, headers };
  if (data && method !== 'GET') cfg.body = JSON.stringify(data);

  const url = path.startsWith('http') ? path : API_BASE + path;
  const res = await fetch(url, cfg);

  if (res.status === 204) return null;
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(json.detail || `HTTP ${res.status}`);
  return json;
}

const api = {
  get:    (path, q) => request('GET', path + (q ? '?' + new URLSearchParams(q) : '')),
  post:   (path, d) => request('POST', path, d),
  put:    (path, d) => request('PUT', path, d),
  delete: (path)    => request('DELETE', path),
};

// ─── Toast 通知 ───────────────────────────────────────────
function showToast(msg, type = 'info', duration = 3000) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
}

// ─── 日期格式化 ───────────────────────────────────────────
function formatDate(str) {
  if (!str) return '';
  const d = new Date(str);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

function timeAgo(str) {
  if (!str) return '';
  const diff = (Date.now() - new Date(str)) / 1000;
  if (diff < 60) return '刚刚';
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`;
  if (diff < 2592000) return `${Math.floor(diff / 86400)} 天前`;
  return formatDate(str);
}

// ─── URL 参数 ────────────────────────────────────────────
function getParam(key) {
  return new URLSearchParams(window.location.search).get(key);
}

// ─── 渲染导航栏 ───────────────────────────────────────────
async function renderNavbar(activeLink = '') {
  let info = {};
  try { info = await api.get('/info'); } catch {}

  const navbar = document.getElementById('navbar');
  if (!navbar) return;

  navbar.innerHTML = `
    <a class="brand" href="/pages/index.html"><span>${info.title || 'TechBlog'}</span></a>
    <nav>
      <a href="/pages/index.html" class="${activeLink === 'home' ? 'active' : ''}">首页</a>
      <a href="/pages/archive.html" class="${activeLink === 'archive' ? 'active' : ''}">归档</a>
      <div class="search-box">
        <span class="icon">🔍</span>
        <input type="text" id="searchInput" placeholder="搜索文章..." />
      </div>
      ${Auth.isLoggedIn()
        ? `<a href="/pages/admin/dashboard.html">后台</a>
           <a href="#" onclick="Auth.logout();return false;">退出</a>`
        : `<a href="/pages/login.html">登录</a>`
      }
    </nav>
  `;

  // 搜索回车
  const si = document.getElementById('searchInput');
  if (si) {
    si.addEventListener('keydown', e => {
      if (e.key === 'Enter' && si.value.trim()) {
        window.location.href = `/pages/index.html?q=${encodeURIComponent(si.value.trim())}`;
      }
    });
  }
}

// ─── 渲染侧边栏 ───────────────────────────────────────────
async function renderSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;

  let cats = [], tags = [];
  try { [cats, tags] = await Promise.all([api.get('/categories'), api.get('/tags')]); } catch {}

  sidebar.innerHTML = `
    <div class="widget">
      <div class="widget-header">📁 分类</div>
      <div class="widget-body">
        <ul class="cat-list">
          ${cats.map(c => `
            <li>
              <a href="/pages/index.html?category=${c.slug}">${c.name}</a>
              <span class="count">${c.post_count}</span>
            </li>`).join('') || '<li style="color:var(--text-muted);font-size:.85rem;">暂无分类</li>'}
        </ul>
      </div>
    </div>
    <div class="widget">
      <div class="widget-header">🏷️ 标签</div>
      <div class="widget-body">
        <div class="tag-cloud">
          ${tags.map(t => `<a href="/pages/index.html?tag=${t.slug}">${t.name}</a>`).join('') || '<span style="color:var(--text-muted);font-size:.85rem;">暂无标签</span>'}
        </div>
      </div>
    </div>
  `;
}

// ─── 渲染分页 ─────────────────────────────────────────────
function renderPagination(container, pagination, onPage) {
  if (!container || !pagination || pagination.pages <= 1) return;
  const { page, pages } = pagination;
  const btns = [];
  btns.push(`<button ${page === 1 ? 'disabled' : ''} onclick="(${onPage})(${page - 1})">‹ 上一页</button>`);
  for (let i = 1; i <= pages; i++) {
    if (i === 1 || i === pages || Math.abs(i - page) <= 2) {
      btns.push(`<button class="${i === page ? 'active' : ''}" onclick="(${onPage})(${i})">${i}</button>`);
    } else if (Math.abs(i - page) === 3) {
      btns.push(`<button disabled>…</button>`);
    }
  }
  btns.push(`<button ${page === pages ? 'disabled' : ''} onclick="(${onPage})(${page + 1})">下一页 ›</button>`);
  container.innerHTML = btns.join('');
}

// ─── 构建文章卡片 HTML ────────────────────────────────────
function buildPostCard(post) {
  const coverEl = post.cover
    ? `<img class="cover" src="${post.cover}" alt="${post.title}" loading="lazy">`
    : `<div class="cover-placeholder">📝</div>`;
  const tags = (post.tags || []).map(t => `<span class="tag-badge">${t.name}</span>`).join('');
  const topBadge = post.is_top ? '<span class="top-badge">置顶</span>' : '';
  const cat = post.category ? `<span>📁 ${post.category.name}</span>` : '';

  return `
    <div class="post-card">
      ${coverEl}
      <div class="info">
        <div class="post-title">
          ${topBadge}
          <a href="/pages/post.html?slug=${post.slug}">${post.title}</a>
        </div>
        <div class="summary">${post.summary || ''}</div>
        <div class="meta">
          ${cat}
          <span>📅 ${formatDate(post.created_at)}</span>
          <span>👁 ${post.views}</span>
          ${tags}
        </div>
      </div>
    </div>`;
}

window.Auth = Auth;
window.api = api;
window.showToast = showToast;
window.formatDate = formatDate;
window.timeAgo = timeAgo;
window.getParam = getParam;
window.renderNavbar = renderNavbar;
window.renderSidebar = renderSidebar;
window.renderPagination = renderPagination;
window.buildPostCard = buildPostCard;
