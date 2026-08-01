---
module: M4
title: M4 开发指南
tags: [开发, 规范, 技术栈]
sources:
  - project: homekeeper
    repo: https://github.com/Simiely/homekeeper
    file: docs/05-开发指南.md
    synced_at: 2026-08-01
  - project: collab-plan-miniprogram
    repo: https://github.com/Simiely/collab-plan-miniprogram
    file: docs/07-conventions.md
    synced_at: 2026-08-01
---

# M4 开发指南

> 按技术栈整理的开发规范、目录结构、代码约定。写代码前先读对应分册。

## 分册导航

| 分册 | 覆盖项目 | 内容 |
|---|---|---|
| [Python / FastAPI / Django](01-Python后端.md) | homekeeper、obsidian-agent、learning-platform、blender-car-mesh-optimizer | 后端分层、ORM、配置、测试 |
| [微信小程序](02-微信小程序.md) | collab-plan-miniprogram、potty-training-miniprogram、miniprogram-item-expiry | 云开发、数据层、同步、单测 |
| [Android / Kotlin](03-Android-Kotlin.md) | android-adskip、DarkMask | 无障碍服务、悬浮窗、前台服务 |
| [桌面 / 前端 / 脚本](04-桌面与脚本工具.md) | WindowTinter、AE/C4D/Blender 插件、vray-material-replacer | C#、ExtendScript、MaxScript、HTML 单文件 |

## 通用约定(所有项目)

1. **文档先行**:主要项目都有 `docs/` 体系,新接手先读 `docs/README.md` 或 README 的文档导航表。
2. **踩坑即记**:遇到问题解决后写入各项目 `DEV.md` / 踩坑文档。
3. **来源追踪**:本中心的聚合文档均标注来源,改代码后同步更新对应文档的 `synced_at`。

## Python 项目通用规范

> 📌 来源:`homekeeper` docs/05-开发指南.md、`collab-plan-miniprogram` docs/07-conventions.md

- **后端分层**:core(领域核心,不依赖 Web 框架)→ api(路由)→ 前端
- **配置管理**:环境变量 + pydantic-settings / `.env` 模板
- **可插拔设计**:索引引擎、LLM 提供商、数据源都走抽象接口
- **测试**:pytest(FastAPI 项目)/ 零依赖 Node 单测(小程序云函数)

## 分册入口

- [01-Python后端.md](01-Python后端.md)
- [02-微信小程序.md](02-微信小程序.md)
- [03-Android-Kotlin.md](03-Android-Kotlin.md)
- [04-桌面与脚本工具.md](04-桌面与脚本工具.md)

---

## 相关文档

- [M1 部署与快速上手](../M1-部署与快速上手.md)
- [M2 架构与设计](../M2-架构与设计.md)
- [M5 踩坑记录](../M5-踩坑记录/README.md)
- [← 返回文档中心](../../README.md)
