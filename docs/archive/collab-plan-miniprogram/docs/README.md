---
module: archive
title: README.md
tags: [collab-plan-miniprogram]
source:
  project: collab-plan-miniprogram
  repo: https://github.com/Simiely/collab-plan-miniprogram
  file: docs/README.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/collab-plan-miniprogram/blob/main/docs/README.md)

# 协作计划小程序 · 文档总导航

> **这是整个项目的唯一入口。** 任何人（包括未来的你、以及 AI Agent）接手这个项目，第一件事就是读这一页。
> 读完这页，你应该知道：项目在做什么、代码放在哪、遇到问题查哪本文档。

---

## 一、项目一句话定位

一个基于**微信云开发**的多人协作计划小程序：用内置账号密码登录，创建计划时指定可见成员，创建者或任一指定成员点击即可完成，支持定时提醒推送，本地与服务器通过时间戳做增量同步。

**技术选型（已锁定，变更需走 [10-changelog.md](./10-changelog.md) 记录）**

| 维度 | 选型 | 原因 |
|---|---|---|
| 后端 | 微信云开发 CloudBase | 免服务器、免备案、免鉴权拿 openid、自带定时触发器 |
| 账号体系 | **自建账号密码**（非微信授权登录） | 需求要求指定账号登录，账号可跨微信复用 |
| 消息提醒 | 订阅消息 + 自建授权额度池 | 微信订阅消息是「一次授权一次推送」，必须自己记账 |
| UI 组件库 | TDesign 小程序版（按需引入） | 官方出品，视觉贴近微信原生，审核友好 |
| 数据同步 | 服务器时间戳水位线 + 增量拉取 + 软删除 | 需求明确要求时间戳比对与差异同步 |

---

## 二、文档地图（按需查阅）

### 📘 先读这三本（新人上手 30 分钟）

| 文档 | 什么时候看 | 核心内容 |
|---|---|---|
| **[01-product-spec.md](./01-product-spec.md)** | 想知道「做什么」 | 功能清单、用户故事、任务状态机、权限矩阵 |
| **[02-architecture.md](./02-architecture.md)** | 想知道「代码在哪、怎么分层」 | 分层架构、模块职责、完整目录树、依赖规则、分包策略 |
| **[08-roadmap.md](./08-roadmap.md)** | 想知道「现在做到哪了、下一步做什么」 | 分阶段开发计划清单（含勾选状态） |

### 🔧 开发时按模块查

| 文档 | 对应模块 | 核心内容 |
|---|---|---|
| **[03-data-model.md](./03-data-model.md)** | 数据库 | 6 张集合的字段定义、索引、**权限配置（安全红线）** |
| **[04-sync-design.md](./04-sync-design.md)** | `miniprogram/sync/` | 水位线算法、增量拉取、离线队列、冲突解决 |
| **[05-reminder-design.md](./05-reminder-design.md)** | `cloudfunctions/remind-scan/` | 定时触发器、订阅额度池、推送幂等锁 |
| **[06-auth-design.md](./06-auth-design.md)** | `cloudfunctions/auth/` | 密码哈希、Token 签发校验、账号↔openid 绑定 |
| **[12-deploy-guide.md](./12-deploy-guide.md)** | 部署 / 上线 | 云函数上传、env 变量、初始化数据库与建索引、M1 验收自检 |

### 📐 规范与质量

| 文档 | 什么时候看 | 核心内容 |
|---|---|---|
| **[07-conventions.md](./07-conventions.md)** | 写代码前 | 命名规范、错误码、Promise 封装、setData 纪律 |
| **[09-pitfalls.md](./09-pitfalls.md)** | **卡住了、报错了、行为诡异** | ⚠️ 踩坑记录库，**已记录 51 个坑**（含 21 个 🔴 级） |
| **[../tests/README.md](../tests/README.md)** | 改完代码、加用例前 | `npm test` 用法、Mock 与真实 SDK 的行为对照表 |
| **[11-testing-release.md](./11-testing-release.md)** | 提审前 | 真机测试矩阵、审核 checklist、常见驳回原因 |
| **[10-changelog.md](./10-changelog.md)** | 每次改动后 | 更新日志（版本、变更、影响面） |

---

