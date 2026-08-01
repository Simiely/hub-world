# 来源标注模板 (SOURCE_TEMPLATE)

> 本文件是文档中心所有文档的 **frontmatter 规范**。每篇文档(模块文档 + 归档文档)都必须以本模板开头。

## 模板

```markdown
---
module: <模块ID>            # 如 M1 / M2 / M3 / M4 / M5 / M6 / project / archive
title: <文档标题>
tags: [<标签1>, <标签2>]    # 技术栈 / 平台 / 领域
sources:
  - project: <项目名>        # 仓库名,如 homekeeper
    repo: https://github.com/Simiely/<项目名>
    file: <源文件路径>        # 内容取自该项目的哪个文件
    synced_at: <YYYY-MM-DD>  # 最近一次同步日期
# 可选的更多 source 条目,文档聚合了多少项目就列多少
---

# <文档标题>

> 📌 来源说明:本文档内容主要取自:
> - `homekeeper` · [docs/05-开发指南.md](https://github.com/Simiely/homekeeper/blob/master/docs/05-开发指南.md)
> - `obsidian-agent` · [docs/06-开发指南.md](https://github.com/Simiely/obsidian-agent/blob/main/docs/06-开发指南.md)
>
> 上游项目更新后,请同步本文档并更新 `synced_at`。
```

## 规则

1. **module 字段**:
   - `M1` 部署与快速上手 / `M2` 架构与设计 / `M3` API 参考
   - `M4` 开发指南 / `M5` 踩坑记录 / `M6` 更新日志
   - `project` 项目卡片页 / `archive` 原始归档

2. **sources 是溯源的核心**:任何内容都必须能追溯到"哪个项目的哪个文件"。聚合文档里每个章节还应在正文用小字标注:

   ```
   > 📌 本节来源:`homekeeper` · docs/05-开发指南.md
   ```

3. **synced_at 是更新维护的锚点**:上游项目文件变更后,更新对应文档并刷新此日期。

4. 归档文档(archive/ 下)直接搬运原文,frontmatter 用 `module: archive`,并在正文顶部加来源引用块。

## 模板文件位置

- 归档文档模板: `docs/_templates/archive-template.md`
- 项目卡片模板: `docs/_templates/project-template.md`
