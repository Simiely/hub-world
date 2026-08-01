---
module: archive
title: DEV.md
tags: [learning-platform]
source:
  project: learning-platform
  repo: https://github.com/Simiely/learning-platform
  file: DEV.md
  branch: master
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/learning-platform/blob/master/DEV.md)

# 开发笔记

记录开发过程中遇到的关键问题及解决方案。

> ⚠️ 2026-07-31 模块化重构后：**全部条目数据源是 `apps/core/data/` 目录**（`__init__.py` 汇总
> CATEGORIES + 每分类一个文件：animals.py 77 只 / fruits.py 23 / vehicles / dinosaurs / space / plants / jobs），
> 不再是 `seed_data.py` 的元组。本文档涉及"数据源/动物数量/文件结构"的旧表述已修正；
> 历史问题描述（Safari/iPad/音频等）仍有效，作为排错参考。

---

## 布局 & CSS

### 全屏布局

卡片和练习模式填满视口：`container` flex column + `height: calc(100vh - 52px)`，每层 `min-height: 0` 防止撑破。

### 图片焦点校准

- `image_utils.py` 用 OpenCV saliency 检测图片视觉重心，但检测的是整只动物的几何中心，不是脸部
- 所有 `image_position` 值已在 `apps/core/data/` 的 ANIMALS 列表手动校准，标记 `image_position_checked=True`
- **不要用 `detect_centers --force` 覆盖手调值**
- 卡片模板中 `centerPos()` 对纵向做 ×0.65 上偏补偿
- 修改焦点：改 `apps/core/data/` 中对应动物的 `'XX% YY%'`，然后 `sync_positions`（或 `seed_data --force`）

### 模式栏按钮对齐

**问题**：浏览/卡片/练习三个页面切换时，模式栏按钮位置跳动。

**根因**：
1. 浏览页多了「再来一次」按钮，总宽度 360px，iPhone 375px 下 `flex-wrap: wrap` 导致折行
2. 浏览页容器 `padding-top: 28px`，卡片/练习页 `container-card` 把容器 padding 归零 + mode-bar `padding-top: 16px`，顶部间距不一致

**修复**：
- 去掉 `.mode-bar` 的 `flex-wrap: wrap`
- `.container` 顶部 padding 从 28px 改为 16px，与卡片/练习的 mode-bar 顶部对齐

### `<button>` vs `<span>` 在 iOS Safari 的渲染差异（血泪教训）

**问题**：「再来一次」按钮的尺寸反复调整仍无法与 badge 对齐，iPhone 上明显偏大。

**排查过程**：逐条对比 CSS，font-size、padding、min-height、line-height、border、box-sizing 完全一致，但 `<button>` 仍比 `<span>` 宽/高几 px。

**根因**：iOS Safari 对 `<button>` 元素有底层渲染偏差，即使设置 `appearance: none`、`box-sizing: border-box`，实际渲染尺寸仍与 `<span>` 有细微差异。

**修复**：把「再来一次」从 `<button class="reset-btn">` 改为 `<span class="mode-badge mode-badge-reset">`，复用 badge 的盒模型，只覆写颜色。自此 iPad 和 iPhone 尺寸完美一致。

**教训**：需要跟相邻元素精确对齐时，优先使用相同元素类型（全部 `<span>` 或全部 `<a>`）。`<button>` 在 iOS 上是不可靠的。

### 图片圆角白边

**问题**：卡片模式图片圆角边缘有 1px 白边。

**根因**：`.card-img-area` 的渐变底色从 `border-radius` 圆角边缘透出。

**修复**：`.card-page .card-img-area` 设 `background: transparent`。

---

## 前端交互

### 浏览模式弹出卡改造

- 从单张 AJAX 加载改为一次传入全部 items JSON
- 新增前后翻页按钮 + 计数器（浮在图片上方 + 50% 透明度）
- 图片点击放大，支持滚轮/双指缩放 + 拖拽
- 去掉放大按钮和随机按钮

### 计数器浮层

浏览模式和卡片模式的计数器均使用绝对定位浮在图片上方：
```css
position: absolute; top: 10px; opacity: 0.5; pointer-events: none;
```
`pointer-events: none` 确保不阻挡图片点击缩放。

### 练习模式题目去重

- 同一轮 10 题内：Session 记录已出题目 ID，每题从剩余中抽取
- 跨轮次：上一轮的题目 ID 保留在 Session，新一轮优先排除
- 降级策略：可用题目不够时只排除本轮已出的

### 卡片模式随机起始

`var current = Math.floor(Math.random() * window.cardItems.length)`，每次打开卡片模式从随机位置开始。

---

## 数据 & 后端

### 种子数据（apps/core/data/）

- **2026-07-31 重构后**：动物数据统一在 `apps/core/data/`（`Animal` dataclass，**77 只**），
  `seed_data.py` / `seed_sync.py` / `sync_positions.py` / `gen_audio.py` 全部从它读取，不再各自维护
- 每只 11 字段：`(name, code, english_name, emoji, img_file, audio_file, fact, image_position, image_position_ipad_portrait, image_position_ipad_landscape, group)`
- `seed_data --force` 覆盖已有数据（清空重建）；生产/Docker 用 `seed_sync`（非破坏增量）
- `image_position_checked=True` 防止 `detect_centers` 覆盖手调值
- `check_data` 命令可校验 DB / 媒体 / apps/core/data/ 三方一致

### N+1 查询修复

`profile_view` 原循环对每个分类逐次查询 `LearningProgress`。改用 `Count + filter=Q()` annotate 一次查询完成。

### view_count 启动 bug

`item_detail_api` 中 `get_or_create` 后 `if progress.id:` 永远为真，导致首次查看就记为 2。改用 `created` 返回值 + `F('view_count') + 1` 原子递增。

---

## 安全

- 登录页 open redirect 加 `url_has_allowed_host_and_scheme` 校验
- `DEBUG` 默认 `False`，`SECRET_KEY` 强制环境变量
- `ALLOWED_HOSTS` 默认 `localhost`
- docker compose 密码改为环境变量
- 登出改为 POST 表单

---

## 音频

### 音频 404 根因

`FileField.save` 在目标文件已存在时自动追加 `_<7位随机>` 后缀 → DB 与磁盘文件名不一致。

**修复**：`seed_data.py` 改用 `_write_media_file()` 直接以规范纯名覆盖写入，清理随机后缀孤儿。

### gTTS 代理问题 → 改用 edge-tts（2026-07-24）

