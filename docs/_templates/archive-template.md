---
module: archive
title: 归档文档模板
---

# 归档文档模板

> 复制本文件到 `docs/archive/<项目名>/<文件名>`,按注释填写。

```markdown
---
module: archive
title: <原文档标题>
tags: [<项目名>, <技术栈>]
source:
  project: <项目名>
  repo: https://github.com/Simiely/<项目名>
  file: <源路径, 如 docs/05-开发指南.md>
  branch: <默认分支>
  synced_at: <YYYY-MM-DD>
---

<!-- ↓↓↓ 以下是原始文档内容,完整保真搬运,不要改动正文 ↓↓↓ -->

# 原始文档标题

(原始内容...)
```

## 归档说明

- **保真原则**:归档文档是上游仓库文档的**完整快照**,正文不改写、不删减。
- **同步机制**:上游仓库更新后,重新拉取最新内容覆盖本文件,并刷新 `synced_at`。
- **来源追溯**:frontmatter 的 `source` 字段记录了精确来源,更新时通过它定位上游文件。
- 归档文档属于"内容仓库";日常阅读和导航请使用 `docs/modules/` 下的聚合模块文档。
