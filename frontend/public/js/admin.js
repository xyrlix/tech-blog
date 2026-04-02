/**
 * TechBlog 后台公共工具
 */

/**
 * 检查登录，未登录跳转
 */
function requireLogin() {
  if (!Auth.isLoggedIn()) {
    window.location.href = '/pages/login.html';
    return false;
  }
  return true;
}

/**
 * 渲染后台侧边栏
 * @param {string} active - 当前激活项: dashboard | posts | editor | taxonomy | comments | settings
 */
async function renderAdminSidebar(active = '') {
  const el = document.getElementById('adminSidebar');
  if (!el) return;

  const user = Auth.getUser();
  const username = user?.username || 'Admin';
  const avatar = username[0].toUpperCase();

  // 获取博客标题
  let title = 'TechBlog';
  try { const info = await api.get('/info'); title = info.title || title; } catch {}

  const links = [
    { key: 'dashboard', icon: '📊', label: '仪表盘', href: 'dashboard.html' },
    { key: 'posts',     icon: '📝', label: '文章管理', href: 'posts.html' },
    { key: 'editor',    icon: '✏️', label: '写文章',   href: 'editor.html' },
    { key: 'taxonomy',  icon: '🏷️', label: '分类 & 标签', href: 'taxonomy.html' },
    { key: 'comments',  icon: '💬', label: '评论管理', href: 'comments.html' },
    { key: 'settings',  icon: '⚙️', label: '博客设置', href: 'settings.html' },
  ];

  el.innerHTML = `
    <div class="logo">⚡ <span>${title}</span></div>
    <nav>
      ${links.map(l => `
        <a href="${l.href}" class="${l.key === active ? 'active' : ''}">
          <span class="nav-icon">${l.icon}</span>${l.label}
        </a>`).join('')}
    </nav>
    <div class="admin-user">
      <div class="avatar">${avatar}</div>
      <div>
        <div style="font-weight:600;font-size:.88rem">${username}</div>
        <div style="display:flex;gap:8px;margin-top:2px">
          <a href="/pages/index.html" style="font-size:.78rem;color:#8b949e">查看博客</a>
          <a href="#" onclick="Auth.logout();return false" style="font-size:.78rem;color:#f85149">退出</a>
        </div>
      </div>
    </div>
  `;
}

window.requireLogin = requireLogin;
window.renderAdminSidebar = renderAdminSidebar;