**问题**：沙箱网络走代理 `127.0.0.1:7890`，gTTS（Google Text-to-Speech）请求 Google 翻译 API 被代理拦截，连续超时。

**排查过程**：
1. 不设代理 → DNS 解析失败（沙箱无直连外网权限）
2. 设代理 → 部分请求能通但极不稳定，批量 20 只动物跑几分钟后随机断开
3. 尝试 `HTTP_PROXY` / `HTTPS_PROXY` 环境变量全部无效

**修复**：改用 **edge-tts**（Microsoft Edge 内置神经网络语音，调用 `cognitive.microsoft.com`）：
```python
import asyncio
from edge_tts import Communicate

async def gen():
    await Communicate('考拉', voice='zh-CN-XiaoxiaoNeural').save('audio/koala.mp3')
    await Communicate('Koala', voice='en-US-JennyNeural').save('audio_en/koala.mp3')
asyncio.run(gen())
```
- 不走 Google，代理可通，稳定快速
- 中文：`zh-CN-XiaoxiaoNeural`（自然女声）
- 英文：`en-US-JennyNeural`（美式女声）
- `pip install edge-tts` 即可使用

**教训**：沙箱环境优先使用不依赖 Google 的 TTS。edge-tts 走 Azure 流，对代理友好。

### iOS 进场自动播放被拦截

`setTimeout` 中 `play()` 脱离用户手势上下文 → `NotAllowedError`。已 `.catch` 静默处理，手动点击不受影响。

---

## CSS 深色模式

- 三态切换：深色(`data-theme=dark`) → 浅色(`data-theme=light`) → 自动(无属性，跟系统)
- 首次访问默认深色
- 所有颜色走 CSS 变量，不要硬编码
- `prefers-reduced-motion` 支持

---

## iPad / Safari 专用坑

### iPad「白变黑」= 智能反转

设置 → 辅助功能 → 显示与文字大小 → 智能反转。**不是 CSS bug**，不要改代码。

### Safari CSS 强缓存

`style.css` 必须带 `?v=` 版本号。

### `<button>` 渲染尺寸偏差

见上文「iOS Safari 渲染差异」一节。用 `<span>` 替代 `<button>` 解决。

### Safari Tracking Prevention 导致 CDN 脚本卡顿（2026-07-23）

**现象**：练习模式突然变得非常卡顿，控制台报 `Tracking Prevention blocked access to storage for https://cdn.jsdelivr.net/...alpinejs...`

**根因**：Safari 智能追踪防护阻止了 CDN 域的 Alpine.js 访问 localStorage/Web Storage，导致脚本执行挂起。

**修复**：将 Alpine.js 从 CDN 下载到 `static/js/alpine.min.js`，模板改用 `{% static 'js/alpine.min.js' %}`。同域静态文件不受追踪防护限制。

**教训**：关键 JS 库不要用 CDN，下载到项目本地托管更可靠。

### 练习模式按钮溢出裁剪（2026-07-23）

**现象**：「下一题」按钮贴边甚至超出可视范围，容器 `overflow: hidden` 裁剪底部。

**根因**：`quiz-feedback` 高度（70px）小于实际内容需求。内容 = padding(8) + 文字区(24px) + 按钮 margin(4px) + 按钮高度(~44px) + padding-bottom(8) = 88px。

**完整布局链**：
```
container-card (height: calc(100vh-52px), overflow:hidden)
  quiz-body (flex:1)
    quiz-round (flex:1, min-height:0)
      quiz-img (flex:1, min-height:0)
      quiz-options (flex:none, ~118px)
      quiz-feedback (flex:none, 必须 ≥ 88px)
```

**修复**：`quiz-feedback` 高度设为 90px，确保内容不溢出。任何高度调整需验证 `∑(flex:none) ≤ height(container-card)`。

### 练习答题后自动朗读（2026-07-23）

`selectAnswer()` 调用 `playQuizAudio()` → 播放中文音频 → 1s 后播放英文。
需要 API 返回 `audio_zh`、`audio_en` 字段，前端用 `<audio>` 元素播放。
`play()` 用 `.catch` 静默处理 iOS 自动播放拦截。

### 图片容器统一透明背景（2026-07-23）

`.popup-img`、`.card-img-area`、`.quiz-img` 全部设 `background: transparent`。
消除渐变底色从 `border-radius` 圆角边缘透出的 1px 白边。

### 练习结果大字报排版（2026-07-23）

- 显示「对了 X 个」，数字 64px，「对了」「个」28px
- 满分：「🎉 满分！太厉害了！」
- 6-9 个：「不错，继续加油」
- 结果区 `padding-top: 60px` 下移避免太靠上

### 答对礼花特效（2026-07-23）

纯 JS Canvas 粒子爆炸：80 颗彩色圆点从图片底部边缘为中心向四周炸开，带重力下坠 + 渐隐。
`launchConfetti()` 在 `selectAnswer` 答对时触发。

### Docker 部署媒体同步策略（2026-07-23）

**问题**：更新了种子数据中的图片焦点、替换了媒体文件（如鸭图），但 Docker 部署后不生效。

**根因分析**：
1. **图片焦点**：`seed_data` 只在数据库为空时运行，已有数据容器直接跳过 → `sync_positions` 命令每次启动从 seed_data 同步
2. **媒体文件**：之前 `ensure_media` 从 GitHub tarball 下载，已存在就跳过；且 `.dockerignore` 排除了 `media/`，镜像内没有媒体文件

**修复**：
- `.dockerignore` 去掉 `media/`，让镜像自带媒体
- Dockerfile 构建时 `cp` 一份 `/app/media-bundled`
- entrypoint 用 `rsync -ac` 从 bundled 同步到卷，checksum 比较只传变化文件
- 新增 `sync_positions` 命令，每次启动更新 image_position 字段

### 浏览弹窗自动发音（2026-07-23）

`showPopup()` → 300ms 后播中文 → 1300ms 后播英文，与卡片模式时序一致。
`playBrowseAudio` 播放前先 `pause()` + `removeAttribute('src')` 避免音频冲突。

### iPad 双击缩放禁用（2026-07-23）

viewport meta 加 `user-scalable=no`，阻止浏览器默认双击缩放。
应用内图片缩放（CSS transform）不受影响。

### Web Audio API 合成音效（2026-07-23）

答对/答错/翻卡音效用 Web Audio API OscillatorNode 合成，不需要额外音频文件。
- 答对：3个上升正弦波（C5-E5-G5），清脆悦耳
- 答错：正弦波 440Hz→300Hz 平滑下降，柔和提示
- AudioContext 在用户点击回调中创建，iOS 不会拦截

