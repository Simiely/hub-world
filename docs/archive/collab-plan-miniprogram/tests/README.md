---
module: archive
title: README.md
tags: [collab-plan-miniprogram]
source:
  project: collab-plan-miniprogram
  repo: https://github.com/Simiely/collab-plan-miniprogram
  file: tests/README.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/collab-plan-miniprogram/blob/main/tests/README.md)

# tests · 本地单测

> 上级导航：[docs/README.md](../docs/README.md)

```bash
npm test              # 跑全部（会自动先执行 sync:shared）
npm test -- plan      # 只跑文件名含 plan 的用例
npm test -- cloud     # 只跑云函数用例
```

---

## 这套测试测的是什么

**测**：云函数业务逻辑（权限、并发、状态机、脱敏）、前端 service/store 的数据流、纯函数工具。
**不测**：真实云环境、真实网络、UI 渲染、真机行为。这些属于 [11-testing-release.md](../docs/11-testing-release.md) 的真机测试矩阵。

目标很明确：**逻辑错误在 1 秒内暴露，不要等到真机联调才发现。**

---

## 文件说明

| 文件 | 覆盖对象 | 断言数 |
|---|---|---|
| `cloud-auth.test.js` | `auth` + `init-db` 云函数：登录、锁定、绑定、守卫、改密 | 58 |
| `cloud-plan.test.js` | `plan` 云函数：创建幂等、可见性、并发完成、状态机、软删除 | 50 |
| `frontend-auth.test.js` | `auth.service` / `session` / `storage`：登录态、换号清缓存 | 34 |
| `frontend-plan.test.js` | `plan.service` / `plan.store` / `member.service`：回写与订阅 | 24 |
| `shared.test.js` | `_shared`：password / token / time / `getDocById` | 32 |
| `utils.test.js` | `utils`：date / format / uuid | 37 |
| | **合计** | **235** |

用例文件**各自可独立执行**（`node tests/cloud-plan.test.js`，需带 `NODE_PATH=tests/mocks`）。
`run-all.js` 只负责逐个 spawn + 汇总，所以没有任何测试框架依赖，栈信息也不会被框架包一层。

---

## Mock 的定位与铁律

`tests/mocks/wx-server-sdk/` 是 `wx-server-sdk` 的内存实现，云函数 `require('wx-server-sdk')`
通过 `NODE_PATH` 解析到它，**业务代码一行都不用改**。

> 🔴 **铁律：Mock 必须严格复刻真实 SDK，宁可更严格，绝不能更宽松。**

这条是用事故换来的（[P47](../docs/09-pitfalls.md)）：
最早的 Mock 让 `doc().get()` 返回**数组**，而真实 SDK 返回**对象**且取不到时**抛异常**。
结果单测全绿，线上必崩——**比没有测试更危险，因为它提供了虚假的安全感**。

已刻意对齐的真实行为：

| 行为 | 真实 SDK | Mock |
|---|---|---|
| `cloud.database()` 早于 `init` | 抛 `Cloud API isn't enough initialized` | 同（复刻 P41） |
| `where().get()` 取不到 | `{ data: [] }` | 同 |
| `doc().get()` 取到 | `{ data: {对象} }` | 同 |
| `doc().get()` 取不到 | **抛异常** `-502004` | 同（复刻 P47） |
| `throwOnNotFound: false` | 改为返回 `{ data: null }` | 同 |
| `update` 的 `undefined` 字段 | 被忽略，不置空 | 同（复刻 P03） |
| 数组字段等值查询 | 命中「包含」 | 同（复刻 P27） |
| `createCollection` 重复建 | 抛 `-501001` | 同 |

新增 Mock 能力时，**先去查官方文档确认真实行为**，再写实现。
拿不准就让 Mock 更严格（抛错），让问题在本地炸，而不是在用户手机上炸。

### 测试辅助方法（真实 SDK 没有）

```js
cloud.__setOpenid('openid_A')      // 切换当前微信身份
cloud.__doc('users', 'u_test1')    // 取活引用，可直接改状态造场景
cloud.__all('user_bindings')       // 取整表快照
cloud.__reset()                    // 原地清空（⚠️ 不能替换 STORE 对象）
```

`__reset` 必须**原地清空**：`common/db.js` 在模块加载时就 `const db = cloud.database()`
把实例捕获走了，换对象会让业务代码继续读旧引用，测试之间互相污染。

---

## 加用例的约定

1. **一个断言只验一件事**，描述写清「期望什么」，失败时能直接看懂
2. 红线级用例（越权、脱敏、并发、软删除）在描述里加 `🔴` 前缀
3. 修完一个坑，**补一条以坑号命名的回归用例**（如 `P47 回归：...`）
4. 写完回归用例要**故意把修复改回去跑一遍**，确认用例真的会红——
   不会红的回归用例等于没写
