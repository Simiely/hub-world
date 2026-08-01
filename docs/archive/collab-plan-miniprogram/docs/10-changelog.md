---
module: archive
title: 10-changelog.md
tags: [collab-plan-miniprogram]
source:
  project: collab-plan-miniprogram
  repo: https://github.com/Simiely/collab-plan-miniprogram
  file: docs/10-changelog.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/collab-plan-miniprogram/blob/main/docs/10-changelog.md)

# 10 · 更新日志

> 上级导航：[README 总导航](./README.md)
> **最新的在最上面。** 每次改动后追加一条，不要等到发版才补。

---

## 记录格式

```markdown
## [版本号] - YYYY-MM-DD

### 新增 Added
- 功能描述

### 变更 Changed
- 行为变化描述（⚠️ 标注是否影响老用户）

### 修复 Fixed
- 修复的问题（关联 09-pitfalls.md 编号）

### 移除 Removed
- 删除的功能

### 数据结构 Schema
- ⚠️ 字段变更（是否需要提升 SCHEMA_VERSION）

### 影响面 Impact
- 需要重新部署的云函数 / 需要重建的索引 / 是否强制重同步
```

**版本号规则**（语义化版本）
- 主版本 `x.0.0`：不兼容的重大变更（如数据结构大改，需强制重同步）
- 次版本 `0.x.0`：新功能，向下兼容
- 修订号 `0.0.x`：修 bug

---

## [0.1.0] - 2026-07-31

### 新增 Added
- 建立完整文档体系（12 篇），以 `README.md` 为总导航入口
- 确定技术选型：微信云开发 CloudBase + 自建账号密码体系 + 订阅消息 + TDesign
- 完成产品功能规格定义（账号 / 计划 / 提醒 / 同步 四大模块，共 24 项功能点）
- 完成技术架构设计：六层模块划分（pages → services → sync/core → utils）与依赖方向铁律
- 完成数据模型设计：6 张集合、字段定义、索引规划、权限红线
- 完成同步机制设计：服务器时间戳水位线 + 增量拉取 + 软删除 + 离线队列 + 幂等合并
- 完成提醒机制设计：定时触发器 + 订阅额度池 + 三层推送去重
- 完成账号安全设计：scrypt 密码哈希 + 自签名 Token + 账号↔openid 绑定表
- 编写编码规范与目录归属决策树
- 编写开发计划清单（M0-M6 共 7 个里程碑，约 120 个任务项）
- 预填踩坑记录库 39 条已知高危坑（含 15 条 🔴 级）
- 编写测试与发布检查清单

### 数据结构 Schema
- 初始定义，`SCHEMA_VERSION = 1`
- 集合：`users` / `user_bindings` / `plans` / `subscribe_quota` / `push_logs` / `op_logs`

### 关键决策记录 Decisions
| 决策 | 选择 | 理由 |
|---|---|---|
| 后端 | 微信云开发 | 免服务器、免备案、自带定时触发器 |
| 账号体系 | 自建账号密码 | 需求要求「指定账号登录」，账号需跨微信复用 |
| 身份模型 | userId 与 openid 分离，用绑定表关联 | 自建账号 + 微信推送的必然结果 |
| 同步策略 | 服务器时间戳水位线 + 幂等合并 | 需求明确要求时间戳比对与差异同步 |
| 删除方式 | 强制软删除 | 硬删除会导致增量同步产生幽灵数据 |
| 完成并发 | 原子条件更新，非"先查后写" | 需求「至少一人完成」必然存在并发点击 |
| 提醒方式 | 订阅消息 + 自建额度池 | 微信不提供可靠的额度查询接口 |
| UI 库 | TDesign 按需引入 | 官方出品、视觉贴近原生、审核友好 |
| 状态管理 | 自研极简发布订阅 | 避免引入 MobX 增加包体积 |
| 云函数组织 | action 路由合并 | 减少函数数量，降低冷启动概率 |

### 影响面 Impact
- 无代码，纯文档阶段
- 下一步进入 M1（地基搭建），见 [08-roadmap.md](./08-roadmap.md)

---

## [0.2.0] - 2026-07-31

> M1 · 地基搭建完成：项目骨架 + 云函数公共层 + 账号体系跑通（代码逻辑通过单测，auth 58 项 / 前端 34 项断言全过）。

