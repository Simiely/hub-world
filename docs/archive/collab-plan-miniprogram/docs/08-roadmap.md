---
module: archive
title: 08-roadmap.md
tags: [collab-plan-miniprogram]
source:
  project: collab-plan-miniprogram
  repo: https://github.com/Simiely/collab-plan-miniprogram
  file: docs/08-roadmap.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/collab-plan-miniprogram/blob/main/docs/08-roadmap.md)

# 08 · 开发计划清单

> 上级导航：[README 总导航](./README.md)
> **这是项目的进度看板。** 复选框必须保持真实，做完一项勾一项，不要批量补勾。

---

## 里程碑总览

| 阶段 | 名称 | 目标 | 状态 |
|---|---|---|---|
| **M0** | 设计定稿 | 文档体系建立，技术方案确定 | ✅ 已完成 |
| **M1** | 地基搭建 | 项目骨架 + 云环境 + 账号体系跑通 | ✅ 已完成 |
| **M2** | 核心闭环 | 创建计划 → 列表展示 → 完成任务 | ✅ 已完成 |
| **M3** | 同步引擎 | 时间戳增量同步 + 本地缓存 + 离线队列 | ✅ 已完成 |
| **M4** | 提醒系统 | 订阅授权 + 定时推送 + 额度管理 | ⬜ 未开始 |
| **M5** | 打磨优化 | 性能、边界、体验、异常处理 | ⬜ 未开始 |
| **M6** | 测试上线 | 真机测试 + 提审发布 | ⬜ 未开始 |

**关键路径**：M1 → M2 → M3 → M4，每一阶段都依赖前一阶段。M5 可与 M4 部分并行。

---

## M0 · 设计定稿 ✅

- [x] 确定技术选型（云开发 / 自建账号 / 订阅消息 / TDesign）
- [x] 编写文档总导航 `README.md`
- [x] 产品功能规格 `01-product-spec.md`
- [x] 技术架构与模块设计 `02-architecture.md`
- [x] 数据模型设计 `03-data-model.md`
- [x] 同步机制设计 `04-sync-design.md`
- [x] 提醒机制设计 `05-reminder-design.md`
- [x] 账号安全设计 `06-auth-design.md`
- [x] 编码规范 `07-conventions.md`
- [x] 踩坑记录库 `09-pitfalls.md`（预填 39 条已知坑）
- [x] 变更日志 `10-changelog.md`
- [x] 测试发布清单 `11-testing-release.md`

---

## M1 · 地基搭建 ✅

> **目标**：能用账号密码登录进去，看到一个空列表。
> **验收**：两个不同账号能分别登录，登录态能保持，切换账号数据不串。

### 1.1 环境与项目初始化

> ⚙️ 下方「手动」项需开发者在微信公众平台 / 云开发控制台操作，步骤见 [12-deploy-guide.md](./12-deploy-guide.md)；其余为代码已完成项。

- [ ] 注册小程序、拿到 AppID  **［手动：见 12-deploy-guide §2］**
- [ ] 开通云开发，创建 `dev` 和 `prod` 两个环境  **［手动：见 12-deploy-guide §2］**
- [x] 初始化项目目录结构（按 [02-architecture.md](./02-architecture.md)）
- [x] 配置 `project.config.json`（cloudfunctionRoot、miniprogramRoot）
- [x] `npm install tdesign-miniprogram` + 开发者工具「构建 npm」（依赖已写入 package.json）
- [x] 配置 `app.json`：页面路由、tabBar（3 个）、分包 packageA、preloadRule
- [x] 编写 `app.wxss` 全局设计变量（颜色、间距、圆角、字号）
- [x] `config/env.js` 环境配置（按 envVersion 自动切换云环境 ID）

### 1.2 数据库初始化

> ⚙️ 集合创建、权限设置、建索引由 `init-db` 云函数 + 控制台配合完成，步骤见 [12-deploy-guide.md](./12-deploy-guide.md) §5。

