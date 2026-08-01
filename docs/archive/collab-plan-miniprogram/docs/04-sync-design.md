---
module: archive
title: 04-sync-design.md
tags: [collab-plan-miniprogram]
source:
  project: collab-plan-miniprogram
  repo: https://github.com/Simiely/collab-plan-miniprogram
  file: docs/04-sync-design.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/collab-plan-miniprogram/blob/main/docs/04-sync-design.md)

# 04 · 时间戳增量同步机制设计

> 上级导航：[README 总导航](./README.md)
> 依赖：[03-data-model.md](./03-data-model.md) 的 `updatedAt` / `deleted` / `planId` 字段
> 对应代码：`miniprogram/sync/` + `cloudfunctions/sync/`

---

## 一、需求还原

> 「每次有新创建的任务会生成一个时间戳，本地和服务器都会有，数据也会保存到本地，每次打开小程序，会优先对比时间戳，如果服务器的最新，就同步差异的部分。」

翻译成技术方案：**服务器时间戳水位线（watermark）驱动的增量拉取 + 本地幂等合并**。

---

## 二、核心模型

### 2.1 水位线（Watermark）

本地保存一个 `lastSyncAt`，含义是：**"服务器上 `updatedAt` 小于这个值的数据，我本地都已经有了"**。

```
本地状态：
  lastSyncAt = 1730000000000   ← 上次同步成功时，服务器告诉我的服务器时间

同步请求：
  "把 updatedAt >= 1730000000000 的所有记录给我"

服务器返回：
  { changes: [...差异记录...], serverTime: 1730000060000, hasMore: false }

本地更新：
  合并 changes → lastSyncAt = 1730000060000
```

### 2.2 完整流程图

```
       打开小程序
            │
            ▼
  ┌────────────────────────┐
  │ 1. 读本地缓存           │  同步操作，< 10ms
  │    立即渲染列表          │  ⭐ 首屏不等网络
  └───────────┬────────────┘
              │
              ▼
  ┌────────────────────────┐
  │ 2. 读本地 lastSyncAt    │
  │    = 0 表示从未同步过    │
  └───────────┬────────────┘
              │
              ▼
  ┌────────────────────────┐
  │ 3. 重放离线操作队列      │  ⭐ 必须先上传本地待提交操作
  │    （创建/完成等）       │     再拉取，否则会被服务器数据覆盖
  └───────────┬────────────┘
              │
              ▼
  ┌────────────────────────┐
  │ 4. 调 sync.pull         │
  │    传 since = lastSyncAt│
  └───────────┬────────────┘
              │
              ▼
  ┌────────────────────────┐
  │ 5. 服务器查询            │
  │    memberIds 包含我      │
  │    AND updatedAt >= since│
  │    按 updatedAt 升序      │
  │    limit 100 分页        │
  └───────────┬────────────┘
              │
              ▼
  ┌────────────────────────┐
  │ 6. 本地幂等合并          │
  │    按 planId 覆盖        │
  │    deleted=true → 本地删 │
  └───────────┬────────────┘
              │
       hasMore? ──是──► 回到步骤 4（带新游标）
              │
              否
              ▼
  ┌────────────────────────┐
  │ 7. lastSyncAt = serverTime│
  │    写回本地              │
  └───────────┬────────────┘
              │
              ▼
  ┌────────────────────────┐
  │ 8. 通知 UI 刷新          │
  │    有变化才刷，避免闪烁   │
  └────────────────────────┘
```

---

## 三、五条设计铁律

### 铁律 1：水位线只能用服务器时间

```js
// ❌ 致命错误
lastSyncAt = Date.now()          // 手机时间！用户改系统时间就全乱

// ✅ 正确
lastSyncAt = response.serverTime // 云函数返回的服务器时间
```

**为什么**：手机时间可能比服务器快 5 分钟。用手机时间做水位线，会导致这 5 分钟内服务器上的新数据被永久跳过——**数据静默丢失，且极难排查**。

### 铁律 2：必须软删除