### Canvas 礼花在 iPad 上卡顿（2026-07-23）

**现象**：电脑流畅，iPad 卡顿。

**根因**：iPad Retina 屏 devicePixelRatio=2，canvas 没有适配 DPR。浏览器在后台做隐式缩放，消耗 GPU。

**修复**：canvas 尺寸 = 逻辑像素 × DPR（上限2），ctx.scale(dpr, dpr) 映射坐标。CSS 尺寸保持逻辑像素。

### 动物数据清单（2026-07-23，2026-07-31 更新）

**2026-07-31 重构后**：代码级主数据源是 `apps/core/data/`（`Animal` dataclass，77 只）。
`ANIMALS.md` 是它的**展示文档**（含全部焦点值），改数据时两者需保持一致。
修改动物内容（增减、科普、焦点）直接编辑 `apps/core/data/`。

**焦点调整工作流**（2026-07-24 优化，2026-07-31 更新）：
- 所有焦点都是基于中心 `50% 50%` 的相对偏移
- 修改 `apps/core/data/` → `python manage.py sync_positions`（只同步焦点）或 `seed_data --force`（全量）
- 服务不需要重启，刷新前端页面即可

### iPad / iPhone 双套图片焦点（2026-07-24）

**需求**：iPad 横/竖屏和 iPhone 竖屏的图片构图不同，需要各自独立的视觉焦点。

**实现**：
1. **模型** `Item` 新增 `image_position_ipad` 字段（`CharField, default='50% 50%'`）
2. **迁移** `0009_item_image_position_ipad`（makemigrations → migrate）
3. **API** `to_dict()` 和 `quiz_question_api()` 同时返回 `image_position` 和 `image_position_ipad`
4. **seed_data** 每个动物增加第 8 个参数（默认为 iPhone 焦点值）
5. **ANIMALS.md** 新增「焦点(iPad)」列

**注意**：前端尚未实现 iPad 检测切换。后期只需一行 JS `screenWidth >= 768` 选择对应字段即可。

### 中文文件名 → 英文重命名（2026-07-24）

**问题**：Windows 下用户拖入的文件名是中文（如 `北极熊.jpg`），需要批量改成英文。

**教训**：
- 不能用 Bash 的 `mv`（UTF-8 over Git Bash 处理中文文件名编码混乱）
- Bash 的 `rename` 命令不可用（需 Linux 的 util-linux 版本）
- **必须用 PowerShell**：
  ```powershell
  Rename-Item "北极熊.jpg" "polarbear.jpg"
  ```
  PowerShell 原生支持 Unicode 路径名，不会编码损坏。

### 新增 20 只动物的批量工作流（2026-07-24）

完整记录了一次批量添加 20 只动物的端到端流程：

**阶段 1：图片素材**
1. 从 Pexels 搜索页（`pexels.com/search/<animal>/`）批量提取 photo ID
2. 用 Python 下载 400px 缩略图到 `candidates/`
3. 用户逐个挑选，有时需要换搜索词（如蛇：不要特写 → 普通搜索）
4. 确定后下载高清原图（不 `?w=` 参数 = 原始分辨率）
5. 保存到 `media/images/`，清理 `candidates/`

**阶段 2：音频生成**
1. 安装 `edge-tts`（pip install edge-tts）
2. 异步批量生成 `audio/`（中文名）、`audio_en/`（英文名）、`audio_fact/`（科普）
3. 约 1-2 秒/个，20 只 × 3 = 60 个文件约 2 分钟

**阶段 3：数据整合**
1. `ANIMALS.md` 新增 20 行，标记 ✅
2. `seed_data.py` 追加 20 条元组
3. `python manage.py seed_data --force` 写入数据库
4. 手动校准图片焦点（用户反馈 → 调整值 → 重跑 seed_data）

**阶段 4：清理**
- 删除 `new-animals/` 临时目录
- 删除 `candidates/` 缩略图
- 删除调试脚本（`gen_audio.py` 等）

### 新增动物图片素材下载工作流（2026-07-24）

**流程**：缩略图挑选 → 用户选择 → 高清下载 → 入仓

1. **批量下载缩略图**（Pexels / Pixabay，免费商用）

   - 搜索关键词用**纯英文**（如 `polar-bear` 而非 `北极熊`）
   - 从 Pexels 搜索结果页 HTML 提取 photo ID（需 User-Agent 伪装）
   - 下载 400px 缩略图到 `new-animals/images/candidates/`

   ```python
   # Pexels 直接访问图片 CDN 不需要搜索页权限
   # 通过已知 photo ID 下载缩略图
   import urllib.request, ssl, io, os
   from PIL import Image
   ctx = ssl.create_default_context()
   ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
   handler = urllib.request.ProxyHandler({'https': 'http://127.0.0.1:7890'})
   opener = urllib.request.build_opener(handler, urllib.request.HTTPSHandler(context=ctx))

   for pid in photo_ids:
       url = f'https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=400'
       req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
       resp = opener.open(req, timeout=10)
       img = Image.open(io.BytesIO(resp.read()))
       img.save(f'new-animals/images/candidates/{label}.jpg')
   ```

2. **用户挑选后下载高清原图**
   ```python
   url = f'https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg'
   # 不加 w 参数 = 原始分辨率
   ```

3. **长边 ≥ 3000px，不裁剪，保持原始比例**

4. **清理候选项**

**注意**：
- Pexels 搜索页会 403，但图片 CDN（`images.pexels.com`）可以直接访问
- 沙箱网络问题用调试 Python：`C:\Users\2504\.workbuddy\binaries\python\versions\3.13.12\python.exe` + ProxyHandler
- 关键词必须英文，Pexels URL 用连字符（`polar-bear`）

---

## 数据安全 & 增量更新（2026-07-25）

### 问题背景

原有 `seed_data --force` 会删除全部数据重建，每次改动物信息（焦点、科普文字等）都要推倒重来。Docker 部署后用户进度丢失。

### 解决方案：code 唯一标识 + seed_sync

1. **模型层**：`Item` 新增 `code` 字段（格式 `english_lower_YYYYMMDDNN`，如 `polar_bear_2026072401`）
   - `unique=True`，改名/换 emoji 不影响匹配
   - 迁移 `0010_item_code` 用 `RunPython` 自动为已有动物生成 code

