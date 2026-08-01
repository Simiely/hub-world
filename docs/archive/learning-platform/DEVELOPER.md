---
module: archive
title: DEVELOPER.md
tags: [learning-platform]
source:
  project: learning-platform
  repo: https://github.com/Simiely/learning-platform
  file: DEVELOPER.md
  branch: master
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/learning-platform/blob/master/DEVELOPER.md)

# 开发者文档 / Developer Guide

> 写给接手这个项目的开发者或 AI 助手。

## 项目概述

**Lets Learn** — 幼儿识字/认知闪卡平台。Django 6.0 + Alpine.js 3.14 + SQLite，专为 iPad / iPhone 触屏设计。

仓库：`github.com/Simiely/learning-platform`（分支：master）

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Django 6.0, Python 3.13+ |
| 前端 | Alpine.js 3.14.8（本地托管，不用 CDN）, 原生 CSS（CSS Variables） |
| 数据库 | SQLite（单文件，`db/db.sqlite3`，不进 git） |
| 生产服务器 | gunicorn（仅 Docker 内使用） |
| 音频素材 | 预生成并随仓库提交（中文/英文/科普 三套 mp3） |
| 图像处理 | Pillow, NumPy, OpenCV headless |
| 拼音排序 | pypinyin |
| 容器化 | Docker + GitHub Actions（自动构建推送 ghcr.io） |

## 项目结构

```
learning-platform/
├── apps/core/                  # 核心应用
│   ├── data/                   # ⭐ 全部分类数据单一来源
│   │   ├── __init__.py         # CardItem dataclass + CATEGORIES 汇总（分类级配置）
│   │   ├── animals.py          # 动物分类（Animal，77 只，焦点已手工校准）
│   │   ├── fruits.py           # 果蔬分类（23 种，emoji 代替图片）
│   │   ├── vehicles.py         # 交通工具（20 种，emoji）
│   │   ├── dinosaurs.py        # 恐龙（16 种，emoji）
│   │   ├── space.py            # 太空（15 种，emoji）
│   │   ├── plants.py           # 花卉植物（16 种，emoji）
│   │   └── jobs.py             # 职业（16 种，emoji）
│   ├── models.py               # Category(含 groups 配置), Item, LearningProgress, QuizAttempt
│   ├── views.py                # 视图 + API（复用 services）
│   ├── services.py             # 公共业务逻辑（拼音排序/首字母/进度记录）
│   ├── image_utils.py          # emoji 取色 + 图片焦点检测
│   ├── tests/                  # 40 个单元/视图测试
│   └── management/commands/
│       ├── seed_data.py        # 全量重建（清空旧数据，仅首启/测试用）
│       ├── seed_sync.py        # 增量同步（Docker 部署安全，可补写缺失音频）
│       ├── sync_positions.py   # 同步图片焦点到数据库
│       ├── detect_centers.py   # OpenCV 自动检测焦点（不要用 --force）
│       └── check_data.py       # 校验 DB / 媒体 / data/ 三方一致
├── apps/users/                 # 用户模块（登录/注册/统计）
├── config/                     # Django 配置
├── templates/                  # 9 个 HTML 模板
│   ├── base.html               # 公共布局
│   ├── index.html              # 首页
│   ├── category_browse.html    # 浏览模式 + 分组 Tabs（逻辑在 static/js/browse.js）
│   ├── category_cards.html     # 卡片模式（逻辑在 static/js/cards.js）
│   ├── category_quiz.html      # 练习模式（逻辑在 static/js/quiz.js）
│   ├── browse_popup.html       # 浏览弹窗
│   └── login/register/profile.html
├── static/
│   ├── css/                    # 13 个 CSS（含 1 个 DEPRECATED）
│   │   ├── theme.css           # 设计令牌 + 主题
│   │   ├── layout.css          # 导航栏 + 模式栏
│   │   ├── buttons.css         # 按钮系统
│   │   ├── utils.css           # 工具类
│   │   └── ...                 # 各页面独立 CSS
│   └── js/
│       ├── alpine.min.js       # Alpine.js（本地！不用 CDN）
│       ├── ipad-detect.js      # iPad 焦点检测
│       ├── audio-player.js     # 音频播放 + 自动连播
│       ├── image-zoom.js       # 图片缩放/拖拽
│       ├── confetti.js         # 礼花特效 + Web Audio 音效
│       ├── browse.js           # 浏览模式（tiles/分组/字母区块/已看）
│       ├── cards.js            # 卡片模式（翻卡/随机/缩放）
│       ├── quiz.js             # 练习模式（Alpine 组件）
├── media/                      # 图片 + 音频（77 只动物，进 git）
├── ANIMALS.md                  # 动物数据展示表（代码主源是 apps/core/data/animals.py）
├── DEV.md                      # 开发笔记（踩坑记录）
├── ADD_ANIMALS_GUIDE.md        # 新增动物操作指南
├── TODO.md                     # 待办与已定决策
├── Dockerfile
├── docker-entrypoint.sh        # 已集成 check_data 校验步骤
├── docker-compose.yml          # ⚠️ 部署前需改数据卷路径
└── requirements.txt
```

