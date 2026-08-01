---
module: archive
title: 开发README.md
tags: [resources]
source:/n  project: resources
  repo: https://github.com/Simiely/resources
  file: 开发README.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/resources/blob/main/开发README.md)

# 开发 README（维护笔记）

本文件记录构建 / 维护「工具软件资源库」过程中遇到的**关键问题与决策**，
供后续遇到同类问题时快速对照参考。普通使用请见 `README.md`。

---

## 0. 一句话目标

源数据是 **Obsidian 双链笔记《软件分类.md》**（会被反复手工增删改），
目标是把它变成**可检索、可快速定位**的单文件 HTML，**且 AI 能读 md 直接重跑更新**。

由此引出核心架构决策：**数据（JSON）与展示（HTML 外壳）分离**。
> 理由：更新 md 时只替换数据块，外壳不变、diff 清晰；统计数字由 JS 实时计算，单一数据源。
> 反例：早期版本用 Python **预渲染**整页卡片，改一项全文件 `diff` 乱掉，已废弃。

---

## 1. 解析层：把自由格式 md 变成结构化数据

源笔记是半结构化的（callout、裸 `>` 行、分隔线、任意顺序混排），解析器踩过三个坑：

### 坑 1：顺序敏感的「label 污染」bug（已修）
- **现象**：下载按钮文字被污染成 `解压密码：1234`。
- **根因**：早期用**流式状态机**，逐行维护一个共享游标 `cur`，遇到链接行就把上一份 `label` 覆盖掉。
  一旦源文件里「链接行」写在「文件名 / 解压密码行」**之前**，游标就被错误复用。当时只是靠数据顺序“恰好正确”没爆。
- **解法**：改为**「先抽事实，后合成结构」**——
  每个块先收集 `urls / files / pwds / texts`，全部收齐后再 `_make_entries()` 生成 entry。
  **完全顺序无关**，label 永远取 `texts[0]`，不再被后续行覆盖。
- **经验**：解析自由格式文本时，**把「事实抽取」和「结构生成」分两步**，绝不在读行过程中边读边改共享游标。

### 坑 2：缺链兜底 / 假「链接缺失」（已修）
- **现象**：某软件同时出现「⚠️ 链接缺失」+ 正常下载两条，或 `href=""` 死链按钮。
- **根因**：按「`>` 行」切块，把同一软件的「文件名行」和「链接行」误切成**两条 entry**（例：ViGEmBus 的 `> 通过网盘分享的文件：…` 与下一行 `> 链接: https://pan.baidu.com/…`）。
- **解法**：以 **`---` 分隔线为块边界**，块内聚合所有下载事实——「文件名 + 链接」天然合并成 1 条带链接的下载。
  对**真缺链**（源本身没贴链接，如早期 Cinema 4D）显式渲染「⚠️ 链接缺失」提示，**绝不输出 `href=""`**。
- **经验**：同一软件的多行事实要**聚合**；对缺失数据要有**显式兜底文案**，不要裸渲染成死链。

### 坑 3：导航点击无反应 / 默认高亮错乱（已修）
- **现象**：左侧导航点谁都没反应；默认高亮停在「其他软件」。
- **根因**：生成 **sidebar（导航）和 main（正文）是两个独立循环**，计数器 `gi` 只在 main 循环里 `gi += 1`，
  sidebar 复用了**还没自增**的 `gi`。结果工具软件 8 个分类全指向 `cat-0`，设计软件全指向 `cat-8`，
  真正的 `cat-9`（其他软件）**没有任何导航项指向它**。
- **解法**：合并成**一个循环**，`gi` 在每个分类上统一 `+1`，保证 nav 的 `data-target` 与 section 的 `id` 严格一一对应；加载时默认高亮第一项。
- **经验**：生成「导航」和「内容」时，**id / target 必须来自同一个递增计数器**；避免「两处循环各自维护索引」。

---

## 2. 工程层：Python / Node / 路径的坑

### 坑 4：Python f-string 里的大括号地狱（已规避）
- **现象**：HTML / CSS / JS 模板里大量 `{}`，用 `f"""..."""` 需要疯狂 `{{ }}` 转义，极易写错。
- **解法**：放弃 f-string，用**「原始模板字符串 + 占位符替换」**：模板里留 `__DATA__` 等占位符，`json.dumps(...)` 后 `TEMPLATE.replace('__DATA__', ...)`。
- **经验**：生成含花括号的代码文本时，**别用 f-string / .format**，直接「字符串占位符替换」最稳。