2. **数据同步层**：新增 `seed_sync` 命令
   - `update_or_create(category=cat, code=code, defaults={...})` — 用 code 做键
   - 翻新已在数据库的 → 原地更新；seed_data 里新增的 → 自动创建
   - **从不删除**已有数据

3. **部署**：Docker entrypoint 末尾跑 `python manage.py seed_sync`，每次启动/更新自动同步

### 教训

- 数据表必须有一个不依赖用户输入的稳定唯一键（code），依赖汉字匹配会随改名失效
- 元组解包顺序错误（`(code, name, ...)` vs `(name, code, ...)` 写反）导致中英文互换 → 数据库被污染
- 用 `RunPython` 做数据迁移比纯 `AlterField` 更安全

---

## 三套图片焦点系统（2026-07-25）

从 iPhone/iPad 双焦点升级为三焦点：

| 字段 | 用途 |
|------|------|
| `image_position` | iPhone 竖屏 |
| `image_position_ipad_portrait` | iPad 竖屏 |
| `image_position_ipad_landscape` | iPad 横屏 |

- 迁移 `0011` 用 `RenameField` 将旧 `image_position_ipad` → `image_position_ipad_portrait`，再 `AddField` 加横屏
- `to_dict()` 和 API 同时返回三个字段
- 前端后期用 `screen.width >= 768` + 方向检测选择对应值

### 教训

- Django 的 `RenameField` 是安全的（保留数据），但 seed_data.py 里的元组解包变量名必须同步更新
- 修改 seed_data.py 的元组结构（增字段）用正则替换极容易出错（引号、逗号、多行对齐）→ 宁可用 Edit 工具逐个改

---

## JavaScript IIFE 缺少分号导致全部 JS 崩溃（2026-07-25）

### 现象

卡片模式完全不工作：图片不显示（只显示 emoji），翻卡、缩放全部失效。F12 Console：

```
Uncaught TypeError: (intermediate value)(...) is not a function
```

### 根因

`closeZoom` 函数末尾的 `}` 后面**没有分号**，紧接着下一行是 zoom 的 IIFE：

```javascript
window.closeZoom = function(e) {
    // ...
}          // ← 缺少分号！
(function initZoom() { ... })();
```

JS 解析器把 `} (function initZoom(){})()` 当成 `undefined(function(){})()`，抛出 TypeError。**这一行错误导致整个 script 标签的后续代码全部终止**，`render()` 永远不会执行。

### 修复

```javascript
};     // ← 加分号
(function initZoom() { ... })();
```

### 教训

- IIFE 前必须确保上一语句已终止（`;` 不能省略）
- 在 `<script>` 标签中，一个 JS 错误会阻止后面所有代码执行
- `(intermediate value)(...) is not a function` 几乎总是缺少分号导致的 IIFE 解析错误

---

## iOS Safari 100vh Bug + bfcache 铺满失效（2026-07-25）

### 现象

iPad 竖屏浏览页面，第二次打开（从 bfcache 恢复）无法铺满屏幕，底部留白。旋转设备到横屏再转回竖屏后恢复正常。

### 根因

1. **iOS Safari 的 `100vh` 包含地址栏高度**，而地址栏的可见性会变化
2. **Safari bfcache（前进/后退缓存）** 恢复页面时使用缓存的旧 `100vh` 计算值，与实际视口不匹配
3. `.container` 的 `flex: 1` 在 `body` 非 flex 容器时无效

### 修复

三管齐下：

**JS 端**（`base.html` `<head>` 中）：
```javascript
function setViewportHeight() {
    var vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', vh + 'px');
}
setViewportHeight();
window.addEventListener('resize', setViewportHeight);
window.addEventListener('orientationchange', () => setTimeout(setViewportHeight, 100));
window.addEventListener('pageshow', e => { if (e.persisted) setViewportHeight(); });
```

**CSS 端**（`style.css`）：
```css
body {
    min-height: 100vh;                    /* 降级 */
    min-height: calc(var(--vh, 1vh) * 100);  /* 真值 */
    display: flex;
    flex-direction: column;
}
.container-card {
    height: calc(100vh - 52px);
    height: calc(var(--vh, 1vh) * 100 - 52px);
}
```

- `--vh` 由 JS 根据 `window.innerHeight` 实时计算
- `orientationchange` 加 `setTimeout(100)` 是因为 iOS 会在旋转动画完成后才更新 innerHeight
- `pageshow.persisted` 捕获 bfcache 恢复

### 教训

- 永远不要单独依赖 `100vh` 做 iOS 布局，用 `var(--vh, 1vh)` 做渐进增强
- `min-height: 100dvh` 是现代方案（iOS 15.4+），但老旧设备仍需 JS 降级
- `viewport-fit=cover` 对 iPad 全屏应用有帮助

---

## 全站 iPad 焦点检测（2026-07-25）

### 问题

三套焦点数据（iPhone / iPad 竖 / iPad 横）已入库，但前端始终读取 `image_position`（iPhone 值），iPad 焦点调整在页面上看不到效果。

### 检测逻辑

iPad 检测用 `screen.width >= 768`（物理像素，iPad 横屏 1366 / 竖屏 1024）：

```javascript
function getImagePos(it) {
    if (screen.width >= 768) {
        return (window.innerWidth > window.innerHeight)
            ? it.image_position_ipad_landscape || '50% 50%'
            : it.image_position_ipad_portrait || '50% 50%';
    }
    return it.image_position || '50% 50%';
}
```

### 涉及页面

| 页面 | 修改方式 |
|------|---------|
| 卡片模式 | 新增 `getImagePos()` 函数，替�� `centerPos()` 参数 |
| 练习模式 | Alpine 获取题目后，JS 替换 `currentQuestion.image_position` |
| 浏览弹窗 | 加载数据时判断设备，选对应焦点字段 |

### 教训

- `window.innerWidth` 在 iPad 竖屏常被夹到 ~375px（手机比例），不可靠；**必须用 `screen.width`**
- Alpine 的 `:style` 绑定不能调用复杂嵌套函数 → 在 JS 数据初始化阶段预处理

---

## 图片缩放拖拽（2026-07-25）

### 实现

放大后支持拖拽平移，组合 `translate + scale`：

```javascript
clone.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + scale + ')';
```

- 鼠标拖拽 → `mousedown/mousemove/mouseup` 计算偏移
- 单指拖拽 → `touchstart/touchmove/touchend`
- 双击 → 重置 `scale=1, tx=0, ty=0`
- 缩放回到 1 时自动归位置零

### 关闭大图的兼容