> 旧版单文件 `static/css/style.css`、`static/js/utils.js` 已在 2026-07-31 模块化重构中删除，无需处理。

## 数据模型

### Category
| 字段 | 类型 | 说明 |
|------|------|------|
| name | CharField | 分类名（如"动物"） |
| slug | SlugField | URL 标识，唯一 |
| icon | CharField | emoji 图标 |
| description | TextField | 描述 |
| sort_order | IntegerField | 排序 |

### Item（核心模型）
| 字段 | 类型 | 说明 |
|------|------|------|
| name | CharField | 中文名 |
| code | CharField | 唯一标识，格式 `english_lower_YYYYMMDDNN` |
| english_name | CharField | 英文名 |
| emoji | CharField | emoji 字符 |
| fact | TextField | 科普知识 |
| image | ImageField | 图片文件 |
| image_position | CharField | iPhone 竖屏焦点，如 `"56% 28%"` |
| image_position_ipad_portrait | CharField | iPad 竖屏焦点 |
| image_position_ipad_landscape | CharField | iPad 横屏焦点 |
| audio | FileField | 中文语音 |
| audio_en | FileField | 英文语音 |
| audio_fact | FileField | 科普语音 |
| group | CharField | 浏览分组（farm/wild/ocean/reptile） |
| sort_order | IntegerField | 排序 |

### LearningProgress / QuizAttempt
学习进度和测验记录模型，关联 User 和 Item，用于已登录用户的学习追踪。

---

## 核心路由

| 路由 | 视图 | 说明 |
|------|------|------|
| `/` | index_view | 首页 |
| `/category/<slug>/` | category_browse_view | 浏览模式（支持 `?letters=zh\|en` 区块） |
| `/category/<slug>/cards/` | category_cards_view | 卡片模式 |
| `/category/<slug>/quiz/` | category_quiz_view | 练习模式 |
| `/api/quiz/<slug>/question/` | quiz_question_api | 练习出题 API |
| `/api/quiz/<slug>/submit/` | quiz_submit_batch | 提交成绩 |
| `/api/mark-viewed/<id>/` | mark_viewed | 标记已查看 |

---

## 关键设计决策

### 为什么 Alpine.js 要本地托管
Safari 智能追踪防护会阻止 CDN 的 Alpine.js 访问 localStorage，导致卡顿。本地托管同域不触发防护。

### 为什么不用 `<button>` 做"再来一次"
iOS Safari 对 `<button>` 元素有渲染偏差。用 `<span>` 复用 badge 盒模型解决。

### 图片焦点（三套系统）
每张图片支持三套独立焦点：`image_position`（iPhone）、`image_position_ipad_portrait`（iPad 竖屏）、`image_position_ipad_landscape`（iPad 横屏）。均在 `apps/core/data/` 中手动校准，标记 `image_position_checked=True`，`detect_centers --force` 不会覆盖。

### 图片规则
- **不裁剪**，保持原始比例（App 用 `object-fit: cover` + 焦点适配）
- 长边 ≥ 3000px
- 动物面部清晰可见