## 三、快速上手路径

### 场景 A：我是新加入的开发（或新一轮 AI 会话）

```
1. 读本页（README）           → 建立全局认知
2. 读 02-architecture.md      → 知道代码放哪、不要越层调用
3. 读 08-roadmap.md           → 找到当前进行中的任务
4. 动手前扫一眼 09-pitfalls.md → 避免重复踩坑
5. 改完代码 → 更新 10-changelog.md
```

### 场景 B：我要加一个新功能

```
1. 在 01-product-spec.md 补功能定义和权限规则
2. 若涉及新字段 → 改 03-data-model.md，并确认是否影响同步（04）
3. 在 08-roadmap.md 加任务项
4. 按 02-architecture.md 的分层写代码（page → service → core/sync）
5. 记录到 10-changelog.md；若过程中踩坑 → 写进 09-pitfalls.md
```

### 场景 C：线上出问题了

```
1. 先查 09-pitfalls.md，大概率已记录
2. 同步类问题 → 04-sync-design.md 的「排查手册」章节
3. 推送类问题 → 05-reminder-design.md 的「错误码对照表」章节
4. 登录类问题 → 06-auth-design.md
5. 解决后必须回写 09-pitfalls.md
```

---

## 四、代码结构速览

> 完整版见 [02-architecture.md](./02-architecture.md)，这里只给最粗的轮廓。

```
/workspace
├── docs/                  # 📚 你正在看的文档体系
├── tests/                 # ✅ 本地单测（npm test，约 3 秒跑完 295 项断言）
│   └── mocks/             #    wx-server-sdk 内存 Mock（🔴 必须严格复刻真实 SDK，见 P47）
├── miniprogram/           # 📱 小程序前端
│   ├── pages/             # ✅ 页面（只做 UI 和交互，不写业务逻辑）
│   │                      #    login / todo / done / plan-detail / profile
│   ├── packageA/          # ✅ 分包（编辑类页面，控制主包体积）
│   │                      #    plan-edit / member-pick
│   ├── components/        # ✅ 可复用 UI 组件
│   │                      #    plan-card / member-avatars / remind-badge / empty-state
│   ├── services/          # ✅ 业务服务层（页面唯一可调用的业务入口）
│   │                      #    auth.service / plan.service / member.service
│   ├── sync/              # ✅ M3 同步引擎（local-db / watermark / queue / index，可单测）
│   ├── core/              # ✅ 基础设施（cloud/storage/session/logger/error/event-bus）
│   ├── store/             # ✅ 全局状态（plan.store：委托 local-db + 发布订阅）
│   └── utils/             # ✅ 纯函数工具（uuid / date / format / promisify）
└── cloudfunctions/        # ☁️ 云函数
    ├── _shared/           # ✅ ⭐ 公共层源码（唯一真源，不要在这里直接编辑后忘了同步）
    ├── auth/              # ✅ 登录鉴权（含同步来的 common/）
    ├── init-db/           # ✅ 一次性数据库初始化 / 建索引 / 种子账号
    ├── plan/              # ✅ 计划增删改查（9 个 action）
    ├── sync/              # ✅ M3 增量同步拉取（pull 复合游标，见 P51）
    ├── remind-scan/       # ⬜ M4 ⏰ 定时触发器（扫描并推送提醒）
    ├── subscribe/         # ⬜ M4 订阅额度记账
    └── */common/          #   ← 由 _shared 同步而来（见 [P40](./09-pitfalls.md)）
```

> ✅ = 已实现　⬜ = 待开发（后面标注所属里程碑）

> ⚠️ **云函数公共层同步机制（关键）**：每个云函数目录里**不能** `require('../_shared/xxx')`（超限会报错，见 [P40](./09-pitfalls.md)）。所以 `_shared/` 是公共层**唯一真源**，部署前必须通过 `npm run sync:shared` 把它复制到每个云函数的 `common/` 子目录。改了 `_shared/` 后**必须重新同步**，否则线上跑的是旧代码。

**依赖方向铁律（不可违反）**

```
pages/components  →  services  →  sync / core  →  utils
                        ↓
                  cloudfunctions
```