### 坑 5：Git Bash 吞掉 Windows 反斜杠路径（已规避）
- **现象**：命令里写 `C:\Users\wandou\...`，到脚本里路径被截断 / 找不到文件。
- **解法**：本机 Git Bash 环境下跑 Python 时，Windows 路径转 **POSIX 风格**（`/c/Users/wandou/...`）或**正斜杠**。
- **经验**：在 WorkBuddy 的 Bash（Git Bash）里跑脚本，Windows 绝对路径一律转 POSIX 或 forward-slash。

### 坑 6：无浏览器环境如何校验渲染（已用 Node 离线验证）
- **现象**：沙箱没有浏览器，无法确认 HTML 是不是空白页。
- **解法**：写个**最小 DOM 桩**（只实现 `createElement / appendChild / querySelectorAll / classList / dataset` 等用到的 API），
  用 **Node 22** 直接 `require` 出 HTML 里的渲染函数执行，断言：
  `.card` 数 == 106+13、空 `href` 的 `.dl-btn` == 0、`.nav-item` == 10、关键软件存在、统计文本正确。
- **经验**：前端渲染逻辑可在 **Node + DOM 桩**下离线验证，不必真开浏览器。校验脚本用完即删，不留仓库。

---

## 3. 解析启发式：区分「分类」与「软件项」

Obsidian 笔记里 `##` **既当分类也当软件项**（设计软件章把 CorelDRAW / Blender / C4D 直接写 `##` 级）。
判定规则（写在 `parse_structure`）：

| 层级 | 含 `[[链接]]` | 处理 |
|------|---------------|------|
| `#`  | — | 大章（分组） |
| `##` | 否 | 分类 |
| `##` | 是 | 软件项 → 归入「`{章名}·其他`」合成分类 |
| `###`| 否 | 父项的子说明 |
| `###`| 是 | 软件项（挂到当前分类 / 父项） |
| `####`| 是 | 子项（挂到当前父项） |

- 合成分类 `get_synthetic()`：当某大章下出现「直接写 `##` 级的软件」，自动建一个名为 `章名·其他` 的分类收纳，避免变成空分类。
- `strip_wiki()`：把 `[[链接|别名]]` / `[[链接]]` 还原成可读文本，既用于标题也用于下载行。

---

## 4. 本机运行时与沙箱限制（速查）

- **Node**：`C:\Users\wandou\.workbuddy\binaries\node\versions\22.22.2\node.exe`
- **Python**：`C:\Users\wandou\.workbuddy\binaries\python\versions\3.13.12\python.exe`
- **GitHub 上传**：`git push` 直连 `github.com:443` 在沙箱被拦 → 用 **Contents API**：
  `PUT /repos/Simiely/resources/contents/{path}`，body 含 base64 content + message + branch；
  **已存在文件需先 `GET` 取 `sha` 再带 `sha` 提交**（否则 409 冲突）。
  **token 仅用于本地上传命令，绝不写进任何被提交的文件。**

---

## 5. 关键代码位置索引（改哪里看哪里）

`build_catalog.py`：
- `parse_downloads()`：下载块解析（坑 1 / 坑 2 的聚合逻辑）。
- `parse_structure()`：标题 → 大章/分类/软件项/子项 的归类（坑 3 的 `gi` 在 `main()` 里统一 +1）。
- `parse_heading()` / `strip_wiki()`：软件名 / 用途 / 收藏 / 双链还原。
- `count_stats()`：Python 端统计（与前端统计应一致）。
- `TEMPLATE`：HTML 外壳（CSS + JS 渲染器）；`__DATA__` 占位符注入 JSON。

`software-catalog.html`（生成后）：
- `<script type="application/json" id="catalog-data">`：内嵌数据，改 md 后只换这块。
- 前端渲染器：`renderItem` / `renderDl` / nav 生成 / IntersectionObserver 滚动高亮。

---

## 6. 更新 / 维护 checklist

1. 改 md → `python build_catalog.py`，看终端统计是否合理（大章/分类/软件/收藏/下载；`missing` 应为 0 除非源真缺链）。
2. 用浏览器或 Node 桩打开 `software-catalog.html` 确认：导航一一对应、无空 `href`、提取码可复制。
3. 推送到私人仓库（Contents API）。
4. 若改了生成逻辑，记得同步更新 `README.md` / 本文件里相关的「坑」与「位置索引」。