### Docker 媒体同步
- 镜像自带 `/app/media-bundled`（`.dockerignore` 不排除 `media/`）
- 每次启动 `rsync -ac` 检查同步到数据卷
- `sync_positions` 同步图片焦点

---

## 数据修改规则

### ⚠️ 铁律
**所有动物数据只能通过 `apps/core/data/` 修改，禁止直接操作数据库。**

### 修改流程
```bash
# 1. 编辑 apps/core/data/（改焦点、科普、新增动物等，Animal dataclass）
# 2. 同步到数据库
python manage.py seed_sync
# 3. 校验一致性（媒体文件 + DB + data/ 对齐）
python manage.py check_data
# 4. 重启服务（Django runserver 自动重载）
```

- `seed_sync` 用 `code` 字段做唯一键匹配，改名/换 emoji 不影响
- 永远不会删除已有数据，只增量更新或原地修改
- **不能用 `seed_data --force`**（会清空旧数据，Docker 环境会丢用户进度）
- `sync_positions` 只同步三套焦点字段，不碰其他数据

### Animal dataclass 结构（apps/core/data/animals.py，11 个字段）
```python
@dataclass(frozen=True)
class Animal:
    name: str                            # 中文名
    code: str                            # 唯一标识，如 'polar_bear_2026072401'
    english_name: str                    # 英文名
    emoji: str                           # emoji（无专属用 '⬛'）
    img_file: str                        # 图片文件名，如 'ant.jpg'
    audio_file: str                      # 音频基名，如 'ant.mp3'
    fact: str                            # 科普知识
    image_position: str                  # iPhone/通用焦点，如 '13% 47%'
    image_position_ipad_portrait: str    # iPad 竖屏，如 '23% 37%'
    image_position_ipad_landscape: str   # iPad 横屏，如 '23% 47%'
    group: str                           # farm/wild/ocean/reptile
```

### ✅ 字段结构改动（2026-07-31 多分类重构后）
全部条目数据统一在 `apps/core/data/` 目录维护（`__init__.py` 汇总 CATEGORIES，每分类一个数据文件），
`seed_data.py` / `seed_sync.py` / `sync_positions.py` / `check_data.py` / `gen_audio.py`
全部通过 `from apps.core.data import CATEGORIES` 遍历读取，用 `a.xxx` 属性访问。
**加新分类 = 新建一个数据文件 + 在 `__init__.py` 的 CATEGORIES 注册一行**；增删字段只需改数据文件一处。

分组可选值：`farm`（家里和农场）、`wild`（野生动物）、`ocean`（海洋动物）、`reptile`（爬虫和昆虫）

---

## 前端架构

### CSS 模块加载规则
| 文件 | 加载范围 | 内容 |
|------|---------|------|
| `theme.css` | 全局 | 设计令牌、深色/浅色/自动主题 |
| `layout.css` | 全局 | 导航栏、模式栏、发音按钮 |
| `buttons.css` | 全局 | 按钮系统 |
| `utils.css` | 全局 | 工具类 |
| `index.css` / `browse.css` / `popup.css` / `cards.css` / `quiz.css` / `auth.css` / `profile.css` / `zoom.css` | 各页面 | 页面专属样式 |

### JS 共享模块
| 模块 | 导出 | 用途 |
|------|------|------|
| `ipad-detect.js` | `iPadDetect.getImagePos()`, `.centerPos()` | iPad 焦点检测 + 卡片上偏 |
| `audio-player.js` | `AudioPlayer(el)` → `play(), stop(), playSequence()` | 音频播放 + 中→英自动连播 |
| `image-zoom.js` | `ImageZoom.init()` | 图片缩放/拖拽 |
| `confetti.js` | `Confetti.launch()`, `.playCorrectSound()`, `.playWrongSound()` | 礼花 + Web Audio 音效 |
| `browse.js` | `browseApp({slug, csrfToken, items, lettersEnabled, markViewedUrl, resetUrl})` | 浏览模式：分组过滤/字母区块（🀄拼音·🔤英文）/已看状态 |
| `cards.js` | `cardsApp({items, csrfToken, markViewedUrl})` | 卡片模式：翻卡/随机/缩放 |
| `quiz.js` | `quizApp({categorySlug, csrfToken, questionUrl, submitUrl, quizUrl, browseUrl})` | 练习模式：10 题问答/连播/提交 |