### 新增 Added
- **云函数公共层 `_shared/`**（唯一真源，经 `npm run sync:shared` 同步到各函数 `common/`）
  - `response.js` 统一返回结构；`constants.js` 错误码 / 集合名 / 模板 ID
  - `db.js` 数据库实例（不导出 `remove`，强制软删除；含冷启动 `cloud.init` 兜底，见 [P41](./09-pitfalls.md)）
  - `password.js` scrypt 哈希与校验（timingSafeEqual + 防枚举 dummy-salt，见 [P46](./09-pitfalls.md)）
  - `token.js` 自签名 Token（`verifyPayload` 支持密码变更即失效，见 [P42](./09-pitfalls.md)）
  - `auth-guard.js` 三层鉴权守卫（签名 → 账号状态 → 密码变更）；`time.js` UTC+8 格式化
- **`auth` 云函数**：`login` / `verify` / `logout` / `changePassword`
  - 登录失败 5 次锁定 15 分钟；登录防枚举（统一报错 + 常量时间假哈希）
  - openid 绑定：同一微信改登他号时失效旧绑定；登出解绑（不再推送）
  - Token 滑窗续期（剩余 < 7 天自动续）
- **`init-db` 云函数**：`status` / `init` / `resetPassword`；`INIT_KEY` 环境变量守卫（默认拒绝）
  - 自动建 6 集合 + 注入 12 索引清单 `INDEX_CHECKLIST` + 种子账号 test1/test2/test3（密码 `Test1234`）
- **前端基础设施层**：`core/{cloud,session,storage,error,logger,event-bus}.js`
  - `cloud.call` 封装（含 401 拦截 → 跳登录）；`session` 登录守卫（[P44](./09-pitfalls.md) 重定向去重修复）
  - `storage` 带 schema 版本 + `LAST_USER_ID` 跨账号检测键（[P21](./09-pitfalls.md)）
  - `error.displayMessage` 中文错误直显
- **`services/auth.service.js`**：登录 / 静默校验 / 登出 / 改密；账号切换清空本地业务数据
- **页面**：`pages/login`、`pages/todo`（启动页）、`pages/done`、`pages/profile`、`pages/plan-detail`，分包 `packageA/pages/{plan-edit,member-pick}` 占位
- **部署手册 [12-deploy-guide.md](./12-deploy-guide.md)**：云函数上传 / env 变量 / 初始化数据库与建索引 / M1 验收自检 / 上线前清单

### 变更 Changed
- 启动页改为 `pages/todo`（登录页置于 `pages` 列表末尾，由守卫 `reLaunch`），见 [04](./04-sync-design.md)

### 修复 Fixed
- **[P40](./09-pitfalls.md)** 云函数不能 `require` 父目录 → `_shared/` 同步到各函数 `common/`
- **[P41](./09-pitfalls.md)** 冷启动 `cloud.database()` 早于 `cloud.init` 崩溃 → `db.js` 幂等兜底初始化
- **[P42](./09-pitfalls.md)** 改密后旧 Token 仍可用 → 守卫比对 `pwdChangedAt` 与 Token `iat`
- **[P43](./09-pitfalls.md)** Node SDK 无法建索引 → `init-db` 输出手动建索引清单
- **[P44](./09-pitfalls.md)** 登录重定向 1 秒时间窗吞掉合法跳转 → 改用 `isOnLoginPage()` 判定
- **[P45](./09-pitfalls.md)** `promisify(wx.xxx)` 丢失 `this` 且加载即读 → 改为箭头包裹
- **[P46](./09-pitfalls.md)** 登录接口可被枚举 → 缺失账号走常量时间假哈希

### 数据结构 Schema
- `users`：新增 `failedCount` / `lockedUntil` / `pwdChangedAt` 字段（密码变更失效机制）
- `user_bindings`：绑定表驱动账号↔openid 多对多
- `SCHEMA_VERSION = 1`（未变更）

### 关键决策记录 Decisions
| 决策 | 选择 | 理由 |
|---|---|---|
| 公共层分发 | `_shared/` 唯一真源 + `sync:shared` 脚本复制 | 云函数目录隔离，勿手改 `common/` |
| 账号切换 | 前端用 `LAST_USER_ID` 检测 + 清空业务缓存 | 解决会话过期后漏清缓存（[P21](./09-pitfalls.md)） |
| Token 失效 | `pwdChangedAt` vs `iat` 服务端比对 | 改密即踢所有设备，无需中心化黑名单 |

