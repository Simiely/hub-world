---
module: archive
title: README.md
tags: [collab-plan-miniprogram]
source:
  project: collab-plan-miniprogram
  repo: https://github.com/Simiely/collab-plan-miniprogram
  file: README.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/collab-plan-miniprogram/blob/main/README.md)

# 协作计划小程序 (collab-plan-miniprogram)

基于**微信云开发（CloudBase）**的多人协作计划小程序：自建账号密码登录、指定成员可见、创建者或任一成员点击即可完成、订阅消息定时提醒、时间戳水位线增量同步。

> 📚 **文档总导航在 [`docs/README.md`](./docs/README.md)** —— 项目唯一入口，新接手的人（包括未来的你与 AI Agent）第一件事就是读它。

---

## 功能概览

| 模块 | 说明 | 状态 |
|---|---|---|
| **账号体系** | 自建账号密码（非微信授权登录），账号可跨微信复用，Token 30 天滑窗续期 | ✅ M1 |
| **核心闭环** | 创建计划 → 指定成员 → 列表展示 → 创建者/任一成员点击完成 | ✅ M2 |
| **同步引擎** | 服务器时间戳水位线 + 复合游标分页 + 本地库 + 离线队列，先 push 后 pull | ✅ M3 |
| **提醒系统** | 订阅消息授权 + 自建额度池 + 定时触发器推送（开发中） | ⬜ M4 |

**当前进度**：M0 → M1 → M2 → M3 已完成，`npm test` **295 项断言全过**（约 3 秒跑完）。详见 [08-roadmap.md](./docs/08-roadmap.md)。

## 技术栈

- 后端：微信云开发 CloudBase（云函数 + 定时触发器 + 免鉴权 openid）
- 前端：微信小程序原生（WXML/WXSS/JS），UI 暂用原生自定义组件（TDesign 待「构建 npm」可用后平替）
- 测试：零依赖 Node 单测，`tests/mocks/wx-server-sdk` 内存 Mock 严格复刻真实 SDK

## 快速开始

```bash
npm install        # 安装依赖并自动同步 _shared → 各云函数 common/
npm test           # 跑全部单测（295 项断言）
npm run sync:shared # 手动同步云函数公共层
```

本地单测无需微信环境；真机联调按 [`docs/12-deploy-guide.md`](./docs/12-deploy-guide.md) 部署云函数、配置环境变量、初始化数据库与索引。

## 目录速览

```
├── docs/            # 📚 文档体系（12 篇，含踩坑库 51 条）
├── miniprogram/     # 📱 前端：pages / packageA / components / services / sync / store / core / utils
├── cloudfunctions/  # ☁️ 云函数：auth / init-db / plan / sync（+ M4 remind-scan / subscribe）
├── tests/           # ✅ 单测（9 个用例文件）
└── scripts/         # 工具脚本（sync-shared 等）
```

## 文档地图（精选）

- 想了解产品「做什么」→ [`01-product-spec.md`](./docs/01-product-spec.md)
- 想了解代码「怎么分层」→ [`02-architecture.md`](./docs/02-architecture.md)
- 想了解同步机制 → [`04-sync-design.md`](./docs/04-sync-design.md)
- 卡住了 / 报错了 → [`09-pitfalls.md`](./docs/09-pitfalls.md)（已记录 51 个坑）
- 变更记录 → [`10-changelog.md`](./docs/10-changelog.md)