```js
// ❌ 硬删除
await db.collection('plans').doc(id).remove()
// 增量同步查不到已删除的记录 → 本地永远残留幽灵计划

// ✅ 软删除
await db.collection('plans').where({ planId }).update({
  data: { deleted: true, updatedAt: Date.now(), rev: _.inc(1) }
})
// 增量同步能拉到 deleted:true → 本地据此删除
```

### 铁律 3：用 `>=` 而非 `>`，配合幂等合并

```js
// 用 > ：同一毫秒内写入的多条记录，可能被跳过（丢数据，严重）
// 用 >=：会重复拉到边界那一条（无害，因为合并是幂等的）
where({ updatedAt: _.gte(since) })
```

再加一层保险——**安全回退窗口**：

```js
const SAFE_WINDOW = 2000; // 2 秒
const since = Math.max(0, lastSyncAt - SAFE_WINDOW);
```

**为什么需要**：云数据库写入到可查询之间存在微小延迟。回退 2 秒相当于「多问一点」，代价是几条重复记录，收益是杜绝丢数据。

### 铁律 4：合并必须幂等

```js
// merge.js 核心：按 planId 覆盖，不是 push
function mergeOne(localMap, remote) {
  if (remote.deleted) {
    localMap.delete(remote.planId);      // 软删除 → 本地移除
  } else {
    localMap.set(remote.planId, remote); // 存在则覆盖，不存在则新增
  }
}
```

同一条数据拉 10 次，结果完全一致。这让重复拉取、重试、断点续传都变得安全。

### 铁律 5：先上传，后下载

```
❌ 先 pull 再 push：
   本地有一条离线创建的计划 → pull 回来的数据覆盖本地 → 离线创建丢失

✅ 先 push 再 pull：
   离线操作先提交到服务器 → 服务器 updatedAt 更新 → pull 时自然带回权威版本
```

---

## 四、云函数 `sync.pull` 实现要点

```js
// cloudfunctions/sync/index.js  （伪代码，实现时补全错误处理）
exports.main = async (event) => {
  const userId = await authGuard(event.token);   // ⭐ 从 token 解出，不信前端

  const SAFE_WINDOW = 2000;
  const since = Math.max(0, (event.since || 0) - SAFE_WINDOW);
  const PAGE_SIZE = 100;                          // ⭐ 云数据库单次上限 100

  const res = await db.collection('plans')
    .where({
      memberIds: userId,                          // 数组包含匹配，走多键索引
      updatedAt: _.gte(since)
    })
    .orderBy('updatedAt', 'asc')                  // ⭐ 必须升序，保证分页不乱
    .skip(event.offset || 0)
    .limit(PAGE_SIZE)
    .get();

  const hasMore = res.data.length === PAGE_SIZE;

  return {
    code: 0,
    data: {
      changes:    res.data,
      hasMore,
      nextOffset: (event.offset || 0) + res.data.length,
      // ⭐ 只有最后一页才返回 serverTime，中间页返回 null
      // 防止分页途中失败，水位线却被推进 → 丢中间页数据
      serverTime: hasMore ? null : Date.now()
    }
  };
};
```

### 🕳️ 分页的隐藏陷阱

**问题**：分页过程中如果有新数据写入，`skip` 分页会错位（漏读或重读）。

**本项目的处理**：
1. 因为按 `updatedAt asc` 排序，新写入的数据 `updatedAt` 最大，会排在最后 → 只会「多读」不会「漏读」
2. 合并幂等，多读无害
3. `serverTime` 只在最后一页返回，任何一页失败都不推进水位线，下次重来

**更稳的替代方案**（数据量大时启用）：用游标分页替代 skip

```js
// 游标分页：用上一页最后一条的 updatedAt 作为下一页起点
where({ memberIds: userId, updatedAt: _.gte(cursor) })
  .orderBy('updatedAt', 'asc').limit(100)
```

> ⚠️ **实现注记**：实际 `cloudfunctions/sync/index.js` 已把上面的复合游标作为**默认分页方式**（替代 skip），
> 并进一步用 `(updatedAt, _id)` 双字段游标（`_id` 唯一，作同毫秒的稳定次级排序键），且保证「续页优先级高于 `since`」
> （一次同步里 `since` 固定、翻页只靠 cursor）。这样即使同一毫秒写入 > 100 条也不会错位或卡死。
> 详见 [09-pitfalls.md](./09-pitfalls.md) P51。