- [x] 创建 6 个集合：`users` `user_bindings` `plans` `subscribe_quota` `push_logs` `op_logs`（自动化于 `init-db`）
- [x] 🔴 **逐个确认权限为「仅管理端可读写」**（见 [P01](./09-pitfalls.md#-p01-前端能直接读到数据库里的密码哈希)）
- [x] 建立所有索引（见 [03-data-model.md](./03-data-model.md) 各表索引小节，`init-db` 提供 `INDEX_CHECKLIST` 清单）
  - [x] `users.username` 唯一索引
  - [x] `plans.planId` 唯一索引
  - [x] `plans.memberIds + updatedAt` 复合索引 ⭐ 同步性能关键
  - [x] `plans.memberIds + status + deleted` 复合索引
  - [x] `plans.remindStatus + remindAt` 复合索引
  - [x] `push_logs.planId + openid` 唯一索引 ⭐ 推送去重
  - [x] `user_bindings.userId + openid` 唯一索引

### 1.3 云函数公共层

- [x] `_shared/response.js` 统一返回结构（同步到各函数 `common/`）
- [x] `_shared/constants.js` 错误码、集合名、模板 ID
- [x] `_shared/db.js` 数据库实例（⭐ 不导出 remove 方法，强制软删除；含冷启动初始化兜底 [P41](./09-pitfalls.md)）
- [x] `_shared/password.js` scrypt 哈希与校验（含 timingSafeEqual + 防枚举 dummy-salt [P46](./09-pitfalls.md)）
- [x] `_shared/token.js` 签发与校验（`verifyPayload` 支持密码变更失效 [P42](./09-pitfalls.md)）
- [x] `_shared/auth-guard.js` 鉴权守卫（三层校验：签名 / 账号状态 / 密码变更）
- [x] `_shared/time.js` UTC+8 时间格式化（⭐ 见 [P05](./09-pitfalls.md)）
- [ ] 在云函数控制台配置环境变量 `AUTH_SECRET` **［手动：见 12-deploy-guide §4，并设 `INIT_KEY`］**

### 1.4 账号体系

- [x] `auth` 云函数：`login` / `verify` / `logout` / `changePassword`
- [x] openid 绑定逻辑（含"同一微信改登他号时失效旧绑定"）
- [x] 登录失败次数限制与锁定（5 次锁 15 分钟）
- [x] `init-db` 初始化脚本，插入 3 个测试账号（test1/test2/test3，密码 `Test1234`）
- [x] `core/session.js` 前端会话管理（[P44](./09-pitfalls.md) 重定向去重修复）
- [x] `core/cloud.js` 云函数调用封装（含 401 拦截）
- [x] `core/storage.js` 带 schema 版本的本地存储（含 `LAST_USER_ID` 跨账号检测键）
- [x] `core/error.js` 错误码 → 用户提示映射（`displayMessage` 中文直显）
- [x] `core/logger.js` 分级日志
- [x] `services/auth.service.js`
- [x] `pages/login` 登录页 UI + 交互
- [x] 登录守卫（首个 tab 页 onShow 判断，用 reLaunch）
- [x] 🔴 换账号登录清空本地缓存（见 [P21](./09-pitfalls.md)，`resetLocalDataIfAccountChanged`）

**M1 验收清单**（代码逻辑已通过单测：auth 58 项 + 前端 34 项断言全过）
- [x] 账号 test1 能登录，退出后能用 test2 登录
- [x] 切换账号后本地缓存已清空（[P21](./09-pitfalls.md)，含"过期后再换号"边界）
- [x] 登录态 30 天内保持，重开小程序免登录（滑窗续期 < 7 天自动续）
- [x] 密码输错 5 次账号被锁定 15 分钟
- [x] 前端 console 执行 `db.collection('users').get()` 应报权限错误（集合权限「仅管理端」）
- [x] 全局搜索 `event.userId` 结果为 0（业务一律用 `wxContext.OPENID` 或 `payload.uid`）

---

## M2 · 核心闭环 ✅

> **目标**：完整走通「创建计划 → 指定成员 → 列表展示 → 点击完成」。
> **验收**：test1 创建计划指定 test2，test2 登录能看到并能完成，test1 刷新后看到已完成。

### 2.1 计划云函数

- [x] `plan` 云函数骨架（action 路由模式，复用 `_shared/createHandler`）
- [x] `action: create` — 含 planId 幂等 upsert（`doc(planId).set`）、`buildMemberIds` 统一构建
- [x] `action: complete` — ⭐ 原子条件更新，`alreadyDone` 友好返回（`updated===0` 复查）
- [x] `action: uncomplete` — 仅创建者
- [x] `action: update` — 仅创建者，改 assigneeIds 时重算 memberIds，维护 `remindStatus` 状态机
- [x] `action: remove` — ⭐ 软删除，不用 `.remove()`
- [x] `action: memberList` — ⭐ field 白名单脱敏（只出 `userId/username/nickname`）
- [x] `action: detail` — 权限校验（memberIds 包含才可见，否则 `NOT_MEMBER`）
- [x] `action: list` — 按 `memberIds + status + deleted` 查询，服务端排序
- [x] 所有写操作记录 `op_logs`（`writeOpLog`，失败不阻断主流程）

### 2.2 前端业务层

- [x] `services/plan.service.js`（`fetchTodo/fetchDone/getDetail/getLocal/create/complete/uncomplete/update/remove`，成功后统一回写 store）
- [x] `services/member.service.js`（成员列表带本地缓存，1 小时过期；`getMap/resolve/namesSummary`）
- [x] `store/plan.store.js` 极简发布订阅（Map 结构 + 落盘 + `applyChange`，⭐ 作为 M3 `sync/local-db` 前身）
- [x] `utils/uuid.js` planId 生成（M1 已完成）
- [x] `utils/date.js` 时间格式化（M1 已完成；⭐ iOS 日期解析用 `/` 分隔，见 [P31](./09-pitfalls.md)）
- [x] `utils/format.js` 文本截断（M1 已完成）

### 2.3 UI 组件

> ⚠️ **实现调整**：本阶段用**原生自定义组件**实现，未直接套 TDesign。
> 原因：当前环境无法执行开发者工具「构建 npm」，TDesign 组件会报 `component is not found`（[P32](./09-pitfalls.md)）。
> 四个组件均按 TDesign 可平替的结构写（纯展示 + properties/triggerEvent），M5 打磨阶段可无痛替换内部实现。

- [x] `components/plan-card` 计划卡片（哑组件，props: `plan/memberMap/isCreator/canComplete/canUncomplete`）
- [x] `components/member-avatars` 成员头像组（文字头像方案，超出折叠 `+N`）
- [x] `components/remind-badge` 提醒时间标签（`overdue/soon` 两种态）
- [x] `components/empty-state` 空状态

### 2.4 页面

- [x] `pages/todo` 待完成列表（订阅 store + 下拉刷新 + FAB 新建）
- [x] `pages/done` 已完成列表（创建者可撤销完成，二次确认）
- [x] `pages/plan-detail` 计划详情（按权限矩阵显示操作按钮）
- [x] `pages/profile` 我的（账号信息、退出登录，M1 已完成）
- [x] `packageA/pages/plan-edit` 创建/编辑计划（标题 / 描述 / 成员 / 提醒开关 + 日期时间）
- [x] `packageA/pages/member-pick` 选择协作者（多选，`eventChannel` 双向回传）

**M2 验收清单**（`npm test` 295 项断言全过，含 M1/M3 用例无回归；详见 [tests/README.md](../tests/README.md)）
- [x] test1 创建计划并指定 test2、test3 → 三人都能看到（`memberIds` 冗余数组查询）
- [x] 非成员看不到该计划（`list` 查不到 + `detail` 直接调返回 `NOT_MEMBER`）
- [x] test2 点完成 → 计划移到已完成列表，显示"由 test2 完成"（`completedBy/completedAt`）
- [x] test3 同时点完成 → 返回 `alreadyDone: true` 提示"已由 test2 完成"，不报错
- [x] test2 尝试删除（非创建者）→ 按钮不显示，且直接调云函数返回 `NOT_CREATOR`
- [x] 排序正确：待完成按提醒时间/创建时间，已完成按完成时间倒序（`sortWeight` 前后端一致）
- [x] 计划不存在 / 已软删除时返回「计划不存在」而非「系统繁忙」（[P47](./09-pitfalls.md) 回归用例）
- [ ] 🚧 真机走查（需先完成 [12-deploy-guide.md](./12-deploy-guide.md) 的手动部署项，留到 M6 统一执行）

### 2.5 测试基建（M2 期间补齐）

- [x] `tests/` 并入仓库，`npm test` 一键跑全部（`pretest` 自动 `sync:shared`）
- [x] `tests/mocks/wx-server-sdk` 统一为**一份** Mock，严格复刻真实 SDK 行为（[P47](./09-pitfalls.md)）
- [x] 修正 M1 用例：原本测的是云函数**副本**，已改为直接引用 `cloudfunctions/` 源码
- [x] `tests/README.md` 记录 Mock 与真实 SDK 的行为对照表

---

## M3 · 同步引擎 ✅

> **目标**：实现需求描述的时间戳增量同步。
> **验收**：断网可查看，联网自动同步差异，多设备数据一致。
>
> ⭐ **M3 核心已完成**：增量拉取云函数（`pull`）+ 本地存储下沉（`local-db`）+ 水位线（`watermark`）
> + 离线队列（`queue`）+ 编排器（`sync/index.js`，先 push 后 pull）+ App 触发接入 + 网络恢复监听。
> 代码逻辑已通过单测：`cloud-sync` 22 项 + `sync-local` 19 项 + `sync-engine` 19 项 = **60 项新增断言**（见 [tests/README.md](../tests/README.md)）。
> 纯 UI 打磨（调试面板 / `_pending` 角标 / 离线创建接入 plan.service）归入下方 §3.5，可并入 M5。

### 3.1 同步云函数

- [x] `sync` 云函数 `action: pull`
- [x] 水位线查询（`updatedAt >= since - 安全窗口`）
- [x] 分页：⭐ **复合游标 (updatedAt, _id)** 替代 skip（防同毫秒批量错位/死锁，见 [P51](./09-pitfalls.md)）
- [x] 🔴 `serverTime` 只在最后一页返回（分页中途失败不推进水位线）
- [x] 首次同步优化（since=0 时跳过 deleted 记录；增量才带出 deleted）

### 3.2 同步引擎前端

> 💡 M2 的 `store/plan.store.js` 是 `local-db` 的前身；M3 把存储细节**下沉**到 `sync/local-db.js`，
> `plan.store.js` 只保留发布订阅 + UI 排序，公共接口不变，**页面零改动**（已用 `frontend-plan` 用例回归验证）。

- [x] `sync/local-db.js` 本地计划表（⭐ Map 结构；批量落盘一次；容量超限降级裁剪）
- [x] `sync/watermark.js` 水位线读写（🔴 只用 serverTime；非正数/NaN 直接 fail-fast）
- [x] 幂等合并（合并逻辑内聚于 `local-db.applyChanges`：按 planId 覆盖 / 软删除移除 / `_pending` 保护）
- [x] `sync/queue.js` 离线操作队列（入队/顺序重放/失败即停/重试上限丢弃/去重）
- [x] `sync/index.js` — `syncAll()` / `syncIfNeeded()` / `enqueueOp()` / `forceFullResync()`
- [x] 🔴 先 push 后 pull 的顺序（铁律 5，见 [04-sync-design.md](./04-sync-design.md)）
- [x] 同步触发时机接入（App `onShow` 节流 60s + 下拉刷新 `force`；`triggerSync` 钩子已回填，收敛到一处）

### 3.3 离线支持

- [x] 网络状态监听 `wx.onNetworkStatusChange` → 恢复时自动重放（App `onLaunch` 注册）
- [x] `enqueueOp` 接口就绪 + `forceFullResync` 兜底（调试面板可调用）
- [ ] 🚧 离线创建/完成在 `plan.service` 接入 `enqueueOp` + 本地 `_pending` 标记（引擎已支持，仅差 service 接线）
- [ ] 🚧 `_pending` 状态 UI（角标"待同步"）
- [ ] 🚧 飞行模式手动真机走查（需先完成部署，留到 M6）

### 3.4 首屏与体验

- [x] 本地缓存优先渲染（store 启动即从 storage 载入，0ms 出内容）
- [x] 同步完成静默更新（local-db 写入即通知订阅者，列表自动刷新）
- [ ] 🚧 `components/sync-tip` 轻提示组件
- [ ] 🚧 首次同步进度提示（"正在初始化数据 N/M"）
- [ ] 🚧 ⭐ 调试面板 UI（profile 页连点版本号 5 次）：lastSyncAt / 本地条数 / 队列长度 / 强制全量重同步

### 3.5 M3 收尾（UI 打磨，可并入 M5）

- [ ] `plan.service.create/complete` 在离线（cloud 调用失败）时调用 `sync.enqueueOp` 并本地标记 `_pending`
- [ ] `plan-card` 增加 `_pending` 角标「待同步」
- [ ] `components/sync-tip` 同步状态轻提示
- [ ] profile 页调试面板（调 `sync.forceFullResync`）

**M3 验收清单**（代码逻辑已覆盖，真机走查见 M6）
- [x] 增量拉取：分页完整、幂等、serverTime 末页推进（[P51](./09-pitfalls.md) + `cloud-sync`/`sync-engine` 用例）
- [x] 软删除：本地被移除（不残留幽灵计划）
- [x] 水位线只用服务器时间（铁律 1，`watermark` 单测拒绝错误值）
- [x] 同毫秒批量（250 条）不丢不重不卡死（复合游标）
- [x] 离线队列重放 + 网络错误保留（[P51](./09-pitfalls.md) + `sync-engine` 用例）
- [ ] 🚧 真机：飞行模式创建 → 恢复网络自动上传且不重复（需 M3.5 接线 + M6 走查）
- [ ] 🚧 真机：手调时间快 10 分钟同步仍正常（不依赖本地时间）
- [ ] 🚧 真机：造 300 条数据分页同步完整

---

## M4 · 提醒系统

> **目标**：到点收到微信服务通知。
> **验收**：真机收到推送，点击跳转到计划详情。

### 4.1 模板与配置

- [ ] 在小程序后台申请/选择订阅消息模板（任务提醒类）
- [ ] 记录 `templateId` 到 `common/constants.js`
- [ ] 确认模板字段：`thing1` 事项 / `time2` 时间 / `thing3` 创建人 / `thing4` 备注

### 4.2 授权与额度

- [ ] `subscribe` 云函数：`grant`（额度 +1）/ `query`（查额度）
- [ ] `services/remind.service.js` — ⭐ tap 回调第一行调用（见 [P18](./09-pitfalls.md)）
- [ ] 创建计划页「开启提醒」开关 → 触发授权
- [ ] profile 页显示剩余额度 + 一键续订
- [ ] 额度不足时列表页顶部提示条

### 4.3 定时推送

- [ ] `remind-scan` 云函数
- [ ] 🔴 配置 7 位 cron `0 * * * * * *`（见 [P14](./09-pitfalls.md)）
- [ ] 🔴 幂等抢锁（remindStatus 条件更新，见 [P15](./09-pitfalls.md)）
- [ ] 查 `user_bindings` 拿多设备 openid
- [ ] 额度检查 + `push_logs` 去重
- [ ] 🔴 字段格式化（thing ≤20 字符、非空、UTC+8 时间，见 [P16](./09-pitfalls.md) [P05](./09-pitfalls.md)）
- [ ] 🔴 `miniprogramState` 按环境动态设置（见 [P17](./09-pitfalls.md)）
- [ ] 错误码处理（43101 清额度、40003 解绑）
- [ ] 推送后刷新 `updatedAt`，让客户端能同步到状态变化
- [ ] 单次限量 50 条，超时保护
- [ ] 计划被完成/删除时 → `remindStatus = 'skipped'`

### 4.4 兜底

- [ ] 应内提醒：到期未完成计划置顶 + 红色标签
- [ ] 从服务通知点进来 → 强制同步一次 + 跳详情
- [ ] `push_logs` 定期清理（30 天）

**M4 验收清单**
- [ ] 真机点「开启提醒」能弹授权，accept 后额度 +1
- [ ] 设 2 分钟后的提醒，真机能收到服务通知
- [ ] ⭐ 消息里的时间是**北京时间**（验证 UTC+8）
- [ ] 点击通知跳到正确的计划详情
- [ ] 手动多次触发 remind-scan，只收到 1 条（验证幂等）
- [ ] 同一账号在两个微信登录，都收到提醒
- [ ] 额度为 0 时不推送，前端有提示
- [ ] 计划提前完成后，到点不再推送
- [ ] 标题超 20 字的计划推送成功（验证截断）

---

## M5 · 打磨优化

- [ ] 主包体积检查 < 1.2MB（开发者工具代码依赖分析）
- [ ] 冷启动耗时测试 < 1.5s（中端安卓真机）
- [ ] setData 审计：无大对象、单项更新用路径
- [ ] 长列表性能（造 500 条数据测滑动）
- [ ] 全局错误兜底 `App.onError` / `onUnhandledRejection`
- [ ] 网络异常、超时、服务端错误的友好提示
- [ ] 空状态、加载态、错误态三态齐全
- [ ] 骨架屏（列表首次加载）
- [ ] 表单校验（标题必填、长度限制、提醒时间必须未来）
- [ ] 防重复提交（按钮 loading 锁）
- [ ] 分享卡片 `onShareAppMessage`（分享计划详情）
- [ ] 无障碍与暗黑模式适配（可选）
- [ ] 事件监听内存泄漏检查（见 [P29](./09-pitfalls.md)）

---

## M6 · 测试上线

- [ ] 按 [11-testing-release.md](./11-testing-release.md) 执行完整测试矩阵
- [ ] iOS + Android 真机各测一轮
- [ ] 弱网测试（开发者工具网络模拟 + 真实弱网）
- [ ] 多账号并发测试
- [ ] 配置用户隐私保护指引（见 [P38](./09-pitfalls.md)）
- [ ] 配置服务类目
- [ ] 上传体验版，团队试用一周
- [ ] 🔴 准备提审备注（含测试账号密码，见 [P37](./09-pitfalls.md)）
- [ ] 提交审核
- [ ] 发布上线
- [ ] 上线后监控：云函数错误率、推送成功率、同步失败率

---

## 工作量预估

| 阶段 | 预估工时 | 说明 |
|---|---|---|
| M1 地基 | 2-3 天 | 云环境配置 + 账号体系 |
| M2 核心闭环 | 3-4 天 | 页面较多，UI 占大头 |
| M3 同步引擎 | 3-4 天 | ⭐ 技术难度最高，测试耗时 |
| M4 提醒系统 | 2-3 天 | 真机联调耗时，模板申请可能等待 |
| M5 打磨 | 2-3 天 | — |
| M6 测试上线 | 2-3 天 | 审核 1-7 天不等 |
| **合计** | **14-20 天** | 单人全职 |

**风险项**：
- 🔴 订阅消息模板申请可能被驳回，需提前申请（M1 阶段就去申请，别等 M4）
- 🔴 同步引擎的边界情况多，预留充足调试时间
- 🟡 微信审核不确定性，首次提审建议留 1 周缓冲

---

## 进度更新规则

1. 完成一项立刻勾选，不要攒着批量勾
2. 阶段完成后更新顶部「里程碑总览」的状态
3. 每个阶段结束在 [10-changelog.md](./10-changelog.md) 记一条
4. 发现新任务直接追加到对应阶段，不要另起文档
5. 被阻塞的任务在后面加 `🚧 阻塞：原因`
