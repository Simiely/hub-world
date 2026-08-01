---
module: archive
title: 02-architecture.md
tags: [collab-plan-miniprogram]
source:
  project: collab-plan-miniprogram
  repo: https://github.com/Simiely/collab-plan-miniprogram
  file: docs/02-architecture.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/collab-plan-miniprogram/blob/main/docs/02-architecture.md)

# 02 · 技术架构与模块设计

> 上级导航：[README 总导航](./README.md)
> 本文定义**代码怎么组织**。功能定义见 [01-product-spec.md](./01-product-spec.md)。

---

## 一、整体架构图

```
┌───────────────────────────────────────────────────────────────┐
│                      小程序端 (miniprogram/)                    │
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  展示层  pages/ + components/                            │  │
│  │  职责：渲染 UI、响应用户交互、调用 service               │  │
│  │  禁止：写业务逻辑、直接调云函数、直接操作 storage        │  │
│  └───────────────────────┬─────────────────────────────────┘  │
│                          │ 只能调用 ↓                          │
│  ┌───────────────────────▼─────────────────────────────────┐  │
│  │  业务服务层  services/                                   │  │
│  │  职责：业务编排、参数校验、调用云函数、更新本地库与 store │  │
│  │  这是页面唯一合法的业务入口                              │  │
│  └──────────┬───────────────────────────┬──────────────────┘  │
│             │                           │                     │
│  ┌──────────▼──────────┐   ┌────────────▼──────────────────┐  │
│  │  同步引擎  sync/     │   │  基础设施  core/               │  │
│  │  水位线 / 合并 /     │   │  request / storage / session  │  │
│  │  离线队列 / 本地库    │   │  logger / error / event-bus   │  │
│  └──────────┬──────────┘   └────────────┬──────────────────┘  │
│             └──────────┬────────────────┘                     │
│                        ▼                                      │
│              utils/  纯函数工具（无副作用、无依赖）             │
└────────────────────────┬──────────────────────────────────────┘
                         │ wx.cloud.callFunction
┌────────────────────────▼──────────────────────────────────────┐
│                   云开发 (cloudfunctions/)                      │
│                                                               │
│  auth      plan      sync      subscribe     remind-scan      │
│  登录鉴权   计划CRUD   增量拉取   额度记账      ⏰定时触发器      │
│    └──────────┴─────────┴───────────┴──────────────┘          │
│                         │                                     │
│                  common/ 公共层                                │
│         auth-guard / db / response / constants                │
│                         │                                     │
│  ┌──────────────────────▼──────────────────────────────────┐  │
│  │  云数据库 Collections                                    │  │
│  │  users │ user_bindings │ plans │ subscribe_quota │      │  │
│  │  push_logs │ op_logs                                     │  │
│  │  ⚠️ 全部设为「仅云函数可读写」                             │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

---

## 二、完整目录结构

```
/workspace
├── docs/                                # 📚 文档体系（见 README.md）
│
├── project.config.json                  # 项目配置（含 cloudfunctionRoot）
├── package.json                         # 根依赖（TDesign 等，用于构建 npm）
│
├── miniprogram/                         # 📱 小程序前端
│   ├── app.js                           # 全局：初始化云开发、恢复会话、触发同步
│   ├── app.json                         # 全局配置：页面路由、tabBar、分包、preloadRule
│   ├── app.wxss                         # 全局样式 + 设计变量（CSS 变量）
│   ├── sitemap.json                     # 搜索索引配置
│   │
│   ├── pages/                           # 主包页面（高频，必须精简）
│   │   ├── login/                       # 账号密码登录
│   │   ├── todo/                        # ① 待完成列表（TabBar 首页）
│   │   ├── done/                        # ② 已完成列表（TabBar）
│   │   ├── profile/                     # ③ 我的（TabBar：额度/改密/退出）
│   │   └── plan-detail/                 # 计划详情
│   │
│   ├── packageA/                        # 📦 分包：编辑类低频页面
│   │   └── pages/
│   │       ├── plan-edit/               # 创建 / 编辑计划
│   │       └── member-pick/             # 选择协作者
│   │
│   ├── components/                      # 可复用 UI 组件（纯展示，通过事件向上传递）
│   │   ├── plan-card/                   # 计划卡片（列表项）
│   │   ├── member-avatars/              # 成员头像组
│   │   ├── remind-badge/                # 提醒时间标签
│   │   ├── empty-state/                 # 空状态占位
│   │   └── sync-tip/                    # 顶部同步状态轻提示
│   │
│   ├── services/                        # 🎯 业务服务层（页面唯一业务入口）
│   │   ├── auth.service.js              # 登录、登出、会话校验、改密
│   │   ├── plan.service.js              # 创建/完成/编辑/删除/查询计划
│   │   ├── member.service.js            # 账号列表、成员信息缓存
│   │   └── remind.service.js            # 订阅授权、额度查询与上报
│   │
│   ├── sync/                            # ⭐ 同步引擎（独立可测模块）
│   │   ├── index.js                     # 对外入口：syncAll() / syncIfNeeded()
│   │   ├── watermark.js                 # 水位线读写与安全回退窗口
│   │   ├── merge.js                     # 增量合并、软删除处理、冲突解决
│   │   ├── queue.js                     # 离线操作队列（入队/重放/去重）
│   │   └── local-db.js                  # 本地计划表 CRUD（基于 core/storage）
│   │
│   ├── core/                            # 🔧 基础设施（不含业务语义）
│   │   ├── cloud.js                     # 云函数调用统一封装（超时/重试/错误码）
│   │   ├── storage.js                   # 本地存储封装（命名空间 + schema 版本 + 迁移）
│   │   ├── session.js                   # Token 存取、过期判断、登录态守卫
│   │   ├── event-bus.js                 # 跨页面事件（如同步完成通知列表刷新）
│   │   ├── logger.js                    # 分级日志 + 上报开关
│   │   └── error.js                     # 错误码常量与统一 toast 映射
│   │
│   ├── store/                           # 全局状态
│   │   └── plan.store.js                # 计划列表内存态 + 订阅通知
│   │
│   └── utils/                           # 纯函数（无副作用，可直接单测）
│       ├── date.js                      # 时间格式化、相对时间、时区安全解析
│       ├── uuid.js                      # 客户端 ID 生成（离线创建用）
│       └── format.js                    # 文本截断（订阅消息字段长度限制）
│
└── cloudfunctions/                      # ☁️ 云函数
    ├── common/                          # 公共层（以本地 npm 包形式被各函数引用）
    │   ├── auth-guard.js                # Token 校验 → 返回 userId
    │   ├── db.js                        # 数据库实例与集合常量
    │   ├── response.js                  # 统一返回结构 { code, data, msg }
    │   ├── constants.js                 # 错误码、集合名、模板 ID
    │   └── password.js                  # scrypt 加盐哈希与校验
    │
    ├── auth/                            # 登录 / 登出 / 校验 / 改密 / 绑定 openid
    ├── plan/                            # 计划 CRUD（含原子完成）
    ├── sync/                            # 增量拉取（水位线查询 + 分页）
    ├── subscribe/                       # 订阅额度记账（+1 / 查询）
    └── remind-scan/                     # ⏰ 定时触发器：扫描到期计划并推送