---

## 五、本地存储结构

```js
// core/storage.js 命名空间下
{
  "plan_app:v1:plans":       { "p_xxx": {...}, "p_yyy": {...} },  // Map 结构，按 planId
  "plan_app:v1:lastSyncAt":  1730000060000,
  "plan_app:v1:opQueue":     [ {...}, {...} ],                     // 离线操作队列
  "plan_app:v1:session":     { token, userId, expireAt },
  "plan_app:v1:schemaVer":   1
}
```

**为什么用 Map（对象）而不是数组存 plans**

| 操作 | 数组 | Map |
|---|---|---|
| 按 planId 更新 | O(n) 遍历查找 | O(1) 直接赋值 |
| 合并 500 条增量 | O(n×m) 慢 | O(m) 快 |
| 去重 | 需手动处理 | 天然去重 |

渲染时再 `Object.values()` + 排序转成数组。

**存储容量限制**：小程序单个 key 上限 1MB，总容量 10MB。
- 一条计划约 400 字节 → 1MB 约存 2500 条
- 超过 2000 条时需分片存储（`plans_0` / `plans_1`...）或只缓存近 3 个月数据
- 已记入 [09-pitfalls.md](./09-pitfalls.md)

---

## 六、离线操作队列

### 6.1 队列项结构

```js
{
  opId:      "op_uuid",        // 幂等键
  type:      "create" | "complete" | "update" | "remove",
  planId:    "p_xxx",
  payload:   { ... },
  createdAt: 1730000000000,    // 本地时间，仅用于排序和过期判断
  retryCount: 0
}
```

### 6.2 离线创建的关键：客户端生成 planId

```js
// utils/uuid.js
function genPlanId() {
  return 'p_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}
```

```
断网创建计划：
  1. 本地生成 planId = "p_lx8a2f9k"
  2. 立即写入本地 plans（乐观更新，UI 马上能看到）
     标记 _pending: true（UI 显示"待同步"角标）
  3. 入队 { type: 'create', planId: 'p_lx8a2f9k', payload }

联网后重放：
  4. 云函数用 planId 做 upsert：
     若已存在 → 直接返回成功（幂等，网络重试不会创建重复计划）
     若不存在 → 插入，服务器补 createdAt/updatedAt
  5. 出队，清除 _pending 标记
```

> ⭐ **这是「时间戳本地和服务器都有」需求的落地点**：客户端先生成本地时间戳 + planId 保证离线可用，服务器落库时以**服务器时间戳为权威**覆盖，同步回来后本地以服务器版本为准。

### 6.3 重放规则

| 规则 | 说明 |
|---|---|
| 顺序执行 | 严格按入队顺序，不并发（后面的操作可能依赖前面的） |
| 失败即停 | 某项失败则停止本轮重放，保留队列，下次再试 |
| 重试上限 | `retryCount > 5` 且是业务错误（非网络错误）→ 丢弃并记录，避免死循环 |
| 队列上限 | 超过 200 条时提示用户「离线数据过多，请联网同步」 |
| 去重 | 同一 planId 的多次 `complete` 合并为一次 |

---

## 七、冲突解决

### 7.1 「两人同时点完成」

这是本项目最主要的并发场景。用**原子条件更新**解决，不用「先查后写」。

```js
// cloudfunctions/plan/complete.js
const now = Date.now();
const res = await db.collection('plans').where({
  planId:  event.planId,
  status:  'pending',        // ⭐ 条件：必须还是未完成
  deleted: false,
  memberIds: userId          // ⭐ 权限：必须是成员
}).update({
  data: {
    status: 'done',
    completedBy: userId,
    completedAt: now,
    updatedAt: now,
    remindStatus: 'skipped', // 完成后作废提醒
    rev: _.inc(1)
  }
});

if (res.stats.updated === 0) {
  // 命中 0 条，三种可能，查一次确定原因，返回友好提示
  const cur = await db.collection('plans').where({ planId }).get();
  if (!cur.data.length)                    return fail('PLAN_NOT_FOUND');
  if (!cur.data[0].memberIds.includes(userId)) return fail('NO_PERMISSION');
  if (cur.data[0].status === 'done')
    return ok({ alreadyDone: true, by: cur.data[0].completedBy }); // ⭐ 不当作错误
}
return ok({ alreadyDone: false });
```