`<div onclick="closeZoom(event)">` 内部有 `.fs-zoom-wrap`（撑满全屏）和 `.fs-tip`，点击"空白"实际命中 wrap 而非 overlay。

修复：关闭判断扩展为匹配 `fs-zoom-wrap`、`fs-tip`、`fs-close`、overlay 自身 ID。

### 教训

- `e.target === e.currentTarget` 对内部有子元素全屏覆盖的场景不可靠
- 用子元素 ID / class 显式匹配比层级委托更可控

---

## Safari flex + min-height 兼容 bug（2026-07-25）

### 现象

练习模式容器高度不随设备/方向自适应，无法填满屏幕。

### 根因

bfcache 补丁给 `body` 加了 `display: flex; min-height: calc(var(--vh) * 100)`。Safari 对 flex 容器 + `min-height` 的组合有兼容 bug：子元素 `flex: 1` 不会正确扩展到 `min-height` 定义的高度，而是塌缩到内容高度。

### 修复

恢复 `body` 原始 CSS（无 flex），`container-card` 直接用 `height: calc(100vh - 52px)`。iOS 的 `100vh` 虽含地址栏，但在卡片/练习模式（全屏容器）下差值可接受。

### 教训

- **Safari flex + min-height 不要同时用**。要么 `height` + flex，要么 `min-height` + no flex。
- bfcache 修复只保留了 `<script>` 部分（后续可能需要），CSS 未引入 `--vh` 依赖。
- 跨浏览器测试前优先在 macOS/iPad Safari 验证。

---

## Alpine 响应式对象赋值（2026-07-25）

### 现象

练习模式 iPad 图片焦点不生效，始终显示 iPhone 焦点。

### 根因

```javascript
var q = this.currentQuestion;  // q 是原始对象引用
q.image_position = newPos;     // 直接写属性，不触发 Alpine 响应式
```

Alpine 3 的 Proxy 需要**通过 `this.xxx` 路径写入**才能触发依赖追踪。

### 修复

```javascript
this.currentQuestion.image_position = (screen.width >= 768)
    ? q.image_position_ipad_landscape
    : q.image_position_ipad_portrait;
```

### 教训

- Alpine 中修改嵌套对象属性必须通过代理路径：`this.currentQuestion.image_position = ...` ✅ | `var q = this.currentQuestion; q.image_position = ...` ❌
- 读取数据可以用局部变量，**写入必须走 this**

---

## AI 快速排错清单

开发时遇到问题，按以下顺序排查：

### 1. 页面白屏 / 卡片模式不工作

```bash
# 确认服务在跑
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/
# 确认模板编译无错
python manage.py shell -c "from django.template.loader import get_template; get_template('category_cards.html'); print('OK')"
# 检查 JS 语法：F12 Console 看红色报错
```

常见原因：
- JS 缺少分号 → `(intermediate value)(...) is not a function`
- IIFE 前无 `;` → 后续所有代码不执行
- Alpine:data 中 `this.xxx = ...` 写成 `var q = this.xxx; q.yyy = ...`

### 2. 图片不显示

```
# 检查图片是否存在
python -c "from apps.core.models import Item; [print(i.name, i.image) for i in Item.objects.all()[:3]]"
# 检查 JSON 数据
curl -s http://localhost:8000/category/animals/cards/ | grep -o '"image":"[^"]*"' | head -3
# 检查图片 URL
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/media/images/lion.jpg
```

### 3. 焦点调整不生效

```
# 确认 seed_data.py 改对了
python -c "
import ast
with open('apps/core/management/commands/seed_data.py') as f:
    tree = ast.parse(f.read())
# 检查对应动物的三组值
"
# 确认数据库已同步
python manage.py shell -c "
from apps.core.models import Item
i = Item.objects.get(code='hippo_2026072405')
print(i.image_position, i.image_position_ipad_portrait, i.image_position_ipad_landscape)
"
# 确认前端接了 iPad 检测（三个页面都要检查）
grep -l "getImagePos\|image_position_ipad\|screen.width >= 768" templates/*.html
```

### 4. Docker 部署异常

```bash
# 检查容器日志
docker compose logs learning-platform
# 确认 seed_sync 执行
docker compose exec learning-platform python manage.py shell -c "from apps.core.models import Item; print(Item.objects.count())"
# 应该输出 77
```

### 5. 本地开发环境

```bash
# 推荐运行命令
cd learning-platform
.venv/Scripts/python.exe manage.py runserver localhost:8000
# 改完 apps/core/data/ 后
.venv/Scripts/python.exe manage.py seed_sync
# 无需重启，Django dev server 自动重载
```

### 6. Git 推送失败（代理问题）

```bash
# 沙箱网络通过代理 127.0.0.1:7890
GIT_SSL_NO_VERIFY=1 git -c http.proxy=http://127.0.0.1:7890 -c https.proxy=http://127.0.0.1:7890 -c http.sslVerify=false push origin master
# TLS 连接错误时重试（代理偶发波动）
```

### 7. 页面布局塌缩

- Safari: body 不要 `display:flex` + `min-height` 同时用
- 卡片/练习: `.container-card` 保持 `height: calc(var(--vh, 1vh) * 100 - 52px)`，用 JS --vh 替代原生 100vh
- 所有全屏页面: `.mode-bar { flex: none }` + 内容区 `flex: 1; min-height: 0; overflow: hidden`

---

## iOS 状态栏 / 刘海 Safe Area 适配（2026-07-25）

### 现象

iPhone 刘海/灵动岛机型上，导航栏内容和弹窗关闭按钮被状态栏遮挡；iPad 上同样出现顶部元素超出一部分。卡片模式底部溢出。

### 根因分析

项目设置了 `viewport-fit=cover`（meta 标签）使页面扩展到屏幕物理边缘，但没有配套的 CSS `env(safe-area-inset-*)` 来避让安全区域。同时 `100vh` 在 iOS Safari 包含了地址栏高度，导致实际可用高度 > `100vh`。

完整时间线：
1. 提交 `f5d07fe` 引入了 `viewport-fit=cover` + JS `--vh` + body flex — 解决了 100vh bug
2. 提交 `5d58d73` 因 Safari flex+min-height bug 回退了 body flex 和 `var(--vh)`，容器回到 `calc(100vh - 52px)`
3. **问题**：`viewport-fit=cover` 仍在但失去配套 —— 状态栏/刘海遮挡 + 100vh 溢出同时出现

### 修复

三管齐下：