### 关键设计规则
- `ipad-detect.js` 在 `<head>` 中**同步加载**（无 `defer`）
- 页面逻辑 JS（browse/cards/quiz）在模板底部以 `xxxApp({...})` 初始化，配置项由模板内联传入
- **CSS/JS 版本号**：修改 CSS/JS 后更新模板中 `?v=YYYYMMDDx`，否则 Safari 强缓存不更新
- iPad 检测用 `screen.width >= 768`（物理像素），不用 `window.innerWidth`
- 每个函数声明末尾加分号：`function foo() { ... };`

### Safari 特殊处理
- 状态栏/刘海适配：`viewport-fit=cover` + `env(safe-area-inset-top)`
- 100vh 地址栏 Bug：用 JS 计算的 `--vh` 替代原生 `100vh`
- body 不设 `display: flex` + `min-height`（Safari bug）
- `<button>` 在 iOS 上有渲染偏差，精确对齐用 `<span>`

---

## 常见问题排查

| 现象 | 根因 | 解决 |
|------|------|------|
| 卡片崩，只显示 emoji | JS 缺少分号 或 `iPadDetect` 未加载 | 查 Console；确认 ipad-detect.js 在 head 同步加载 |
| 图片焦点不生效 | 前端没接 iPad 字段 | 使用 `iPadDetect.getImagePos()` |
| 发音按钮样式丢失 | 页面没加载对应 CSS 模块 | 确认 `.ph-*` 样式在 `layout.css` |
| 翻卡时音频串音 | `playSequence` 未取消旧序列 | 检查 `sequenceId` 机制 |
| 首次加载不发音 | 浏览器 autoplay 拦截 | 已加解锁逻辑，用户点屏幕即可 |
| Docker 部署后异常 | data/ 数据问题 | 跑 `manage.py check_data` 校验三方一致 |
| 音频 404 | 磁盘文件名与 DB 不一致 | seed_data 用 `_write_media_file()` 覆写 |
| CSS 改了不生效 | Safari 强缓存 | 更新模板 `?v=` 版本号 |
| 练习模式容器塌缩 | quiz.css 缺少全视口样式 | 确认 `.container-quiz` 含 `height: calc(var(--vh)*100-52px)` |
| 练习答题后音频混乱 | `playQuizAudio` 引用动态属性被覆盖 | 用闭包冻结题目快照 + `_quizSeqId` 防护 |
| 练习模式 layout 跳动 | `x-if` 条件渲染导致高度变化 | 改用 `x-show` + 固定 height |
| 图片焦点偏移 | `image_position` 校准值不准 | 改 data/ 条目后 `sync_positions` 或 `seed_data --force` |
| iPad 白变黑 | iPad 辅助功能「智能反转」| **不是 CSS bug**，不要改代码 |

---

## 本地环境

```bash
git clone https://github.com/Simiely/learning-platform.git
cd learning-platform
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data      # 首次全量写入
python manage.py runserver 0.0.0.0:8000
```

- 本地开发用 `seed_data`（全量写入）；Docker 部署走 `seed_sync`（增量同步），二者不要混用
- 网络走代理 `127.0.0.1:7890`，git 有时需要 `GIT_SSL_NO_VERIFY=1 git -c http.proxy=http://127.0.0.1:7890 push`

## Docker 部署

### 部署前必改
`docker-compose.yml` 中的数据卷路径，默认是作者 NAS 路径 `/mnt/usb2/...`，必须改为本地路径。

### 首次部署
```bash
docker compose up -d
```
容器启动自动执行：collectstatic → migrate → rsync 媒体 → seed_sync → 创建管理员 → gunicorn

### 更新部署
```bash
docker compose pull && docker compose up -d
```

### 部署地址
- 本地：`http://localhost:8000`
- Docker：`http://服务器IP:2511`
- Docker 数据：持久化在数据卷中

### Docker 构建
- 推送到 `master` 分支自动触发 GitHub Actions → 构建镜像 → 推送到 ghcr.io
- `cancel-in-progress: true`，同一分支多次推送只保留最后一次构建

