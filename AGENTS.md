# AGENTS.md · 项目规则

> 📌 **文档基线**：2026-08-03 完成管理仓库规范化（AGENTS/CHANGELOG 新增、三仓互链、过时信息清理）
> **更新文档/代码后，请更新此行**（日期 + 新 commit hash），并在 CHANGELOG 追加版本

> 给 AI / 未来的你：只记代码里看不出的关键信息。架构详解见 [DEVELOPMENT.md](DEVELOPMENT.md)，文档中心维护见 [docs/ABOUT.md](docs/ABOUT.md)。

## 项目是什么（三仓定位）

**展示层管理仓库**：项目导航站 + 开发帮助文档中心。与 [knowledge-base](https://github.com/Simiely/knowledge-base)（经验提炼）、[codebuddy-skills](https://github.com/Simiely/codebuddy-skills)（技能集合）互链，三仓各司其职、不重复存储。

## 技术栈

- 单文件 SPA：`index.html`（#viewWelcome 首页 + #viewCatalog 目录页，CSS opacity/transform 过渡）
- 数据：`projects.json`（fetch 加载，失败用 FALLBACK_PROJECTS 兜底）
- 文档中心：docs/ 三层（导航 README → 模块 M1-M6 → 归档 archive/ 快照），来源标注 + synced_at 追踪
- 自动脚本：docs/_scripts/（gen_project_pages / check_docs / archive_docs / backfill_archive）
- GitHub Pages 部署（`.nojekyll`，根目录自动构建）

## 关键坑

1. **关键视觉状态用内联样式**：`.cat-card` 的 opacity 用 CSS class 曾失效（卡片生成了但看不见）——用 `card.style.opacity` 直接设置
2. **动画延迟只在一个地方控制**：CSS `transition-delay` 和 JS `setTimeout` 同时控制同一动画会双重延迟（时钟晚 1s 出现）——二选一
3. **Pages 部署排障**：CDN 缓存 max-age=600；排查用 API `GET /repos/{owner}/{repo}/pages`，手动构建 `POST .../pages/builds`，空 commit 触发重建
4. **projects.json 必填**：`name`、`path`；`path` 不带前后 `/`；`category` 需与导航 tab 的 `data-cat` 一致（web/tool/design）
5. **文档中心来源追踪**：archive/ 是完整快照、modules/ 是聚合改写——更新走"上游仓库 → 同步 archive/ → 刷新 synced_at → 更新模块"

## 维护命令

```bash
# 文档中心维护
python3 docs/_scripts/gen_project_pages.py   # 生成项目页
python3 docs/_scripts/check_docs.py          # 校验文档完整性
python3 docs/_scripts/archive_docs.py        # 归档上游文档快照
# 导航站本地预览
npx serve .
```

## 约定

- 深/浅色主题（localStorage 'hubworld-theme'）；强调色 #ff9292；卡片靠 1px 边框区分（bg 与 card 同色）
- 新增项目：projects.json 加条目 + docs/projects/ 登记（ABOUT.md 流程）
- 仓库改名/删除后：同步更新 README 项目表、docs/projects/ 对应页、archive/