**CSS 端**（`style.css`）：
```css
:root {
    --safe-top: env(safe-area-inset-top, 0px);
    --safe-bottom: env(safe-area-inset-bottom, 0px);
}

/* 导航栏避让刘海/状态栏 */
.navbar { padding-top: var(--safe-top); }

/* 卡片/练习模式：用 JS --vh 替代 100vh（排除地址栏 + safe area） */
.container-card { height: calc(var(--vh, 1vh) * 100 - 52px); }

/* 弹窗关闭按钮避让 */
.popup-close { top: calc(14px + var(--safe-top)); }
.img-fs .fs-close { top: calc(20px + var(--safe-top)); }
```

**JS 端**（`base.html`，已有，无需修改）：
```javascript
function setViewportHeight() {
    var vh = window.innerHeight * 0.01;
    document.documentElement.style.setProperty('--vh', vh + 'px');
}
```

**关键原理**：
- `env(safe-area-inset-top)` → 系统提供的刘海/状态栏高度，非刘海设备为 0
- `var(--vh, 1vh) * 100` → `window.innerHeight`，iOS 上自动排除地址栏和安全区域
- 两者结合：navbar 推离刘海 + 容器高度用真实可见区域

**退化行为**：
- 桌面浏览器：`safe-area-inset-top = 0px`，`vh = 100vh`，无影响
- 无刘海 iPhone：`safe-area-inset-top = 20px`（状态栏），正常避让
- 有刘海 iPhone：`safe-area-inset-top = 59px`（灵动岛+状态栏），正常避让
- iPad：`safe-area-inset-top = 24px`，正常避让

### 教训

- `viewport-fit=cover` 必须配套 `env(safe-area-inset-*)`，只设 meta 不写 CSS 就会遮挡
- iOS 的 `100vh` 不可用于精确布局，用 `window.innerHeight` 的 JS 自定义属性
- body 的 `flex` + `min-height` 组合在 Safari 是毒药，保持 body 无 flex
- 修改布局链后要在 iPad/iPhone 真机上验证，桌面 Chrome DevTools 模拟不够准

### 快速排错

| 现象 | 可能原因 | 排查 |
|------|---------|------|
| 顶部被遮挡 | navbar 缺 safe-top padding | 检查 `.navbar` 是否有 `padding-top: var(--safe-top)` |
| 底部溢出 | container-card 用了 100vh 而非 var(--vh) | 检查 `.container-card` height 是否含 `var(--vh)` |
| 弹窗按钮被挡 | close 按钮 top 未加 safe-top | 检查 `.popup-close` / `.fs-close` top 值 |
| 非刘海设备也异常 | safe-top 变成了非 0 值 | 确认 `env()` 有 fallback `0px` |
| 桌面端布局变了 | 误改了 body CSS | 确认 body 仍无 flex/min-height |

---

## 练习模式音频逻辑修复（2026-07-26）

### 问题

练习模式答题后音频混乱：音效（答对滴滴答错下降音）和中文名称同时播放，听感不清。且快速连续答题时出现串音。

### 根因

`playQuizAudio()` 直接从 `this.currentQuestion` 读取数据。答题后 `this.current++`，用户点击"下一题"会改变 `this.currentQuestion`，导致延迟触发的音频播错了题目。

### 修复

两个关键改动：

1. **题目数据冻结**：`selectAnswer()` 中将当前题目保存到局部变量 `q`，传给 `playQuizAudio(q)`，而非依赖 `this.currentQuestion`。后续切换题目不影响本次播放。

2. **序列 ID 防护**（`_quizSeqId`）：每次调用 `playQuizAudio` 递增 ID，所有异步回调（probe `onReady`、英文 `setTimeout`）检查 ID 是否匹配，不匹配则丢弃。防止快速点击导致的串音。

3. 音效和中文**同时触发**——无延迟，天然交叠符合听觉预期。

### 关键代码

```javascript
selectAnswer(id) {
    // ...
    this.current++;
    this.playQuizAudio(this.currentQuestion);
},
playQuizAudio(q) {
    var self = this;
    this._quizSeqId = (this._quizSeqId || 0) + 1;
    var mySeqId = this._quizSeqId;
    // 所有异步回调检查 self._quizSeqId !== mySeqId → return
}
```

### 教训

- 异步音频播放中，不能用组件的动态属性（`this.currentQuestion`），必须用闭包冻结的快照
- 任何含 `setTimeout` 的音频序列都要加递增 ID 防止串音

---

## 练习模式容器适配（2026-07-26）

### 问题

模块化重构后，练习模式容器不再填满视口，高度塌缩。

### 根因

练习模式需要 `.container-card` 的全视口布局（`height: calc(var(--vh) * 100 - 52px)`），但这个类定义在 `cards.css` 中，练习页面只加载了 `quiz.css`。

### 修复

把全视口容器样式直接加到 `quiz.css` 的 `.container.container-quiz` 中，不再依赖 `cards.css`。模板中也移除 `container-card` 类，只用 `container-quiz`。

```css
.container.container-quiz {
    padding: 0 20px;
    height: calc(var(--vh, 1vh) * 100 - 52px);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}
```

### 教训

- CSS 文件拆分后，必须确保每个页面加载的 CSS 包含该页面所有的容器/布局样式
- 不要跨页面共享容器类（如 `container-card`），每个页面应有完整独立的容器定义

---

## 模块化重构记录（2026-07-26）

### 重构背景

原代码前端 JS 散落在 4 个模板文件中（650+ 行），高度重复；CSS 为单一 1174 行巨石文件。每次修改都需在多处同步更新。重构目标：消除重复代码、按页面拆分 CSS、提取共享 JS 模块。

### 模块化方案

**CSS**：拆分为 12 个文件（theme / layout / buttons / index / browse / popup / cards / quiz / auth / profile / zoom / utils），通过 `{% block extra_css %}` 按需加载。

**JS**：提取 4 个共享模块：
- `audio-player.js` — AudioPlayer 工厂函数，统一音频播放
- `image-zoom.js` — ImageZoom.init()，图片缩放/拖拽
- `ipad-detect.js` — iPadDetect.getImagePos() / .centerPos()
- `confetti.js` — Confetti 礼花 + 音效

### 踩坑：JS 加载时序

**问题**：重构后卡片模式报 `iPadDetect is not defined`。

**根因**：`ipad-detect.js` 在 `<body>` 底部用 `defer` 加载，但模板内联 `<script>` IIFE 在 HTML 解析阶段立即执行，比 `defer` 脚本更早。内联脚本引用了尚未定义的 `iPadDetect`。

