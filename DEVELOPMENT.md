# Hub World · 开发文档

## 项目结构

```
hub-world/
├── index.html              # 主入口（单文件应用）
├── projects.json           # 项目数据（外部 JSON）
├── .nojekyll               # GitHub Pages 跳过 Jekyll
└── <project-name>/         # 各子项目目录（对应 path）
```

## 架构说明

### 单文件 SPA

`index.html` 包含两个视图：
- **`#viewWelcome`**：首页（标题 → 浮动卡片 → CTA）
- **`#viewCatalog`**：目录页（Masonry 网格 + 分类 tab）

视图切换通过 CSS `opacity / visibility / transform` 过渡实现。

### 数据流

```
projects.json  ──fetch──▶  DOMContentLoaded  ──▶  initFloatingCards()
                                                    renderCatalog()
                        │
                        └─ fetch 失败 ──▶ FALLBACK_PROJECTS（硬编码 fallback）
```

- 页面加载时通过 `fetch('projects.json')` 异步加载项目数据
- JSON 格式：`{ "_readme": "...", "projects": [...] }`
- 若 fetch 失败（如 `file://` 协议或用 GitHub Pages 缓存问题），自动使用 `FALLBACK_PROJECTS` 常量兜底
- `DOMContentLoaded` → fetch → 解析 → 初始化，均通过 Promise 链串行执行

### FALLBACK_PROJECTS 机制

```js
var FALLBACK_PROJECTS = [
    { name: '琅勃拉邦旅行计划', desc: '琅勃拉邦 5 日慢游 · 4 人双酒店定制', icon: '✈️', path: 'luang-prabang-trip', tags: ['旅行', '定制'], category: 'web' }
];

fetch('projects.json')
    .then(r => r.json())
    .then(data => { projects = data.projects || data; })
    .catch(() => { projects = FALLBACK_PROJECTS; })
    .then(() => { /* 初始化所有功能 */ });
```

Promise 链的关键设计：`.catch()` 后的 `.then()` 始终执行，确保初始化代码不会因数据加载失败而跳过。

## 分类系统

导航栏 tab 对应 `category` 字段：

| tab 值 | 显示名 | 说明 |
|--------|--------|------|
| `all` | 全部 | 显示所有项目 |
| `web` | 网页 | 网页类项目 |
| `tool` | 工具 | 工具类项目 |
| `design` | 设计 | 设计类项目 |

`renderCatalog(filterCat)` 通过 `getSortedProjects()` 按分类筛选，并按拼音排序。

## 样式定制

CSS 变量在 `:root` 中定义，主要可改：

| 变量 | 默认值（暗色） | 说明 |
|------|---------------|------|
| `--pink` | `#ff9292` | 强调色 |
| `--bg` | `#08080c` | 页面背景 |
| `--bg-card` | `#08080c` | 卡片背景（与页面同色） |
| `--text` | `#eee` | 主文字色 |
| `--text-muted` | `#888` | 次要文字色 |
| `--border` | `rgba(255,255,255,0.08)` | 卡片边框 |

**主题切换**：通过 `[data-theme="light"]` / `[data-theme="dark"]` 覆盖 `:root` 变量，存储在 `localStorage('hubworld-theme')`。

## 动画系统

### 首页进入动画（`activateHero`）

采用**三级级联延迟**，通过 CSS `transition-delay` 实现错落效果：

```js
function activateHero() {
    $('titleMain').classList.add('show');         // CSS delay: 0.35s
    $('heroSub').classList.add('show');            // CSS delay: 0.65s
    setTimeout(() => $('btnToCatalog').classList.add('show'), 850);  // 无 CSS delay
    setTimeout(() => $('liveClock').classList.add('show'), 650);     // 无 CSS delay
}
```

| 元素 | JS 触发 | CSS delay | 首次可见 |
|------|---------|-----------|---------|
| 标题 | 200ms | 0.35s | ~550ms |
| 副标题 | 200ms | 0.65s | ~850ms |
| 按钮 | 200ms + 850ms | 0s | ~1050ms |
| 时钟 | 200ms + 650ms | 0s | ~850ms |

### 浮动卡片漂移动画

