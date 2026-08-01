---
module: archive
title: 03-data-model.md
tags: [collab-plan-miniprogram]
source:
  project: collab-plan-miniprogram
  repo: https://github.com/Simiely/collab-plan-miniprogram
  file: docs/03-data-model.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/collab-plan-miniprogram/blob/main/docs/03-data-model.md)

# 03 · 数据模型设计

> 上级导航：[README 总导航](./README.md)
> 相关：[04-sync-design.md](./04-sync-design.md)（同步依赖本文的时间戳与软删除字段）

---

## ⚠️ 安全红线（先看这个）

云开发数据库的权限配置是**最容易出致命漏洞**的地方。默认权限允许前端直接读数据库。

**本项目所有集合权限必须设为：`仅创建者可读写` 中最严的一档 —— 「所有用户不可读，仅管理端可读写」**

在开发者工具 → 云开发 → 数据库 → 集合 → 权限设置中选择：

> **「仅管理端可读写」**（即只有云函数能操作）

| 集合 | 权限 | 不这么做的后果 |
|---|---|---|
| `users` | 仅管理端 | 🔴 前端 `db.collection('users').get()` 可拖走**全部密码哈希** |
| `user_bindings` | 仅管理端 | 🔴 泄露 openid 与账号对应关系 |
| `plans` | 仅管理端 | 🔴 任何人可读取**所有人**的计划，可任意篡改完成状态 |
| `subscribe_quota` | 仅管理端 | 🟡 额度可被前端刷 |
| `push_logs` | 仅管理端 | 🟡 信息泄露 |
| `op_logs` | 仅管理端 | 🟡 信息泄露 |

> 微信小程序的数据库权限「仅创建者可读写」判断依据是 `_openid`。本项目用**自建账号体系**，`_openid` 与业务身份不对应，所以这一档**完全不可用**，必须走云函数。

---

## 一、集合总览

| 集合 | 用途 | 预估量级 |
|---|---|---|
| `users` | 内置账号 | 数十~数百 |
| `user_bindings` | 账号 ↔ 微信 openid 绑定（推送用） | 账号数 × 设备数 |
| `plans` | 计划主表 | 千~万级 |
| `subscribe_quota` | 订阅消息额度池 | 账号数 |
| `push_logs` | 推送记录（排查与去重） | 万级，定期清理 |
| `op_logs` | 关键操作审计日志 | 万级，定期清理 |

---

## 二、`users` — 账号表

```js
{
  _id:          "u_a1b2c3",        // 主键，同时作为业务 userId
  username:     "zhangsan",         // 登录名，唯一
  passwordHash: "scrypt$...",       // scrypt 哈希，绝不存明文
  salt:         "随机16字节hex",     // 每个账号独立盐
  nickname:     "张三",              // 展示名
  avatarText:   "张",                // 头像文字（省去图片存储）
  avatarColor:  "#3B82F6",          // 头像底色
  status:       "active",           // active | disabled
  createdAt:    1730000000000,
  updatedAt:    1730000000000,
  lastLoginAt:  1730000000000
}
```

**索引**

| 字段 | 类型 | 唯一 | 说明 |
|---|---|:---:|---|
| `username` | 升序 | ✅ | 登录查询 + 防重 |
| `status` | 升序 | ❌ | 拉取可选协作者列表 |

**要点**
- `_id` 手动指定为可读的短 ID（如 `u_` 前缀），比自动生成的长串更易调试
- 前端拿到的账号列表必须**脱敏**：只返回 `_id / nickname / avatarText / avatarColor`
- `avatarText + avatarColor` 方案避免了头像图片上传与 CDN，大幅简化实现

---

## 三、`user_bindings` — 账号与微信绑定表

> 这张表是「自建账号 + 微信推送」架构的桥梁，**不能省**。

```js
{
  _id:         "自动",
  userId:      "u_a1b2c3",      // 关联 users._id
  openid:      "oXXXXXXXXXXXX", // 微信身份，推送目标
  deviceInfo:  "iPhone 14",     // 可选，便于用户识别设备
  boundAt:     1730000000000,
  lastActiveAt:1730000000000,
  active:      true             // 退出登录后置 false，不物理删除
}
```

