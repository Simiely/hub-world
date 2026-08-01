---
module: archive
title: README.md
tags: [resources]
source:
  project: resources
  repo: https://github.com/Simiely/resources
  file: README.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/resources/blob/main/README.md)

# 工具软件资源库（HTML）

把一份 Obsidian 双链笔记《软件分类.md》自动转换成**单文件、可离线打开**的软件资源目录网页。
左侧分类导航负责「整体浏览」，顶部搜索 / ⭐收藏负责「快速定位」，下载链接带提取码一键复制。

> 主色 `#FF9292`（珊瑚粉），深色默认 + 浅色切换；响应式（移动端侧栏自动转横滑）。
> 私人仓库：`Simiely/resources`（private）。

---

## 特性

- **整体浏览**：左侧「大章 → 分类」两级导航，点击平滑跳转，滚动自动高亮当前分类。
- **快速定位**：顶部实时搜索（匹配软件名 / 用途 / 备注 / 文件名），⭐「仅收藏」一键只看重点。
- **卡片化信息**：软件名 + 收藏星标 + 用途 pill + 网盘下载按钮 + 提取码「复制」+ 备注 / 警告条；子项（如 Everything 的 Toolbar）折叠在父卡内。
- **数据 / 展示分离**：md 是数据源，HTML 是生成物。改了 md 只需重跑脚本，只替换数据块，外壳不变、diff 清晰。
- **离线可用**：纯静态 HTML + 内嵌 JSON，双击即开，无需联网、无构建步骤。

---

## 架构

```
软件分类.md  ──parse──►  结构化 JSON  ──embed──►  software-catalog.html
                                  ▲                    （静态外壳 + 前端渲染器）
                                  │
                          build_catalog.py
```

- `build_catalog.py`：只负责「读取 md → 产出结构化 JSON」，内嵌进 HTML 的 `<script type="application/json" id="catalog-data">`。
- `software-catalog.html`：**外壳完全静态**（CSS + JS 渲染器），打开时在浏览器里读取 JSON 并渲染。
- 因此更新 md 后，脚本**只替换 HTML 里的数据块**，外壳不变、diff 清晰；统计数字由 JS 从数据实时计算（单一数据源，不会和 JSON 对不上）。

---

## 文件结构

```
resources/
├── software-catalog.html   # 资源库页面（数据 + 静态外壳）
├── build_catalog.py        # 生成器：md → 结构化 JSON → 嵌入 HTML
├── README.md               # 本文件：项目说明 + 使用
└── 开发README.md           # 开发笔记：关键问题 / 决策 / 坑（供后续维护参考）
```

---

## 使用方法

### 1. 预览
直接双击 `software-catalog.html` 用浏览器打开即可。

### 2. 重新生成
```bash
# 用默认源路径生成到同目录 software-catalog.html（默认源见 DEFAULT_MD）
python build_catalog.py

# 指定源 / 输出
python build_catalog.py --md "路径/软件分类.md" --out "路径/out.html"

# JSON 缩进（默认 1，便于 diff；设 2 更易读）
python build_catalog.py --indent 2
```
> 默认源路径：`C:\Users\wandou\Documents\obsidian\simiely\06_资料\软件分类.md`
> 脚本不含任何 token，纯本地运行。运行时会在终端打印统计（大章 / 分类 / 软件 / 收藏 / 子项 / 下载 / 缺失），可用于自检。

### 3. 更新流程（手动或交给 AI）
1. 在 Obsidian 里改《软件分类.md》（增删软件、改网盘链接、加 ⭐ 收藏等）。
2. 重跑 `python build_catalog.py`（如需可传 `--md` 指向最新路径）。
3. 打开 `software-catalog.html` 预览确认（重点看统计数字、有无「⚠️ 链接缺失」）。
4. 推送到本仓库（见下）。

**交给 AI 做时**：让 AI 读取最新的《软件分类.md》→ 运行上面的生成命令 → 校验输出（统计数字、无空 `href` 死链、`missing` 应为 0 除非源真缺链）→ 推送。脚本已内置统计打印，AI 可据此自检；也可用 Node 跑前端渲染器离线校验（见开发 README）。

### 4. 推送到私人仓库
仓库 `Simiely/resources`（private）。用 GitHub **Contents API** 上传（不能用 `git push`，见下）：

| 本地文件                | 仓库路径                |
|-------------------------|-------------------------|
| `software-catalog.html` | `software-catalog.html` |
| `build_catalog.py`      | `build_catalog.py`      |
| `README.md`             | `README.md`             |
| `开发README.md`         | `开发README.md`         |

> ⚠️ 本机 `git push` 直连 `github.com:443` 在沙箱被拦，请用 `PUT /repos/Simiely/resources/contents/{path}`（已存在文件需先 GET 取 `sha` 再带 `sha` 提交）。**token 仅用于本地上传命令，不要写进任何被提交的文件。**

---

## 数据说明 / 约定

源笔记里 Obsidian 专属语法按以下规则处理：

- `![[...]]` 嵌入图 / 双链详情：独立 HTML 无法引用原笔记图片，已去除，仅保留文字与网盘信息。
- 标题分类规则：`#` = 大章；`##/###` **含 `[[链接]]`** 的是软件项，纯文字的是分类；`####` = 子项。
  设计软件章里直接写在 `##` 级的专业工具（CorelDRAW、Blender、C4D 等）归入合成分类「设计软件·其他」。
- 若某软件在源笔记里**本身没贴网盘链接**，页面会渲染「⚠️ 链接缺失」提示（不是 bug），回 Obsidian 补上链接即可。

---

## 已知限制

- 源笔记里的图片、附件、双链跳转在网页里不可用（纯文字 + 网盘信息）。
- 提取码复制依赖浏览器 `navigator.clipboard`；个别老旧浏览器或 `file://` 限制下可能需手动选复制。
- 需要启用 JavaScript 才能渲染列表（已加 `<noscript>` 提示）。