```

---

## 三、模块职责与依赖规则

### 3.1 依赖方向（铁律）

```
pages / components
       ↓ 只能调
   services
       ↓ 可调
 sync  ←→  core
       ↓ 可调
     utils
```

| 规则 | 违反后果 |
|---|---|
| 页面不得 `wx.cloud.callFunction` | 错误处理、重试、登录态刷新逻辑散落各处，无法统一维护 |
| 页面不得 `wx.setStorageSync` 存业务数据 | 绕过 schema 版本管理，升级时数据结构错乱 |
| `core/` `utils/` 不得引用 `services/` `pages/` | 形成循环依赖，模块无法复用和单测 |
| `sync/` 不得直接 `setData` | 同步引擎与 UI 解耦，通过 `event-bus` 或 `store` 通知 |
| 云函数不得信任前端传来的 `userId` | **越权漏洞**，userId 必须从 Token 解出 |

### 3.2 各层职责边界

| 层 | 做什么 | 不做什么 |
|---|---|---|
| **pages** | setData、事件绑定、页面生命周期、导航 | 业务规则判断、网络请求、数据持久化 |
| **components** | 接收 properties 渲染、triggerEvent 上抛 | 调用 service、读写 storage |
| **services** | 参数校验、调云函数、写本地库、更新 store、错误转提示 | 直接 setData、UI 相关逻辑 |
| **sync** | 水位线、拉取、合并、队列重放 | 业务权限判断、UI 提示 |
| **core** | 网络/存储/会话/日志的技术封装 | 任何业务语义（不出现 plan、member 等词） |
| **utils** | 纯计算、格式化 | 任何 IO、任何 wx API 调用 |

---

## 四、核心模块设计要点

### 4.1 `core/cloud.js` — 云函数调用封装

统一处理这些横切关注点，页面和 service 都不用重复写：

```js
callCloud(name, action, data) 内部做：
  ① 自动附加 Token（从 session 取）
  ② 超时控制（默认 10s，可覆盖）
  ③ 网络错误重试（幂等接口重试 2 次，非幂等不重试）
  ④ 统一解包 { code, data, msg }
  ⑤ code === 401 → 清会话 + 跳登录页
  ⑥ 失败时按错误码映射为用户可读提示（走 core/error.js）
  ⑦ 记录耗时日志