### 影响面 Impact
- 需部署云函数：`auth`、`init-db`
- 需配置环境变量：`AUTH_SECRET`（Token 签名）、`INIT_KEY`（`init-db` 守卫）
- 需在控制台手动：创建云环境、将 6 集合权限设为「仅管理端可读写」、按 `INDEX_CHECKLIST` 建 12 索引
- 下一步进入 M2（核心闭环：创建计划 → 列表展示 → 完成），见 [08-roadmap.md](./08-roadmap.md)

---

## [0.4.0] - 2026-07-31

> M3 · 同步引擎核心完成：时间戳增量拉取 + 本地存储下沉 + 离线队列 + 编排器 + App 触发接入。
> `npm test` **295 项断言全过**（M3 新增 `cloud-sync` 22 + `sync-local` 19 + `sync-engine` 19 = 60 项，无回归）。

### 新增 Added

- **`sync` 云函数 `action: pull`**（增量拉取「我可见」的计划变更）
  - 水位线 `since - SYNC_SAFE_WINDOW(2000)` 安全回退；`memberIds` 数组包含匹配（走多键索引）
  - 分页：⭐ **复合游标 (updatedAt, _id)** 替代 skip，根治同毫秒批量错位/死锁（见 [P51](./09-pitfalls.md)）
  - `serverTime` 只在最后一页返回（分页中途失败不推进水位线，铁律）
  - 首次同步（`since<=0`）跳过 `deleted`；增量才带出 `deleted: true`
- **`miniprogram/sync/local-db.js`** 存储下沉层
  - Map 结构 + 批量落盘一次（`flush`）；容量超限降级裁剪（P12，按 updatedAt 淘汰最旧，最坏清空不崩）
  - `applyChanges` 幂等合并：按 planId 覆盖 / 软删除移除 / 保护 `_pending` 离线草稿（铁律 4 + 7.3）
- **`miniprogram/sync/watermark.js`** 水位线读写（🔴 只用 serverTime；非正数/NaN/负数/undefined 直接 fail-fast）
- **`miniprogram/sync/queue.js`** 离线操作队列（入队 / 顺序重放 / 失败即停 / 重试上限 5 丢弃 / 去重 / 上限）
- **`miniprogram/sync/index.js`** 编排器
  - `syncAll`（先 push 后 pull，铁律 5）/ `syncIfNeeded`（60s 节流）/ `enqueueOp` / `forceFullResync`
  - 广播 `SYNC_DONE` / `SYNC_FAIL`；防重入
- **`store/plan.store.js` 重构**：存储细节下沉到 `local-db`，只保留发布订阅 + UI 排序，公共接口不变（**页面零改动**，已用 `frontend-plan` 用例回归验证）
- **`app.js` 接入**：`triggerSync` 回填 `syncIfNeeded` 钩子（同步入口收敛到一处，见 [P13](./09-pitfalls.md)）；`onLaunch` 注册 `wx.onNetworkStatusChange` 联网恢复即同步
- **测试**：`cloud-sync.test.js`（22）/ `sync-local.test.js`（19）/ `sync-engine.test.js`（19），共 60 项

### 变更 Changed

- `plan.store.js` 不再自持内存 Map，委托 `local-db`（设计文档五「数据本地唯一可信副本」的下沉实现）
- `sync` 云函数分页由设计文档伪代码的 `skip` 改为复合游标（同毫秒 > 单页上限时不丢不重不卡死）

### 修复 Fixed

- **[P51](./09-pitfalls.md)** 🔴 **同步分页同毫秒批量死锁**：① skip 分页在同毫秒（>100 条）下无稳定次级排序键，错位漏读/重读；
  ② 续页若沿用 `since<=0` 全量查询会永远返回第一页导致游标卡死。**修复**：`(updatedAt, _id)` 复合游标严格续接 + 续页优先级高于 `since`。

### 数据结构 Schema

- 无新增字段（`sync` 视图比 `plan` 视图多带 `deleted`，不含 `_id`）
- `SCHEMA_VERSION = 1`（未变更，本地缓存结构兼容）

### 关键决策记录 Decisions