**索引**

| 字段 | 类型 | 唯一 | 说明 |
|---|---|:---:|---|
| `userId + active` | 复合升序 | ❌ | 推送时查该账号所有活跃 openid |
| `openid` | 升序 | ❌ | 反查当前微信登录了哪个账号 |
| `userId + openid` | 复合 | ✅ | 防重复绑定 |

**关键设计说明**

```
一个 userId  →  多个 openid（同一账号在多台手机/多个微信登录）
一个 openid  →  同一时刻只应有一个 active 的 userId
```

| 场景 | 处理 |
|---|---|
| 账号 A 在微信甲登录 | 新增绑定 (A, 甲, active=true) |
| 账号 A 又在微信乙登录 | 新增绑定 (A, 乙, active=true)，甲仍有效 → 提醒推两个微信 |
| 微信甲改登账号 B | 把 (A, 甲) 置 `active=false`，新增 (B, 甲, active=true) |
| 账号 A 在微信甲退出 | 把 (A, 甲) 置 `active=false` |

> 🕳️ **坑**：如果不做「微信甲改登账号 B 时失效旧绑定」，甲会同时收到 A 和 B 的提醒，用户会困惑且可能构成信息泄露。

---

## 四、`plans` — 计划主表（核心）

```js
{
  _id:          "自动生成",
  planId:       "p_16f8c9a2b3",   // ⭐ 业务主键，客户端生成，用于离线创建与幂等

  // ---- 内容 ----
  title:        "完成季度复盘报告",   // 必填，≤ 50 字
  desc:         "包含数据分析部分",    // 选填，≤ 500 字

  // ---- 成员 ----
  creatorId:    "u_a1b2c3",        // 创建者
  assigneeIds:  ["u_d4e5", "u_f6g7"], // 指定协作者
  memberIds:    ["u_a1b2c3","u_d4e5","u_f6g7"], // ⭐ 冗余 = creator + assignees，专供索引查询

  // ---- 状态 ----
  status:       "pending",         // pending | done
  completedBy:  null,              // userId
  completedAt:  null,              // 时间戳

  // ---- 提醒 ----
  remindAt:     1730100000000,     // 提醒时间戳，null 表示不提醒
  remindStatus: "pending",         // none | pending | sending | sent | failed | skipped
  remindLockAt: null,              // 幂等锁时间戳，防定时器重复推送

  // ---- 同步控制（⭐ 不可缺，见 04 文档）----
  createdAt:    1730000000000,     // 服务器时间
  updatedAt:    1730000000000,     // ⭐ 任何字段变更都必须刷新，同步水位线依据
  deleted:      false,             // ⭐ 软删除，禁止物理删除
  rev:          1                  // 版本号，每次更新 +1，用于冲突诊断
}
```

### 4.1 索引（性能关键）

| 索引 | 字段 | 用途 |
|---|---|---|
| `idx_planId` | `planId` (唯一) | 幂等 upsert、单条查询 |
| `idx_member_updated` | `memberIds` + `updatedAt` | ⭐ **增量同步主查询**，必须有 |
| `idx_member_status` | `memberIds` + `status` + `deleted` | 待办/已完成列表查询 |
| `idx_remind_scan` | `remindStatus` + `remindAt` | ⏰ 定时扫描到期提醒 |

> `memberIds` 是数组字段，云开发支持对数组建索引（多键索引），`where({ memberIds: userId })` 会自动匹配数组包含。

### 4.2 为什么要冗余 `memberIds`

不冗余的话，查「我可见的计划」需要：

```js
// ❌ 低效：or 查询无法有效走索引
_.or([ { creatorId: userId }, { assigneeIds: userId } ])
```

冗余后：

```js
// ✅ 单一索引命中
{ memberIds: userId, deleted: false }
```

**维护规则**：任何修改 `creatorId` 或 `assigneeIds` 的地方，**必须同步重算 `memberIds`**。建议在云函数 `common/` 里封装一个 `buildMemberIds(creatorId, assigneeIds)` 强制统一。

### 4.3 `remindStatus` 状态机