**前端表现**：第二个点击的人看到「该计划已由张三完成」的轻提示，列表自动刷新为已完成。**不弹错误**。

### 7.2 「编辑冲突」

创建者编辑 vs 协作者完成，可能同时发生。

**策略：字段级隔离 + 服务器权威（Last Write Wins）**

| 字段组 | 谁能改 | 冲突可能 |
|---|---|---|
| `title / desc / assigneeIds / remindAt` | 仅创建者 | 低（单人操作） |
| `status / completedBy / completedAt` | 任一成员 | 高 → 用原子条件更新解决 |

因为两组字段的可写人群不重叠，实际冲突概率极低。发生时以服务器最终状态为准（`updatedAt` 大的胜出），下次同步自动纠正本地。

### 7.3 本地脏数据 vs 服务器数据

```js
// merge.js
function resolve(local, remote) {
  // 本地有未提交的操作（_pending）→ 保留本地，等队列重放后再纠正
  if (local && local._pending) return local;
  // 否则一律以服务器为准
  return remote;
}
```

---

## 八、同步触发时机

| 时机 | 方式 | 节流 |
|---|---|---|
| App `onLaunch` | 异步触发，不阻塞 | — |
| App `onShow`（从后台切回） | `syncIfNeeded()` | 距上次同步 > 60s 才执行 |
| 列表页下拉刷新 | `syncAll({ force: true })` | 无节流 |
| 完成/创建操作后 | 局部更新，**不触发全量同步** | — |
| 收到提醒消息点进来 | `syncAll({ force: true })` | — |

> 🕳️ **坑**：不要在每个页面的 `onShow` 都调同步。用户在列表和详情间来回切会疯狂打接口。统一在 App 级别 + 下拉刷新触发。

---

## 九、首次同步（全量）

`lastSyncAt === 0` 时即为首次同步：

```
1. since = 0 → 拉取该用户全部可见计划
2. 分页循环直到 hasMore = false
3. 显示进度提示（"正在初始化数据 32/150"）
4. 全部完成后才写 lastSyncAt
```

**优化**：首次同步可只拉 `deleted: false` 的记录（已删除的历史数据没必要下发），后续增量再带上 deleted。

```js
const query = since === 0
  ? { memberIds: userId, deleted: false }            // 首次：跳过已删除
  : { memberIds: userId, updatedAt: _.gte(since) };  // 增量：含已删除
```

---

## 十、排查手册

同步出问题时按此顺序排查：

| 症状 | 可能原因 | 检查点 |
|---|---|---|
| 本地看不到别人创建的计划 | `memberIds` 没包含我 | 云端查该计划的 `memberIds` 字段；检查 `buildMemberIds` 是否被调用 |
| 数据少了一部分 | 水位线推进过头 | 检查是否用了手机时间；检查分页中途失败是否推进了水位线 |
| 删除的计划还在 | 用了硬删除 | 检查 `remove` 是否改成了 `update deleted:true` |
| 数据重复 | 合并用了 push 而非按 planId 覆盖 | 检查 `merge.js` |
| 同步很慢 | 索引缺失 | 检查 `memberIds + updatedAt` 复合索引是否建立 |
| 离线创建的计划变成两条 | planId 未做幂等 upsert | 检查云函数是否按 planId 判重 |
| 一直在全量同步 | `lastSyncAt` 没写回 | 检查 `serverTime` 是否为 null（分页未完成） |

**调试工具建议**：在「我的」页加一个隐藏入口（连点版本号 5 次），显示：

```
lastSyncAt:    2026-07-31 19:03:20
本地计划数:      142
待同步队列:      0
schema 版本:    1
[强制全量重同步]  ← 兜底大招
```

这个调试面板在联调期能省掉大量时间，强烈建议第一版就做。