| 决策 | 选择 | 理由 |
|---|---|---|
| 分页 | 复合游标 (updatedAt, _id) 替代 skip | 同毫秒批量不丢不重不卡死（[P51](./09-pitfalls.md)） |
| 存储 | `plan.store` 下沉为 `local-db` | 单一存储出口，页面零改动，便于 M5 平滑替换 |
| 离线 | 队列重放 + `_pending` 保护 | 先 push 后 pull，避免离线草稿被服务器版本覆盖（铁律 5） |

### 影响面 Impact

- 需**新增部署**云函数：`sync`（首次上线必须上传）
- 前端新增 `miniprogram/sync/` 四文件；`app.js` 已接 `triggerSync`，无需改页面
- 真机联调见 M6：飞行模式创建、跨设备同步、调时间验证不依赖本地时间
- 下一步进入 M4（提醒系统），见 [08-roadmap.md](./08-roadmap.md)

---

## [0.3.0] - 2026-07-31

> M2 · 核心闭环完成：创建计划 → 指定成员 → 列表展示 → 点击完成 全链路跑通。
> `npm test` **235 项断言全过**（含 M1 用例无回归），约 3 秒跑完。

### 新增 Added

- **`plan` 云函数**（action 路由，9 个 action）
  - `create` — ⭐ 客户端生成 `planId` + `doc(planId).set` 幂等写入，为 M3 离线创建预留
  - `list` — 按 `memberIds + status + deleted` 查询，服务端排序（待完成：有提醒的按 `remindAt` 升序在前，其余按 `createdAt` 降序；已完成：按 `completedAt` 降序）
  - `detail` — 成员校验，非成员返回 `NOT_MEMBER`
  - `complete` — ⭐ **原子条件更新**（`{status:'pending', deleted:false}` 作为更新条件），并发下第二个点击者拿到 `alreadyDone: true` 而不是报错
  - `uncomplete` / `update` / `remove` — 仅创建者，`remove` 走软删除
  - `memberList` — field 白名单脱敏，只返回 `userId / username / nickname`
  - 写操作统一落 `op_logs`（`writeOpLog` 失败不阻断主流程）
- **前端业务层**
  - `store/plan.store.js` — Map 结构内存表 + 本地落盘 + 发布订阅（`upsert / upsertMany / applyChange / remove / getList / subscribe`）
  - `services/plan.service.js` — 云函数调用 + **成功后统一回写 store**，页面只订阅 store，不各自持有列表
  - `services/member.service.js` — 成员列表 1 小时本地缓存，`getMap / resolve / namesSummary`
- **UI 组件（原生自定义组件）**：`plan-card` / `member-avatars` / `remind-badge` / `empty-state`
- **页面真实逻辑**
  - `pages/todo` 待完成（订阅 store、下拉刷新、FAB 新建、卡片直接完成）
  - `pages/done` 已完成（创建者可撤销完成，带二次确认）
  - `pages/plan-detail` 详情（按权限矩阵渲染操作按钮）
  - `packageA/pages/plan-edit` 创建/编辑（标题 / 描述 / 成员选择 / 提醒开关 + 日期时间）
  - `packageA/pages/member-pick` 协作者多选（`eventChannel` 双向回传，排除自己）
- **测试基建 `tests/`**（并入仓库，`npm test` 一键跑）
  - 6 个用例文件共 235 项断言；`run-all.js` 逐个 spawn + 汇总，零框架依赖
  - `tests/mocks/wx-server-sdk` 内存 Mock，业务代码零改动即可在 node 里跑云函数
  - `tests/README.md` 给出 **Mock 与真实 SDK 的行为对照表**
- **`_shared/db.js` 新增 `getDocById(coll, id)`** — 按 `_id` 取单条，取不到返回 `null`

### 变更 Changed

- ⚠️ **UI 库策略调整**：M2 的 4 个组件用**原生自定义组件**实现，暂未套用 TDesign。
  原因：当前环境无法执行开发者工具「构建 npm」，直接引用会报 `component is not found`（[P32](./09-pitfalls.md)）。
  组件均按「纯展示 + properties + triggerEvent」写，内部实现可在 M5 无痛替换为 TDesign，页面层不用改。
- 页面不再直接 `import cloud`，一律经 `services` 层；`services` 层负责回写 `store`（依赖方向铁律见 [02-architecture.md](./02-architecture.md)）

### 修复 Fixed

