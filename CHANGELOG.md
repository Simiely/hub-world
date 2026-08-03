# CHANGELOG.md · 版本记录

> 按里程碑记录导航站与文档中心的发展。详细问题记录见 [DEVELOPMENT.md](DEVELOPMENT.md)。

## 2026-08-03 — 管理仓库规范化

- **三仓互链**：README 顶部加管理仓库区（knowledge-base 经验库 + codebuddy-skills 技能库），明确分工
- **AGENTS.md 新增**：技术栈 + 5 条关键坑 + 维护命令 + 文档基线
- **CHANGELOG.md 新增**：本文件
- **过时信息清理**：ntlite-windows-guide-2 → ntlite-windows-guide（仓库已改名）；CircleDiffusion / miniprogram-item-expiry 标记已删除

## 里程碑（历史演进）

- **文档中心上线**：docs/ 三层结构（导航 README + 模块 M1-M6 + 归档 archive/），35 项目文档聚合，来源标注 + synced_at 追踪
- **自动化脚本**：docs/_scripts/（gen_project_pages / check_docs / archive_docs / backfill_archive）
- **导航站迭代**：浮动卡片漂移动画（6 张循环 + parallax）、Masonry 目录网格 + 分类 tab、深/浅主题
- **数据驱动**：projects.json（fetch + FALLBACK_PROJECTS 兜底）
- **初始版本**：项目导航单页（luang-prabang-trip 等早期项目）

## 备注

- 仓库无版本 tag；提交历史 219 条