```
   无提醒时间
        │
        ▼
     none ────设置提醒时间────►  pending
                                   │
                    定时器扫描命中并抢到锁
                                   │
                                   ▼
                               sending ──推送成功──► sent
                                   │
                                   └──推送失败──► failed（可重试）

  计划被完成/删除 → 提醒作废 → skipped
  修改提醒时间   → 重置为 pending，清空 remindLockAt
```

---

## 五、`subscribe_quota` — 订阅额度池

```js
{
  _id:          "自动",
  userId:       "u_a1b2c3",
  openid:       "oXXXX",            // 额度是绑定到具体微信的
  templateId:   "TEMPLATE_ID_XXX",
  remaining:    3,                  // 剩余可推送次数
  totalGranted: 10,                 // 累计授权次数（统计用）
  totalUsed:    7,                  // 累计已用
  updatedAt:    1730000000000
}
```

**索引**：`userId + openid + templateId`（唯一）

> 微信的订阅次数是按 (openid, templateId) 维度累积的，所以额度记录必须带 openid，不能只按 userId 记。

---

## 六、`push_logs` — 推送日志

```js
{
  _id:        "自动",
  planId:     "p_16f8c9a2b3",
  userId:     "u_a1b2c3",
  openid:     "oXXXX",
  templateId: "TEMPLATE_ID_XXX",
  result:     "success",       // success | fail
  errCode:    0,
  errMsg:     "",
  pushedAt:   1730100000000
}
```

**索引**：`planId + openid`（唯一）→ ⭐ 天然的推送去重保险，即便定时器重复执行也不会重复推

**清理**：保留 30 天，用定时云函数清理旧记录（避免集合无限增长）

---

## 七、`op_logs` — 操作审计

```js
{
  _id:      "自动",
  userId:   "u_a1b2c3",
  action:   "plan.complete",
  targetId: "p_16f8c9a2b3",
  detail:   { from: "pending", to: "done" },
  ip:       "...",              // 云函数可从 context 获取
  at:       1730000000000
}
```

用途：排查「这条计划是谁完成的/谁改的」，以及同步异常时的时间线还原。

---

## 八、字段命名与类型约定

| 约定 | 说明 |
|---|---|
| 时间字段 | 一律用**毫秒数字时间戳**（`Number`），不用 `Date` 对象也不用字符串 |
| 时间来源 | 一律由**云函数**生成，客户端时间只用于 UI 展示 |
| 布尔字段 | 用 `is`/`has`/明确语义命名，且**必须有默认值**（不能是 `undefined`） |
| ID 字段 | 统一 `xxxId` 后缀；`_id` 仅指数据库主键 |
| 数组字段 | 复数命名（`memberIds`、`assigneeIds`） |
| 空值 | 用 `null` 表示"无"，不用 `undefined`（云数据库会忽略 undefined 字段导致更新失败） |

> 🕳️ **坑**：`db.collection().update({ data: { remindAt: undefined } })` **不会**把字段设为空，而是**忽略该字段**。要清空必须用 `null` 或 `_.remove()`。

---

## 九、初始化脚本要点

首次部署需要做的数据初始化（建议写成一次性云函数 `init`，跑完即删）：

```
1. 创建 6 个集合
2. 建立所有索引（云控制台手动建 或 用 SDK 建）
3. 插入初始账号（用 scrypt 生成密码哈希，绝不明文）
4. 校验所有集合权限均为「仅管理端可读写」  ← 必查
```

**初始账号建议**：先建 3 个测试账号（`test1/test2/test3`），便于验证多人协作与提醒逻辑。

---

## 十、数据模型变更流程

改字段时**必须**走这个流程，否则会引发同步事故：

```
1. 改本文档的字段定义
2. 判断是否影响同步：
   ├─ 新增可选字段 → 安全，老数据读出来是 undefined，前端做默认值兜底
   ├─ 重命名/删除字段 → 危险！本地缓存是旧结构
   │    → 必须提升 core/storage.js 的 SCHEMA_VERSION
   │    → 触发本地清库 + 全量重同步
   └─ 改字段语义（同名不同义）→ 最危险，等同于重命名，同上处理
3. 更新 04-sync-design.md 的合并逻辑（如有必要）
4. 记录到 10-changelog.md
```