```

**设计要点**：所有云函数采用 `name + action` 的路由模式（一个云函数内部按 action 分发），减少云函数数量，降低冷启动概率。

### 4.2 `core/storage.js` — 带版本的本地存储

```js
命名空间：  plan_app:{schemaVersion}:{key}
schema 版本：常量 SCHEMA_VERSION，结构变更时 +1
迁移机制：  启动时对比本地版本，不一致则执行 migrations 或清库重同步
```

> **为什么需要版本**：后续给 plan 加字段时，老用户本地存的是旧结构。不做版本管理，轻则渲染异常，重则同步合并崩溃。这是一个典型的「上线后才发现」的坑，已记入 [09-pitfalls.md](./09-pitfalls.md)。

### 4.3 `sync/` — 同步引擎

对外只暴露三个方法，内部实现完全封装：

```js
syncAll({ force })     // 全量/增量同步，返回 { added, updated, removed }
syncIfNeeded()         // 距上次同步超过阈值才同步（避免频繁热启动打接口）
enqueueOp(op)          // 离线操作入队
```

算法细节见 [04-sync-design.md](./04-sync-design.md)。

### 4.4 `store/plan.store.js` — 轻量全局状态

不引入 MobX 等第三方库（省包体积），自己实现极简发布订阅：

```js
plan.store.js 提供：
  getTodoList() / getDoneList()   // 从内存态派生
  setPlans(list)                  // 全量设置
  upsertPlan(plan)                // 单条更新
  subscribe(fn) / unsubscribe(fn) // 变更通知