- **[P47](./09-pitfalls.md)** 🔴 ⭐ **本阶段唯一的线上级 bug**，三层一起修：
  - `doc(id).get()` 返回**对象**不是数组，误写 `res.data[0]` 恒为 `undefined`
  - `doc(id).get()` 取不到记录时**默认抛异常**（`throwOnNotFound` 默认 `true`），
    导致 `if (!plan) throw PLAN_NOT_FOUND` **永远执行不到**，
    用户看到的是「系统繁忙 5000」而不是「计划不存在 4001」
  - `auth-guard` 用 catch-all 把**任何**异常转成 `USER_NOT_FOUND`，数据库抖动会被显示成「账号不存在」
  - 修法：全局 `throwOnNotFound: false` + 统一收口 `getDocById`（只吞"记录不存在"，真实故障继续上抛）
  - 已补回归用例，并**故意把修复改回去验证过用例会红**（红 6 条）
- **[P49](./09-pitfalls.md)** `plan-detail.wxml` 用了 `empty-state` 但 json 未声明，那一块静默不渲染
- **测试自身的 bug**：M1 用例原本引用的是云函数**副本**而非 `cloudfunctions/` 源码，
  改完源码测试也不会红。已改为直接引用源码

### 新增预防性坑位 Pitfalls

- **[P48](./09-pitfalls.md)** 🔴 `remindAt` 改了但 `remindStatus` 没重置 → 到点不推送（M4 定时器依赖此状态机）
- **[P50](./09-pitfalls.md)** 🟡 前后端排序规则不一致 → 乐观更新后卡片"跳位"，已抽成同源 `sortWeight`

### 数据结构 Schema

- `plans` 集合按 [03-data-model.md](./03-data-model.md) 落地，字段无新增
- ⭐ `memberIds = [creatorId, ...assigneeIds]` 冗余数组，是"谁能看到"的**唯一判据**；
  任何改动 `assigneeIds` 的地方都必须重算它（`buildMemberIds`）
- `SCHEMA_VERSION = 1`（未变更）

### 关键决策记录 Decisions

| 决策 | 选择 | 理由 |
|---|---|---|
| planId 生成方 | **客户端**生成，服务端用 `doc(planId).set` | 天然幂等，M3 离线创建重放不会产生重复计划 |
| 完成并发 | 条件更新 + `updated===0` 复查 | 需求「至少一人完成」必然并发；第二人应看到"已完成"而非错误 |
| 可见性判据 | 冗余 `memberIds` 数组 + 数组索引 | 避免 `or(creatorId, assigneeIds)` 双条件，索引才走得动 |
| 列表数据源 | 页面订阅 `plan.store`，不各自缓存 | 完成一条计划要同时影响待完成/已完成两个 tab |
| UI 组件 | 先原生、后平替 TDesign | 环境不具备构建 npm 条件，不因工具链卡住业务进度 |
| 单条查询 | 一律走 `getDocById`，禁止裸写 `doc().get()` | 返回结构与失败行为都反直觉，收口成一个函数才不会再踩 |
| Mock 严格度 | 宁可比真实 SDK 更严格 | 宽松的 Mock 会给出虚假安全感，比没有测试更危险 |

### 影响面 Impact

- 需部署云函数：**`plan`**（新增）、**`auth`** 与 **`init-db`**（`_shared` 有改动，必须重传）
  部署前先跑 `npm run sync:shared` 同步 `common/`（[P40](./09-pitfalls.md)）
- 依赖索引：`plans.memberIds + status + deleted` 复合索引必须已建，否则列表会全表扫（[P43](./09-pitfalls.md)）
- 无需强制重同步（M3 才引入水位线）
- 下一步进入 M3（同步引擎：水位线增量拉取 + 本地库 + 离线队列），见 [08-roadmap.md](./08-roadmap.md)

---

## 待办提醒

以下事项需要在开发过程中及时回写本文档：

- [x] M1 完成后记一条 `[0.2.0]`
- [x] M2 完成后记一条 `[0.3.0]`
- [ ] M3 完成后记一条 `[0.4.0]`（同步引擎，可能涉及 SCHEMA 变更）
- [ ] M4 完成后记一条 `[0.5.0]`
- [ ] 首次提审前记一条 `[1.0.0-rc]`
- [ ] 上线后记一条 `[1.0.0]`
