---
module: project
title: 项目卡片模板
tags: [template]
---

# 项目卡片模板

> 复制本文件到 `docs/projects/<项目名>.md`,按注释填写。

```markdown
---
module: project
title: <项目名> - <中文名>
tags: [<技术栈标签>]
project:
  name: <项目名>
  repo: https://github.com/Simiely/<项目名>
  private: false          # 是否为私有仓库
  language: <主语言>
  branch: <默认分支>
  description: <一句话描述>
  synced_at: <YYYY-MM-DD>
---

# <项目名>

## 项目简介

(1-3 句描述,取自仓库 description / README)

## 快速信息

| 项 | 值 |
|---|---|
| 语言 | ... |
| 状态 | 进行中 / 维护中 / 完成 |
| 部署方式 | ... |
| 开源协议 | ... |

## 文档入口

- [GitHub 仓库](链接)
- [归档文档](链接到 docs/archive/ 下的对应文件)

## 相关模块

- M1 部署与快速上手: (链接)
- M4 开发指南: (链接)
- M5 踩坑记录: (链接)
```