```

页面在 `onShow` 订阅、`onHide` 取消订阅，避免内存泄漏。

---

## 五、云函数设计

### 5.1 统一约定

| 项 | 约定 |
|---|---|
| 入参结构 | `{ action, token, payload }` |
| 出参结构 | `{ code: 0, data: {...}, msg: '' }`，`code !== 0` 即失败 |
| 鉴权 | 除 `auth.login` 外，所有 action 第一行调 `authGuard(token)` |
| userId 来源 | **只能**从 Token 解出，永不采信 payload 里的 userId |
| 时间戳 | 一律用云函数服务端 `Date.now()`，禁止采信客户端时间 |
| 日志 | 关键写操作记录到 `op_logs`，便于排查 |

### 5.2 云函数一览

| 云函数 | action | 说明 | 幂等 |
|---|---|---|:---:|
| `auth` | `login` | 用户名密码校验 → 签发 Token + 绑定 openid | ✅ |
| | `verify` | 校验 Token 有效性 | ✅ |
| | `logout` | 失效 Token + 解绑 openid | ✅ |
| | `changePassword` | 校验旧密码后更新 | ❌ |
| `plan` | `create` | 创建计划（按 clientId 幂等 upsert） | ✅ |
| | `complete` | 原子条件更新完成 | ✅ |
| | `uncomplete` | 撤销完成（仅创建者） | ✅ |
| | `update` | 编辑（仅创建者） | ❌ |
| | `remove` | 软删除（仅创建者） | ✅ |
| `sync` | `pull` | 按水位线拉取增量 + 分页 | ✅ |
| `member` | `list` | 返回可选协作者账号列表（脱敏） | ✅ |
| `subscribe` | `grant` | 用户授权成功后额度 +1 | ❌ |
| | `query` | 查询剩余额度 | ✅ |
| `remind-scan` | *(定时触发)* | 扫描到期计划 → 推送 → 额度 -1 | ✅（带锁） |

> `member.list` 可合并进 `plan` 云函数以减少函数数量，视实际冷启动表现决定。

### 5.3 云函数配置要点

| 云函数 | 超时 | 内存 | 特殊配置 |
|---|---|---|---|
| `auth` | 5s | 256MB | scrypt 计算较慢，内存不要太低 |
| `plan` | 5s | 256MB | — |
| `sync` | 20s | 512MB | 首次全量同步数据量大 |
| `remind-scan` | 60s | 512MB | 批量推送耗时；需配置定时触发器 |

**定时触发器配置**（`remind-scan/config.json`）：

```json
{
  "triggers": [{
    "name": "remindScanTimer",
    "type": "timer",
    "config": "0 * * * * * *"
  }]
}
```
> 云开发 cron 是 **7 位**（秒 分 时 日 月 周 年），比标准 cron 多一位。写成 5 位会配置失败，这是高频坑。

---

## 六、包体积规划

| 部分 | 内容 | 预算 |
|---|---|---|
| 主包 | 5 个页面 + 5 个组件 + core/sync/services + TDesign 按需组件 | **< 1.2MB** |
| packageA | 创建编辑页 + 成员选择页 | < 300KB |
| **合计** | | < 1.5MB |

**控制手段**

1. **TDesign 按需引入**：只在用到的页面 `usingComponents` 里声明，不做全局注册
2. **图标走字体或云存储**：不打包大量 PNG；小图标用 base64 内联（< 2KB 的）
3. **分包预下载**：在 `app.json` 配置 `preloadRule`，进入 todo 页时后台预下载 packageA，用户点「创建」时无感
4. **不引入 moment/lodash**：日期和工具函数自己写在 `utils/`，只实现用到的
5. **定期体检**：开发者工具「代码依赖分析」，每个迭代看一次

```json
// app.json 预下载配置
"preloadRule": {
  "pages/todo/todo": {
    "network": "wifi",
    "packages": ["packageA"]
  }
}
```

---

## 七、性能设计要点

### 7.1 setData 纪律

| 规则 | 说明 |
|---|---|
| 合并调用 | 一次交互内的多个状态变更合并成一次 `setData` |
| 路径更新 | 列表单项变更用 `this.setData({ ['list[3].status']: 'done' })`，不整个列表重设 |
| 剔除无用字段 | 只把视图用得到的字段放进 data；原始完整数据挂 `this.xxx` |
| 纯数据字段 | 不参与渲染的用 `options.pureDataPattern: /^_/` 声明 |
| 长列表 | 超过 100 条启用分页加载或 `recycle-view` |

### 7.2 启动优化

```
app.js onLaunch 只做三件事（同步、快速）：
  ① wx.cloud.init()
  ② 从 storage 恢复 Token（同步读，< 5ms）
  ③ 标记启动时间

绝不在 onLaunch 里：
  ✗ await 网络请求（阻塞首屏）
  ✗ 全量读取本地计划数据（大 JSON 反序列化慢）
  ✗ 弹任何授权框
```

同步动作放在首页 `onShow` 里异步触发，不阻塞渲染。

---

## 八、环境与配置管理

```
miniprogram/config/env.js

export const ENV = {
  dev:  { cloudEnvId: 'dev-xxxxx',  logLevel: 'debug', mockDelay: 0 },
  prod: { cloudEnvId: 'prod-xxxxx', logLevel: 'error', mockDelay: 0 },
}
```

通过 `__wxConfig.envVersion` 自动判断当前环境（`develop` / `trial` / `release`），无需手动改代码提审。

> ⚠️ 切勿把生产环境 ID 写死在多处；只在 `env.js` 一处维护。

---

## 九、模块化落地检查清单

新增代码前对照检查：

- [ ] 这段逻辑属于哪一层？放对目录了吗？
- [ ] 页面里有没有出现 `wx.cloud`、`wx.setStorage`、`wx.request`？（应该没有）
- [ ] service 里有没有 `setData`？（应该没有）
- [ ] core/utils 里有没有出现业务词汇（plan/member/remind）？（应该没有）
- [ ] 新增字段是否影响同步？改了 [03-data-model.md](./03-data-model.md) 和 [04-sync-design.md](./04-sync-design.md) 吗？
- [ ] 云函数里有没有直接用前端传的 userId？（严禁）
- [ ] 是否新增了主包体积？能否放分包？