**修复**：将 `utils.js` 和 `ipad-detect.js` 移到 `<head>` 中同步加载（无 `defer`），确保内联脚本执行前已可用。

**规则**：模板内联脚本直接引用的 JS 模块必须在 `<head>` 中同步加载。仅未被内联脚本引用的模块（如 `confetti.js`、`image-zoom.js`）可以 `defer`。

### 踩坑：CSS 归属错误

**问题**：发音按钮（`.ph-line`、`.ph-cell`、`.ph-sound`）样式在卡片模式下丢失。

**根因**：这些样式放在 `popup.css` 中，但卡片页面不加载 `popup.css`。

**修复**：将共享的发音按钮样式移到全局加载的 `layout.css`。

**规则**：模板重构时，逐一检查每个页面加载的 CSS 文件是否包含该页面使用的所有类名。最好做一个 CSS 类名 ↔ 模板的交叉对照。

### 踩坑：浏览器 autoplay 拦截

**问题**：`NotAllowedError: play() failed because the user didn't interact with the document first`。

**解决模式**：
```javascript
// 尝试播放
audio.play().catch(function(e) { console.log('Audio play error:', e); });
// 如果被拦截，绑定一次性解锁
document.addEventListener('click', function() { audio.play(); }, { once: true });
document.addEventListener('touchend', function() { audio.play(); }, { once: true });
```

用户首次点击/触摸屏幕后，浏览器解除 autoplay 限制，后续播放正常。

### 踩坑：快速翻卡时音频序列错乱

**问题**：快速连续翻页时，中文没读完就跳到英文，或上一页英文覆盖了当前页中文。

**根因**：每次 `playSequence` 创建的 `setTimeout` 未在下次调用时清除。

**修复模式**（`audio-player.js`）：
```javascript
var sequenceId = 0;
function cancelPending() {
    sequenceId++;  // 递增 ID 使旧回调失效
    if (enTimer) { clearTimeout(enTimer); enTimer = null; }
}
function playSequence(items, idx) {
    cancelPending();
    var mySeqId = sequenceId;
    // ... 所有异步回调中检查 sequenceId !== mySeqId 则 return
}
```

### 版本号管理

CSS 文件通过 `?v=YYYYMMDDx` 版本号绕过 Safari 强缓存。修改 CSS 后：
1. 更新 `base.html` 中全局加载的 CSS（theme/layout/buttons/utils）版本号
2. 更新各页面 `{% block extra_css %}` 中页面专属 CSS 版本号

### 最终文件清单（2026-07-31 更新）

| 类型 | 数量 | 文件 |
|------|------|------|
| CSS 模块 | 13 | theme, layout, buttons, utils, index, browse, popup, cards, quiz, auth, profile, zoom（+ style.css 已 DEPRECATED） |
| JS 模块 | 8 | ipad-detect, audio-player, image-zoom, confetti, browse, cards, quiz（+ alpine.min.js；utils.js 已 DEPRECATED） |
| 模板 | 9 | base, index, category_browse, category_cards, category_quiz, browse_popup, login, register, profile |

> 2026-07-31 第二次 JS 抽取：browse/cards/quiz 页面逻辑已从模板内联脚本移到独立 JS 文件，
> 模板只保留 `xxxApp({...})` 初始化调用；URL 均用 `{% url %}` 生成。

---

## 浏览模式分组 Tabs（2026-07-28）

### 需求

动物全部混在一个网格中，浏览时不方便查找。需要按类别分组显示。

### 方案选择

选择 **方案 B（顶部 Tabs 切换）**，仅修改浏览模式，不影响卡片和练习模式：

```
[ 全部 (77) | 🏠 家里和农场 (13) | 🌍 野生动物 (34) | 🌊 海洋动物 (14) | 🦎 爬虫和昆虫 (16) ]
```

点击 Tab 切换，网格自动显示/隐藏对应组的动物。
> 数量为 2026-07-31 第7批上线后的最新值（共 77 只）。
> 2026-07-31 更新：iPhone 窄屏下分组按钮默认只显示 emoji（全部按钮显示 emoji 数字如 7️⃣7️⃣），
> 点击选中按钮才展开文字。浏览页另有两个**互斥区块按钮**：🀄 = 拼音字母区块（?letters=zh）、
> 🔤 = 英文首字母区块（?letters=en，按英文名 A-Z 排序）；无参数 = 默认拼音排序、无区块；
> 再点已选中的按钮取消区块（回默认）；区块状态与分组过滤互不干扰（分组切换保留区块按钮选中态）。

### 零交叉分组设计

避免"企鹅既是鸟类又是海洋动物"式的交叉问题，按 **生活场景（在哪里见到）** 划分：

| 分组 | slug | 数量 | 划分逻辑 |
|------|------|------|---------|
| 🏠 家里和农场 | `farm` | 13 | 孩子日常能接触到的家养/农场动物 |
| 🌍 野生动物 | `wild` | 34 | 动物园或自然纪录片 |
| 🌊 海洋动物 | `ocean` | 14 | 海洋环境 |
| 🦎 爬虫和昆虫 | `reptile` | 16 | 小型爬行类和昆虫 |

### 关键决策点

- 企鹅 → 海洋动物（孩子脑海中关联南极/海洋/冰块，而非鸟类）
- 鹰/猫头鹰/鹦鹉 → 野生动物（在自然或动物园中见到）
- 鳄鱼 → 爬虫组（虽然凶猛，但生物学分类是爬行动物）
- 松鼠 → 野生动物（森林中见到）

### 实现

**后端改动**：

1. **`models.py`** — `Item` 模型新增 `group` 字段
   ```python
   GROUP_CHOICES = [
       ('farm', '🏠 家里和农场'),
       ('wild', '🌍 野生动物'),
       ('ocean', '🌊 海洋动物'),
       ('reptile', '🦎 爬虫和昆虫'),
   ]
   group = models.CharField(
       max_length=20, blank=True, default='',
       choices=GROUP_CHOICES, verbose_name='浏览分组'
   )
   ```
   `to_dict()` 新增 `"group": self.group or ""`

2. **`apps/core/data/animals.py`** — `Animal`（即共享 `CardItem`）含 11 字段，`group` 为第 11 位。77 只动物按组排列，方便维护（2026-07-31 重构：数据从 seed_data.py 元组迁移到 data.py dataclass，后又拆分为 data/ 多分类目录）

3. **`views.py`** — `category_browse_view` 新增 `group_counts` 统计和 `total` 传递给模板

**前端改动**：

