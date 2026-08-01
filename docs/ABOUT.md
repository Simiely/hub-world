---
module: about
title: 文档中心总说明
tags: [说明, 规范, 维护]
---

# 📖 开发帮助文档中心 · 总说明

> **本文档是文档中心的"总纲"** —— 说明它是什么、为什么这样组织、目录如何分工、更新时该走什么流程、有哪些必须遵守的规则和必须避开的坑。
> 无论是人还是 AI Agent,接手维护前请先读本文档 + [_templates/SOURCE_TEMPLATE.md](_templates/SOURCE_TEMPLATE.md)。

---

## 1. 这是什么

**开发帮助文档中心** = Simiely 全部 **35 个 GitHub 项目**(33 公开 + 2 私有)开发文档的**统一聚合入口**。

它解决的问题:
- 文档散落在 35 个仓库里,格式不统一、互相没有链接 → **集中到一个地方**
- 知识重复(3 个 Python 项目、2 个 Android、3 个小程序共享大量经验)→ **按主题模块化聚合**
- 更新容易乱、不知道哪份是最新的 → **来源标注 + 同步日期追踪**

## 2. 核心设计原则(为什么这样组织)

### 原则一:三层结构,各司其职

```
导航层   docs/README.md + modules/ 索引   → 让人"找得到"
模块层   modules/M1~M6                   → 让人"看得懂"(聚合、提炼、互链)
归档层   archive/<项目>/                 → 让人"查得准"(原始文档完整保真快照)
```

- **模块层是日常阅读和更新的主战场**,按主题而非按项目组织;
- **归档层是"内容仓库"和溯源依据**,只做保真搬运,不改写。

### 原则二:单一事实来源(SSOT)

每个源项目的 GitHub 仓库文档是**唯一权威**。本中心:
- `archive/` = 源文档的**快照副本**(可离线阅读,但以 GitHub 原文为准)
- `modules/` = 基于快照的**提炼改写**(人维护)

> ⚠️ 冲突时的裁决规则:**GitHub 原文 > archive 快照 > modules 提炼**。modules 与原文不一致时,以原文为准修正 modules。

### 原则三:来源可追溯(更新不乱的基石)

每篇文档的 frontmatter 都带 `source` / `sources` 字段:

```yaml
sources:
  - project: homekeeper            # 内容取自哪个项目
    repo: https://github.com/Simiely/homekeeper
    file: docs/05-开发指南.md      # 取自该项目的哪个文件
    synced_at: 2026-08-01          # 最近同步日期 —— 更新的锚点
```

正文中每个章节用 `> 📌 来源:<项目> · <文件>` 标注。**任何内容都能追溯到"哪个项目的哪个文件"**。

## 3. 目录结构总览

```
hub-world/
├── README.md                    # 仓库导航(含文档中心入口)
├── index.html / projects.json   # 原有 HTML 导航站(独立,勿动)
└── docs/                        ★ 文档中心
    ├── README.md                # 导航首页:场景速查表(读者入口)
    ├── ABOUT.md                 # 本文档:总说明(维护者入口)
    ├── modules/                 # 模块层 —— 跨项目聚合文档(日常更新主战场)
    │   ├── M1-部署与快速上手.md
    │   ├── M2-架构与设计.md
    │   ├── M3-API参考.md
    │   ├── M4-开发指南/
    │   │   ├── README.md
    │   │   ├── 01-Python后端.md
    │   │   ├── 02-微信小程序.md
    │   │   ├── 03-Android-Kotlin.md
    │   │   └── 04-桌面与脚本工具.md
    │   ├── M5-踩坑记录/
    │   │   ├── README.md
    │   │   ├── 01-微信小程序坑.md
    │   │   ├── 02-Android坑.md
    │   │   ├── 03-Python坑.md
    │   │   └── 04-桌面与脚本坑.md
    │   └── M6-更新日志.md
    ├── projects/                # 项目层 —— 35 个项目卡片页(脚本生成)
    │   ├── README.md
    │   └── <项目名>.md
    ├── archive/                 # 归档层 —— 各项目原始文档快照(脚本搬运)
    │   ├── README.md
    │   └── <项目名>/<原始路径>
    ├── _templates/              # 规范模板
    │   ├── SOURCE_TEMPLATE.md   # ★ 来源标注规范(必读)
    │   ├── archive-template.md
    │   └── project-template.md
    └── _scripts/                # 维护脚本 + 维护指南
        ├── README.md            # 维护指南(更新流程详解)
        ├── archive_docs.py      # 全量搬运:仓库文档 → archive/
        ├── backfill_archive.py  # 增量补齐:下载缺失归档文件
        ├── gen_project_pages.py # 重新生成 projects/ 卡片页
        └── check_docs.py        # 联检:链接 / frontmatter / 结构
```

## 4. 更新流程(按场景)

> 详细命令见 [_scripts/README.md](_scripts/README.md)。以下是与本文档配套的"决策版"流程。

### 场景 A:某个项目更新了文档(最常见)