- ❌ 页面**禁止**直接 `wx.cloud.callFunction`，必须走 `services/`
- ❌ 页面**禁止**直接 `wx.setStorageSync` 存业务数据，必须走 `core/storage.js`
- ❌ `core/` 和 `utils/` **禁止**反向引用 `services/` 和 `pages/`

---

## 五、三个必须先理解的核心机制

这三点是本项目的技术心脏，不理解就会写出错误代码。

### 1️⃣ 两套身份 ID（最容易搞混）

| ID | 是什么 | 用途 |
|---|---|---|
| `userId` | 自建账号的主键 | 业务身份：谁创建的、谁可见、谁完成的 |
| `openid` | 微信身份 | **仅用于推送订阅消息** |

一个 `userId` 可能绑定**多个** `openid`（同一账号在不同微信上登录）。二者通过 `user_bindings` 集合关联。
👉 详见 [06-auth-design.md](./06-auth-design.md)

### 2️⃣ 时间戳水位线同步（需求核心）

```
本地存 lastSyncAt（上次同步成功时的「服务器时间」）
    ↓
打开小程序 → 调 sync 云函数，带上 lastSyncAt
    ↓
云函数返回 updatedAt >= lastSyncAt 的记录（含被软删除的）+ 当前服务器时间
    ↓
本地按 planId 幂等覆盖合并 → 更新 lastSyncAt = 服务器时间
```

**三条铁律**：
- 水位线**只能用服务器时间**，绝不用手机本地时间（手机时间可被用户改）
- 删除**必须软删除**（`deleted: true`），硬删除会让本地留下幽灵数据
- 合并**必须幂等**（按 `planId` 覆盖），允许重复拉取

👉 详见 [04-sync-design.md](./04-sync-design.md)

### 3️⃣ 订阅消息额度池

微信订阅消息 = **用户授权一次，你才能推一次**。不记账就会推送失败。

```
用户点击「开启提醒」→ requestSubscribeMessage → accept
    ↓
额度 +1（记在 subscribe_quota 集合）
    ↓
定时触发器推送成功 → 额度 -1
    ↓
额度为 0 → 前端红点提示用户「续订」
```

👉 详见 [05-reminder-design.md](./05-reminder-design.md)

---

## 六、文档维护规则（重要）

为了让文档不腐烂，约定如下：

| 规则 | 说明 |
|---|---|
| **改代码必改文档** | 任何行为变更 → 更新 [10-changelog.md](./10-changelog.md) |
| **踩坑必记录** | 调试超过 30 分钟的问题 → 写进 [09-pitfalls.md](./09-pitfalls.md)，格式见该文件头部 |
| **改数据结构必同步三处** | [03-data-model.md](./03-data-model.md) + [04-sync-design.md](./04-sync-design.md) + 数据库索引 |
| **任务状态即时更新** | [08-roadmap.md](./08-roadmap.md) 的复选框保持真实，不要批量补勾 |
| **文档写「为什么」** | 代码写「怎么做」，文档重点写「为什么这么设计」和「不能怎么做」 |

---

## 七、当前项目状态

| 项 | 状态 |
|---|---|
| 阶段 | **M3 · 同步引擎 ✅**（时间戳水位线增量拉取 + 本地库下沉 + 离线队列 + 编排器） |
| 已完成 | M0 设计定稿 → M1 地基搭建 → M2 核心闭环 → M3 同步引擎 |
| 测试状态 | `npm test` → **295 项断言全过**（9 个用例文件，约 3 秒跑完，见 [tests/README.md](../tests/README.md)） |
| 下一步 | M4 · 提醒系统（订阅授权 + 定时推送 + 额度池）⭐ 真机联调多 |
| 待部署 | 云函数 `auth` / `init-db` / `plan` / **`sync`**（部署前先跑 `npm run sync:shared`） |
| 已知取舍 | UI 暂用原生自定义组件，TDesign 待「构建 npm」可用后平替（见 [P32](./09-pitfalls.md)） |
| 详细进度 | 见 [08-roadmap.md](./08-roadmap.md) |
| 部署手册 | 见 [12-deploy-guide.md](./12-deploy-guide.md)（上传云函数 / 配 env / 建索引 / 验收） |

---

*最后更新：见 [10-changelog.md](./10-changelog.md) 顶部条目*