- 6 张卡片从右向左持续漂移，溢出左侧后循环到右侧
- 通过 `requestAnimationFrame` 驱动，每帧 `leftPct -= 0.018`
- 响应式：`activeCount` 根据容器宽高比切换（3/4/6 张）
- 鼠标 parallax：`pointermove` 事件驱动微偏移

## 关键问题记录

### 🔴 问题 1：项目卡片不显示（2026-07-03）

**现象**：卡片在 DOM 中生成，debug 确认 `renderCatalog` 执行完毕且数据正确，但用户看不到卡片。

**根因分析**：
1. `.cat-card` 初始 `opacity: 0`，通过 `.cat-card.visible` 设为 `opacity: 1`
2. JS 中 `setTimeout(card.classList.add.bind(card, 'visible'), delay)` 添加 `.visible` 类
3. 但 `.cat-card.visible` 的 `opacity: 1` **未被浏览器正确应用**（疑似 CSS 类优先级或浏览器缓存特性导致）

**修复方式**：
- 将透明度控制从 CSS class 切换为 JavaScript **内联样式**直接设置
- `.cat-card` CSS 保留 `opacity: 0` 作为初始状态
- JS 中 `card.style.opacity = '0'` 初始化，`setTimeout(() => card.style.opacity = '1', delay)` 渐入
- 完全绕过 CSS 类继承和优先级问题

**经验教训**：
- 对于关键的视觉状态（opacity、display），优先使用内联样式而非 CSS class
- CSS class 在复杂页面中可能因特异性、加载顺序等原因失效
- 调试时区分"DOM 存在"和"视觉可见"是两个独立维度

### 🔴 问题 2：时钟动画出现时间错误（2026-07-03）

**现象**：时钟的进入动画远晚于预期，与其它元素不同步。

**根因分析**：
- CSS `.action-hint` 设置了 `transition-delay: 0.85s`
- JS `activateHero` 中也设置了 `setTimeout(..., 850)` 来添加 `.show` 类
- 导致**双重延迟**：`.show` 在 1050ms 时添加，但 CSS 过渡再等 850ms，实际可见约在 1900ms

**修复方式**：
- 移除 CSS 的 `transition-delay`（设为 `0s`）
- 将 JS 的 `setTimeout` 从 850ms 调整为 650ms（配合 `activateHero` 的 200ms 触发延迟，刚好在 850ms 开始动画）
- 确保每个元素的动画延迟只在一个地方控制

**经验教训**：
- CSS `transition-delay` 和 JS `setTimeout` 不要同时控制同一个动画的延迟
- 统一使用一个层级的延迟控制（要么纯 CSS，要么纯 JS）

### 🔴 问题 3：GitHub Pages 部署失败（多次）

**现象**：推送后 GitHub Pages 不自动部署或构建失败。

**根因**：
1. Pages 环境可能被误删，导致构建队列卡死
2. CDN 缓存 `max-age=600`（10 分钟），部署成功后用户可能看到旧版本

**修复/排查方式**：
- 通过 API 检查状态：`GET /repos/{owner}/{repo}/pages`
- 手动触发构建：`POST /repos/{owner}/{repo}/pages/builds`
- 推送空 commit 触发重新构建：`git commit --allow-empty -m "trigger rebuild"`
- 等待 CDN 缓存过期或使用 `?t={timestamp}` 参数绕过

## 部署

推送到 `main` 分支后，GitHub Pages 从根目录自动构建部署。  
访问地址：https://simiely.github.io/hub-world/

**部署排障命令**（需 GitHub Token）：

```bash
# 检查状态
curl -H "Authorization: token <TOKEN>" https://api.github.com/repos/Simiely/hub-world/pages

# 查看最近构建
curl -H "Authorization: token <TOKEN>" https://api.github.com/repos/Simiely/hub-world/pages/builds

# 手动触发构建
curl -X POST -H "Authorization: token <TOKEN>" https://api.github.com/repos/Simiely/hub-world/pages/builds
```

## 注意事项

- 子项目需放在对应 `path` 的子目录下（如 `luang-prabang-trip/`）
- `path` 值不要带前导 `/` 或尾部 `/`
- 分类 tab 的 `data-cat` 需与 `projects[].category` 一致
- `--bg-card` 和 `--bg` 相同（暗色 = `#08080c`），卡片靠 1px 边框区分
- 浮动卡片 `category` 为 `other` 的子项默认排在拼音排序末位