4. **`category_browse.html`** — 在 `.mode-bar` 和 `.browse-grid` 之间插入 Tabs 栏。每个 `.b-tile` 加 `data-group` 属性。JS 过滤逻辑：
   ```javascript
   window.filterGroup = function(btn, group) {
       document.querySelectorAll('.group-tab').forEach(t => t.classList.remove('active'));
       btn.classList.add('active');
       document.querySelectorAll('.b-tile').forEach(tile => {
           tile.style.display = (group === 'all' || tile.dataset.group === group) ? '' : 'none';
       });
   };
   ```

5. **`browse.css`** — 新增胶囊按钮样式（`.group-tabs` 用 flex-wrap 自适应换行，`.group-tab` 选中态用 `--primary` 粉色）

---

## 2026-07-31 大版本 · 关键踩坑与经验

### 1. gen_audio.py 绝不能无参数全量跑
- 现象：全量跑重新生成所有分类音频，中途 edge-tts 网络抖动会留下 **0 字节损坏文件**（cat.mp3 / whale.mp3 实际被覆盖坏）
- 规则：永远 `python gen_audio.py --category <slug>` 限定分类；修复损坏文件用
  `gen_audio.py --category <slug> <base>` 只补指定条目
- `seed_sync` 现在支持**补写缺失媒体**（条目已存在但 audio/image 为空时补齐，已有媒体不受影响）

### 2. 跨分类 audio_file 基名必须全局唯一
- 事故：vehicles 和 space 的「火箭」都用 `rocket.mp3`，后生成的覆盖先生成的 → 交通版火箭播太空文案
- 规则：不同分类条目的 `audio_file` 基名不得相同（测试 `test_audio_basenames_globally_unique` 会拦截）

### 3. 宿主命令执行环境会间歇性故障（WorkBuddy 特性）
- 现象：Bash / PowerShell / 子代理全部无输出（连 `echo` 都空），几分钟到几十分钟后自行恢复
- 对策：① 文件修改用 Read/Write/Edit 照常做，命令部分等恢复；② 用户重启 WorkBuddy 立即可恢复；
  ③ 验证文件是否存在用 Read 探测（Glob 对 media/ 大目录索引不完整，会漏报）

### 4. Quiz 出题去重的物理限制
- 10 题 × 4 选项 = 40 个「出现位置」，最少分类（太空 15 条）撑不满 → **「选项全不重复」不可能**
- 教训：第一版用 seen 全去重，实测 15 条分类第 5 题就耗尽重置、正确答案反而重复
- 正解（时间正向）：正确答案互不重复 + 已出答案不再混入后续选项；干扰项允许复用但永与答案冲突
- 测试 `QuizNoRepeatTests` 3 个用例锁死该行为

### 5. 模板 slice 切 emoji 会切坏 ZWJ 组合
- 现象：职业分组标签（👨⚕️/👨🚒/👩🏫 等 ZWJ emoji）用 `{{ label|slice:":1" }}` 只剩半个 emoji；
  iPad 宽屏下标签 emoji 重复显示 2 个（slice 的 + label 里的）
- 正解：视图层 `label.partition(" ")` 拆成 icon + 纯文字，模板按钮统一 gt-count=icon / gt-label=文字
- 规则：`Category.groups` 的 label 固定 `"emoji 文字"` 格式

### 6. 首页查询优化
- `prefetch_related("items")` + 模板 `cat.item_count`（内部 count()）→ 每次发新 COUNT（7 分类 8 次查询）
- 正解：`Category.objects.annotate(item_count=Count("items"))` → 1 次查询，模板零改动
- 注意：annotate 字段名与模型方法同名时，实例属性优先，模板 `cat.item_count` 渲染 int

### 7. 其他
- `cp -r data/ 目标已存在的 data/` 会产生嵌套 `data/data/`；用 `cp data/*.py 目标目录/`
- 工作区副本（D:\workbuddy\...）必须与真实仓库（C:\Users\2504\Documents\learning-platform）同步
- 提交前跑：`manage.py check` / `manage.py test apps.core` / `manage.py check_data`（30+ 测试兜底）

### 8. 大图压缩（mozjpeg，>4MB → 4MB 内）
- 规则（2026-07-31 更新）：图片超过 4MB 必须压缩到 4MB 以内，**不降分辨率**
- 工具：npm 装 `mozjpeg`（imagemin 包）→ `node_modules/mozjpeg/vendor/cjpeg.exe`（mozjpeg 3.1）
- **⚠️ Windows 坑**：cjpeg 的 `-outfile -`（stdout）模式不可用——stdout 返回空导致输出 0 字节文件，
  还会残留一个名为 `-` 的垃圾文件（用 `git rm --cached -- "-"` + `rm -- "-"` 清理）
- 正解流程：Pillow 解码 → `tempfile` PPM 临时文件 → `cjpeg -quality Q -optimize -outfile tmp.jpg tmp.ppm`
  → 二分 quality(40-98) 找 <4MB 的最高质量 → 写临时文件后 `os.replace` 原子替换原图
- 实测：15 张 88.2MB → 51.4MB，全部 3.4~3.8MB，quality 62~98（照片肉眼几乎无差别），分辨率 100% 不变
- 压缩不改变文件名 → DB / check_data 无需任何处理

### 9. Django 模板标签参数不支持条件表达式
- 事故：`{% ifchanged item.pinyin_initial if sort_en else item.en_initial %}` —— Django 把 ifchanged 参数按
  空白拆成多个**变量**，`if`/`else` 被当变量解析 → 分块判断错乱，同首字母的条目每个都单独渲染分块
- 规则：**模板标签参数只接受简单变量**；任何条件/表达式逻辑一律在视图层预计算好（如 `item.initial`），
  模板里 `{% ifchanged item.initial %}` 单变量
- 测试锁死：`test_letter_dividers_grouped_by_initial`（同字母合并为一个分块）


### 迁移步骤

```bash
# 1. 加 group 字段
python manage.py makemigrations
python manage.py migrate

# 2. 重新导入带分组的数据
python manage.py seed_data --force

# 后续加新动物时，seed_data 元组第 11 位就是分组
```

### 注意事项

- 每组必须 ≥ 4 只（练习模式最低要求），当前最小 6 只 ✓
- 分组 Tabs 只在浏览模式显示，卡片和练习模式不受影响
- visited 状态跨组保持，切换 Tab 不会丢失
- group 字段使用 Django choices 枚举，防止脏数据
- 新增动物时别忘了填第 11 个字段 group
