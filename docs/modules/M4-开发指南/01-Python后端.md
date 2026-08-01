---
module: M4
title: M4-01 Python 后端开发指南
tags: [python, fastapi, django, sqlalchemy]
sources:
  - project: homekeeper
    repo: https://github.com/Simiely/homekeeper
    file: docs/05-开发指南.md
    synced_at: 2026-08-01
  - project: obsidian-agent
    repo: https://github.com/Simiely/obsidian-agent
    file: docs/06-开发指南.md
    synced_at: 2026-08-01
  - project: learning-platform
    repo: https://github.com/Simiely/learning-platform
    file: DEVELOPER.md
    synced_at: 2026-08-01
---

# M4-01 Python 后端开发指南

> 覆盖 homekeeper(FastAPI)、obsidian-agent(FastAPI)、learning-platform(Django)。

## FastAPI 项目(homekeeper / obsidian-agent)

> 📌 来源:`homekeeper` docs/05-开发指南.md · `obsidian-agent` docs/06-开发指南.md

### 分层原则

```
core/  → 领域核心,不依赖 Web 框架,单测好写
api/   → REST 路由,只做参数校验与响应
config → 环境变量 + pydantic-settings
```

### 技术要点

| 主题 | 约定 |
|---|---|
| 数据访问 | SQLAlchemy 2.x ORM |
| 校验 | Pydantic v2 |
| 认证 | JWT(项目内如 homekeeper 自建) |
| 配置 | `.env.example` 模板 + pydantic-settings |
| 可插拔 | 索引引擎 / LLM / 数据源走抽象接口 |
| 测试 | pytest |

### 新增一个模块的流程(以 homekeeper 为例)

1. 在 `core/` 添加领域逻辑(纯函数/类,不 import 框架)
2. 在 `api/` 添加路由,绑定 core
3. 前端加页面/交互
4. 补充文档 + 踩坑记录

## Django 项目(learning-platform)

> 📌 来源:`learning-platform` · DEVELOPER.md

- 数据模型:Category / Item(分类、条目),`seed_sync` 管理种子数据
- 路由:`/category/<name>/`、`/category/<name>/cards/`、`/category/<name>/quiz/`
- 前端:Alpine.js,触屏优先
- 发音:edge-tts 生成三语音频
- 新增动物流程:见 `ADD_ANIMALS_GUIDE.md`

## 本地开发环境

| 项目 | 命令 |
|---|---|
| homekeeper | `docker compose up -d --build` 或本地 venv |
| obsidian-agent | 见 docs/06-开发指南.md(Docker + 本地两种) |
| learning-platform | `python manage.py runserver 0.0.0.0:8000` |

---

## 相关文档

- [M1 部署与快速上手](../M1-部署与快速上手.md)
- [M2 架构与设计](../M2-架构与设计.md)
- [M5 踩坑记录 · Python](../M5-踩坑记录/03-Python坑.md)
- [返回 M4 索引](README.md)