---

## 文档索引

| 文件 | 用途 | 什么时候看 |
|------|------|-----------|
| `README.md` | 项目门面 / 快速上手 | 第一次接触项目 |
| `ANIMALS.md` | 动物数据展示表（77 只、焦点、批次） | 查动物信息 / 核对焦点 |
| `DEVELOPER.md`（本文） | 架构 / 数据模型 / 数据修改规则 / 前端架构 | 改代码前必读 |
| `ADD_ANIMALS_GUIDE.md` | 新增动物完整操作指南 | 要加动物时 |
| `DEV.md` | 开发笔记（详细踩坑历史） | 排错时 |
| `TODO.md` | 待办事项 + 已定决策 | 接手下一次任务时 |

> 文档与代码的对应关系：**动物数据以 `apps/core/data/` 为准**，ANIMALS.md 是它的展示版，
> 二者需保持一致；改完数据跑 `python manage.py check_data` 可自动校验。

---

## 关键问题速查

> 开发过程中踩过的坑，遇到类似问题优先查这里。

### 1. 音频播放间隔
中英文自动连播的间隔在 `static/js/audio-player.js` 第 54 行：`gapSeconds = 0.1`（100ms）。若想调整，直接改这个默认值。

### 2. Safari 100vh 地址栏 Bug
iOS Safari 的 `100vh` 包含地址栏高度，会导致底部被裁剪。修复方案三管齐下：
- JS 计算 `--vh`（`base.html` 行内脚本）
- CSS 使用 `height: calc(var(--vh, 1vh) * 100)`
- 监听 `pageshow` 事件处理 bfcache 恢复

### 3. CSS/JS 强缓存（Safari）
Safari 会强缓存 CSS/JS 文件。**每次修改后必须更新模板中的 `?v=YYYYMMDDx` 版本号**，否则修改不生效。

### 4. iPad 图片焦点检测
必须用 `screen.width >= 768`（物理像素）检测 iPad，**不能**用 `window.innerWidth`（Safari 竖屏会缩放）。
对应模块：`static/js/ipad-detect.js` → `iPadDetect.getImagePos(item)`。

### 5. JS 分号导致白屏
函数声明末尾**必须加分号**（`function foo() { ... };`），否则紧跟的 IIFE 会解析错误，导致整个页面 JS 崩溃。
典型报错：`(intermediate value)(...) is not a function`

### 6. Alpine.js 必须本地托管
Safari 智能追踪防护会阻止 CDN 域（如 cdn.jsdelivr.net）的 Alpine.js 访问 localStorage，导致页面卡死。
**不要用 CDN**，已本地托管在 `static/js/alpine.min.js`。

### 7. iOS Safari `<button>` 渲染偏差
iOS Safari 对 `<button>` 元素有底层渲染偏差，即使 CSS 完全一致，尺寸也和 `<span>` 不一样。
需要精确对齐时，用 `<span>` 替代 `<button>`（如"再来一次"按钮）。

### 8. 音频文件名随机后缀
`FileField.save()` 在目标文件已存在时会自动追加 `_<7位随机>` 后缀，导致 DB 路径与磁盘文件名不一致。
修复：`seed_data.py` 用 `_write_media_file()` 以规范纯名覆盖写入。

### 9. N+1 查询
`profile_view` 原循环对每个分类逐次查询 `LearningProgress`。已改用 `Count + filter=Q()` annotate 一次查询完成。

### 10. view_count 首次查看计数翻倍
`mark_viewed` 中 `get_or_create` 后判断 `if progress.id:` 永远为真。已改用 `created` 返回值 + `F('view_count') + 1` 原子递增。

### 11. edge-tts 替代 gTTS
沙箱环境走代理，gTTS 请求 Google API 被拦截。改用 `edge-tts`（Microsoft Edge 神经网络语音），调用 `speech.platform.bing.com` 可通代理。

### 12. 数据库字段迁移安全
- `RenameField` 安全（保留数据），但 seed_data 元组变量名必须同步更新
- 新增字段用 `RunPython` 做数据迁移比纯 `AlterField` 更安全