```
1. 更新归档快照     → 运行 archive_docs.py / backfill_archive.py(需 GITHUB_TOKEN)
2. 检查差异         → git diff archive/<项目>/ 看上游改了什么
3. 同步模块文档     → 手动更新 modules/ 里涉及该项目的章节(提炼、改写)
4. 刷新 synced_at   → 更新对应文档 frontmatter 的 synced_at 为当天
5. 更新项目卡片     → 如需,运行 gen_project_pages.py
6. 联检             → python _scripts/check_docs.py,确认"关键链接全部通过"
7. 提交推送         → git commit + push 到 hub-world main
```

### 场景 B:新增一个项目

```
1. 归档文档   → 把新项目文档搬运进 archive/<项目名>/
2. 生成卡片   → 更新 _docs_manifest.json 或直接运行 gen_project_pages.py(需登记元数据)
3. 补模块     → 在 modules/ 对应分册(M1 部署 / M4 开发指南 / M5 踩坑)补充条目
4. 更新索引   → projects/README.md + docs/README.md 的项目一览表
5. 联检 + 推送
```

### 场景 C:新踩了一个坑

```
1. 先写进对应项目仓库的 DEV.md(源头)
2. 同步 archive/(跑 backfill)
3. 在 modules/M5-踩坑记录/ 对应平台分册补充一条(现象 → 原因 → 解法)
4. 更新该分册 frontmatter 的 synced_at
```

### 场景 D:发现文档中心有错误

```
1. 判断错误来源:
   - modules 写错了 → 直接改 modules(它是人维护的,本就允许改)
   - archive 与原文不一致 → 以 GitHub 原文为准,重新同步 archive
2. 不要直接改 archive 的正文 → archive 是"快照",正文只由同步脚本更新
   (唯一例外:archive 文件头的"查看 GitHub 原文"提示块)
```

## 5. 编写规范(必须遵守)

### 5.1 frontmatter 规范

- 每篇文档**必须**以 `---` 开头的 frontmatter 开始
- 字段:见 [_templates/SOURCE_TEMPLATE.md](_templates/SOURCE_TEMPLATE.md)
- `module` 字段取值:`M1`~`M6` / `project` / `archive` / `about` / `template`
- 聚合文档(modules)有多个来源时用 `sources`(列表);单一来源用 `source`

### 5.2 章节来源标注

聚合文档里,每个项目的章节前用引用块标注来源:

```markdown
> 📌 来源:`homekeeper` · docs/05-开发指南.md
```

### 5.3 链接规范(重要,最容易出错)

| 规则 | 说明 | 反例 |
|---|---|---|
| **相对路径** | 用相对链接,不用绝对路径 | ❌ `/docs/modules/M1.md` |
| **层级要算对** | `modules/` 下的子目录文档(如 M4 分册)指向同层用 `文件名.md`,指向上级用 `../`,指向 archive 用 `../../archive/` | ❌ 少写 `../` |
| **中文/括号文件名** | 含中文的链接 GitHub 能识别,但含括号 `()` 的必须用 `%28`/`%29` 转义 | ❌ `02-更新日志(CHANGELOG).md` |
| **代码块内的"链接"** | 代码块(```)和行内代码(`)里的内容不会被解析为链接,无需处理 | |
| **锚点链接** | `#锚点` 只对当前页有效;跨文件锚点(`file.md#锚点`)在 GitHub 上可用 | |

### 5.4 命名与内容

- 模块文档:M1~M6 + 描述性标题
- 踩坑条目统一格式:**现象 → 原因 → 解决方案**
- 归档文档:保持与源仓库相同的文件名和正文(保真原则)

## 6. 常见错误避坑清单(血泪教训)

| # | 坑 | 后果 | 规避 |
|---|---|---|---|
| 1 | **脚本里硬编码 GitHub token** | 推送被 GitHub 密钥扫描拦截,且公开仓库会泄露凭据 | token 一律从环境变量 `GITHUB_TOKEN` 读取,绝不写进代码 |
| 2 | **GitHub Contents API 请求中文文件名时不 URL 编码** | 请求静默失败,文件缺失(曾导致 18 个文档丢失) | 用 `urllib.parse.quote(path)` |
| 3 | **归档后源文档内部相对链接失效** | `docs/05-开发指南.md` 这类链接指向了 `docs/docs/` | 每个归档文件顶部补"查看 GitHub 原文"链接兜底 |
| 4 | **modules 子目录文档的 `../` 层级数错** | 链接 404 | 画一遍相对路径再写;用 `check_docs.py` 联检 |
| 5 | **文件名含括号 `()` 未转义** | Markdown 链接被截断 | 用 `%28` / `%29` |
| 6 | **忘记更新 synced_at** | 溯源时间线失真 | 每次改文档顺手刷新 frontmatter 日期 |
| 7 | **直接改 archive 正文** | 快照与原文失真 | archive 正文只由同步脚本覆盖 |

## 7. 文档中心自身版本记录

| 日期 | 版本 | 变更 |
|---|---|---|
| 2026-08-01 | v1.0 | 初版:35 项目收录、M1-M6 模块、34 项目归档(110 文件)、35 卡片页、来源标注规范、维护脚本 4 件 |

## 8. 相关入口

- [导航首页(读者入口)](README.md)
- [来源标注规范](_templates/SOURCE_TEMPLATE.md)
- [维护指南(命令详解)](_scripts/README.md)
- [🤖 更新提示词模板(发给 AI 用)](_templates/UPDATE-PROMPTS.md)
- [项目索引](projects/README.md)
- [归档区索引](archive/README.md)
