---
module: archive
title: 05-reminder-design.md
tags: [collab-plan-miniprogram]
source:
  project: collab-plan-miniprogram
  repo: https://github.com/Simiely/collab-plan-miniprogram
  file: docs/05-reminder-design.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/collab-plan-miniprogram/blob/main/docs/05-reminder-design.md)

# 05 · 订阅消息与定时提醒设计

> 上级导航：[README 总导航](./README.md)
> 对应代码：`cloudfunctions/remind-scan/` + `cloudfunctions/subscribe/` + `miniprogram/services/remind.service.js`

---

## 一、先理解微信订阅消息的三条硬规则

这是整个提醒功能设计的**约束前提**，不理解就会做出跑不通的方案。

| 规则 | 含义 | 对设计的影响 |
|---|---|---|
| **一次授权一次推送** | 用户点一次「允许」，你只能推**一条**消息 | 必须自建额度池记账 |
| **必须用户手势触发** | `requestSubscribeMessage` 只能在 tap 事件回调里调 | 不能自动弹窗，要设计引导时机 |
| **推送目标是 openid** | 不是你的自建 userId | 必须有 `user_bindings` 绑定表 |

**长期订阅**（可无限推送）只对政务、医疗、交通等特定类目开放，普通小程序**申请不到**，不要抱幻想。

---

## 二、整体流程

```
┌──────────────────────────────────────────────────────────┐
│                     授权阶段（前端）                        │
│                                                          │
│  用户点击「开启提醒」按钮（必须是 tap）                      │
│            ↓                                             │
│  wx.requestSubscribeMessage({ tmplIds: [模板ID] })        │
│            ↓                                             │
│  返回 { 模板ID: 'accept' | 'reject' | 'ban' }             │
│            ↓                                             │
│  accept → 调 subscribe.grant 云函数 → 额度 +1              │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│                   推送阶段（定时云函数）                     │
│                                                          │
│  每分钟触发 remind-scan                                    │
│            ↓                                             │
│  查 remindStatus='pending' AND remindAt <= now            │
│            ↓                                             │
│  抢锁：条件更新 remindStatus → 'sending'（幂等保护）        │
│            ↓                                             │
│  对每个 memberId：                                         │
│    ├─ 查 user_bindings 拿所有 active 的 openid            │
│    ├─ 查 subscribe_quota 确认额度 > 0                     │
│    ├─ 查 push_logs 确认未推过（二次去重）                   │
│    └─ cloud.openapi.subscribeMessage.send()              │
│            ↓                                             │
│  成功 → 额度 -1，写 push_logs，remindStatus='sent'         │
│  失败 → 写 push_logs，remindStatus='failed'                │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│                   兜底阶段（应内提醒）                       │
│  打开小程序时，对 remindAt <= now 且未完成的计划            │
│  在列表页置顶 + 显示红色「已到期」标签                       │
└──────────────────────────────────────────────────────────┘
```

---

## 三、订阅消息模板设计

在微信公众平台 →「订阅消息」→ 从模板库选择或申请。

**建议模板：任务提醒 / 待办提醒**

| 字段 | 类型 | 示例值 | ⚠️ 长度限制 |
|---|---|---|---|
| `thing1` | 事项名称 | 完成季度复盘报告 | **20 个字符以内** |
| `time2` | 提醒时间 | 2026年7月31日 19:03 | 固定格式 |
| `thing3` | 创建人 | 张三 | 20 字符以内 |
| `thing4` | 备注 | 请及时处理 | 20 字符以内 |

### 🕳️ 字段格式坑（高频报错源）

| 类型 | 规则 | 违反后的错误码 |
|---|---|---|
| `thing` | **20 个字符以内**，中英文数字均算 1 个 | `47003 参数不符合规则` |
| `time` | 必须 `2026年7月31日 19:03` 或 `2026-07-31 19:03` 格式 | `47003` |
| `number` | 只能是数字，最多 32 位 | `47003` |
| `phrase` | **5 个汉字以内** | `47003` |
| 所有字段 | **不能为空字符串** | `47003` |
| 所有字段 | 不能含表情、特殊符号 | `47003` |

**强制封装截断函数**（`utils/format.js`，云函数侧也要有一份）：

```js
// 所有 thing 类型字段必须过这个函数
function toThing(str, max = 20) {
  const s = String(str || '').replace(/[\r\n\t]/g, ' ').trim();
  if (!s) return '无';                                    // ⭐ 不能为空
  return s.length > max ? s.slice(0, max - 1) + '…' : s;  // ⭐ 截断
}

function toTime(ts) {
  const d = new Date(ts + 8 * 3600 * 1000);               // ⭐ 云函数是 UTC，要 +8
  const p = n => String(n).padStart(2, '0');
  return `${d.getUTCFullYear()}年${d.getUTCMonth()+1}月${d.getUTCDate()}日 ${p(d.getUTCHours())}:${p(d.getUTCMinutes())}`;
}
```

> 🕳️ **时区坑**：云函数运行环境是 **UTC 时区**，`new Date().getHours()` 拿到的是 UTC 小时，比北京时间少 8 小时。所有面向用户的时间格式化必须显式 +8 小时。这个坑会导致提醒消息里显示的时间全错。

---

## 四、额度池管理

### 4.1 为什么必须自己记账

微信提供了 `wx.getSetting({ withSubscriptions: true })` 查询订阅状态，但：

- 只有用户勾选了「总是保持以上选择」，才能查到
- 没勾选时返回空，**查不到剩余次数**
- 而且这只是前端接口，云函数推送前无法调用

结论：**必须自建 `subscribe_quota` 集合记账**。

### 4.2 记账规则

```
用户授权 accept   →  remaining += 1,  totalGranted += 1
推送成功          →  remaining -= 1,  totalUsed += 1
推送失败(43101)   →  remaining = 0    （用户已拒收，清零）
```

**43101 = 用户拒绝接收消息**。收到这个错误说明用户在设置里关闭了该模板的接收，此时额度记录已失效，直接清零并在前端提示用户重新开启。

### 4.3 一次授权多条额度的技巧

`requestSubscribeMessage` 单次最多传 **3 个模板 ID**。如果只有 1 个模板，用户一次只能给 1 次额度，体验很差。

**优化策略**：

| 策略 | 说明 |
|---|---|
| 引导勾选「总是保持以上选择」 | 用户勾选后，后续调用不再弹窗且自动 accept，可持续攒额度 |
| 关键节点重复引导 | 创建计划时、完成计划后、打开小程序看到额度不足时 |
| 额度可视化 | 「我的」页显示「剩余提醒次数：3」，低于 2 时红色提示 + 一键续订按钮 |
| 创建时即时补充 | 用户创建带提醒的计划时，若额度不足，当场弹授权 |

---

## 五、定时触发器实现

### 5.1 配置（`cloudfunctions/remind-scan/config.json`）

```json
{
  "triggers": [
    {
      "name": "remindScanTimer",
      "type": "timer",
      "config": "0 * * * * * *"
    }
  ]
}
```

### 🕳️ Cron 表达式坑

云开发定时触发器是 **7 位**，比标准 Linux cron 多「秒」和「年」：

```
   秒  分  时  日  月  周  年
   0   *   *   *   *   *   *     ← 每分钟的第 0 秒执行
```

| 需求 | 表达式 |
|---|---|
| 每分钟 | `0 * * * * * *` |
| 每 5 分钟 | `0 */5 * * * * *` |
| 每天 9 点 | `0 0 9 * * * *` |

写成 5 位（`* * * * *`）会**部署失败或不触发**，且错误信息不明显。

> **触发精度**：最小 1 分钟。所以提醒时间精度只能到分钟级，UI 上的时间选择器**不要提供秒选项**，避免用户预期落差。

### 5.2 扫描逻辑（含幂等锁）

```js
// cloudfunctions/remind-scan/index.js  （伪代码）
exports.main = async () => {
  const now = Date.now();
  const LOCK_TIMEOUT = 5 * 60 * 1000;  // 锁 5 分钟后视为超时可重抢

  // 1. 查到期且未处理的计划
  const due = await db.collection('plans').where({
    status: 'pending',
    deleted: false,
    remindStatus: 'pending',
    remindAt: _.lte(now).and(_.gt(now - 24 * 3600 * 1000)) // ⭐ 只处理24h内到期的
  }).limit(50).get();                                       // ⭐ 单次限量，防超时

  for (const plan of due.data) {
    // 2. ⭐ 抢锁：原子条件更新，防止定时器重复执行导致重复推送
    const lock = await db.collection('plans').where({
      planId: plan.planId,
      remindStatus: 'pending'          // 条件：仍是 pending 才能抢到
    }).update({
      data: { remindStatus: 'sending', remindLockAt: now }
    });
    if (lock.stats.updated === 0) continue;   // 没抢到，别的实例在处理

    // 3. 推送给所有成员
    const results = await pushToMembers(plan);

    // 4. 回写最终状态
    await db.collection('plans').where({ planId: plan.planId }).update({
      data: {
        remindStatus: results.anySuccess ? 'sent' : 'failed',
        updatedAt: Date.now(),          // ⭐ 刷新 updatedAt，让客户端能同步到状态变化
        rev: _.inc(1)
      }
    });
  }
};
```

### 🕳️ 幂等锁的必要性

云函数定时触发器**不保证只执行一次**。在网络抖动、实例重启等情况下可能重复触发。没有锁的话，用户会在同一分钟收到 2-3 条相同提醒。

**三层去重保险**：

```
第 1 层：remindStatus 条件更新抢锁       （主要手段）
第 2 层：push_logs 的 planId+openid 唯一索引  （数据库层兜底）
第 3 层：推送前查 push_logs 是否已有记录     （逻辑层兜底）
```

### 5.3 推送实现

```js
async function pushToMembers(plan) {
  const creator = await getUser(plan.creatorId);
  let anySuccess = false;

  for (const userId of plan.memberIds) {
    // 拿该账号所有活跃设备的 openid
    const bindings = await db.collection('user_bindings')
      .where({ userId, active: true }).get();

    for (const b of bindings.data) {
      // 去重检查
      const dup = await db.collection('push_logs')
        .where({ planId: plan.planId, openid: b.openid }).count();
      if (dup.total > 0) continue;

      // 额度检查
      const q = await getQuota(userId, b.openid, TEMPLATE_ID);
      if (!q || q.remaining <= 0) {
        await logPush(plan, userId, b.openid, 'fail', -1, 'NO_QUOTA');
        continue;
      }

      try {
        await cloud.openapi.subscribeMessage.send({
          touser: b.openid,
          templateId: TEMPLATE_ID,
          page: `pages/plan-detail/plan-detail?planId=${plan.planId}`,  // ⭐ 点击跳转
          miniprogramState: 'formal',   // developer | trial | formal
          lang: 'zh_CN',
          data: {
            thing1: { value: toThing(plan.title) },
            time2:  { value: toTime(plan.remindAt) },
            thing3: { value: toThing(creator.nickname) },
            thing4: { value: toThing(plan.desc || '请及时处理') }
          }
        });
        await consumeQuota(userId, b.openid, TEMPLATE_ID);   // 额度 -1
        await logPush(plan, userId, b.openid, 'success', 0, '');
        anySuccess = true;
      } catch (e) {
        if (e.errCode === 43101) await clearQuota(userId, b.openid); // 用户已拒收
        await logPush(plan, userId, b.openid, 'fail', e.errCode, e.errMsg);
      }
    }
  }
  return { anySuccess };
}
```

---

## 六、错误码对照表

推送失败时按此表排查：

| errCode | 含义 | 处理方式 |
|---|---|---|
| `40003` | openid 无效 | 该绑定失效，置 `active: false` |
| `43101` | **用户拒绝接收 / 无授权额度** | 额度清零，前端提示重新开启 |
| `47003` | **模板参数不符合规则** | 检查字段长度、格式、是否为空（最高频） |
| `41030` | page 路径不正确 | 页面必须已发布；开发版用 `miniprogramState: 'developer'` |
| `45009` | 接口调用超限 | 单模板日推送有上限，需降低频率 |
| `-1` | 系统繁忙 | 重试 |

> 🕳️ **41030 坑**：`page` 指向的页面**必须在已发布的线上版本中存在**。开发阶段测试推送时，如果页面还没发布，会一直报 41030。开发期把 `miniprogramState` 设为 `'developer'` 即可。

---

## 七、前端授权引导实现要点

```js
// services/remind.service.js
async function requestSubscribe() {
  const TMPL_ID = 'xxxxx';

  // ⚠️ 此函数必须在 tap 事件回调链中调用，不能有 await 在它之前打断手势上下文
  const res = await new Promise(resolve => {
    wx.requestSubscribeMessage({
      tmplIds: [TMPL_ID],
      success: resolve,
      fail: (e) => resolve({ [TMPL_ID]: 'fail', _err: e })
    });
  });

  if (res[TMPL_ID] === 'accept') {
    await cloud.call('subscribe', 'grant', { templateId: TMPL_ID });
    return { ok: true };
  }
  if (res[TMPL_ID] === 'ban') {
    // 模板被封禁，联系运营
    return { ok: false, reason: 'ban' };
  }
  return { ok: false, reason: 'reject' };
}
```

### 🕳️ 手势上下文坑

```js
// ❌ 错误：await 之后手势上下文丢失，requestSubscribeMessage 会失败
async onTapRemind() {
  await this.savePlan();               // 网络请求
  await requestSubscribe();            // 此时已不是手势上下文 → fail
}

// ✅ 正确：先请求订阅，再做其他异步操作
async onTapRemind() {
  const sub = await requestSubscribe(); // 手势后立即调用
  await this.savePlan();
}
```

**规则：`requestSubscribeMessage` 必须是 tap 回调里的第一个异步调用。**

---

## 八、用户拒绝授权的降级方案

| 情况 | 降级处理 |
|---|---|
| 用户拒绝授权 | 仍允许设置提醒时间，但标注「仅应内提醒」 |
| 额度耗尽 | 「我的」页红点 + 列表页顶部提示条「提醒额度不足，点击补充」 |
| 推送失败 | 打开小程序时，到期未完成的计划置顶 + 红色「已到期」标签 |

**应内提醒实现**（`services/plan.service.js`）：

```js
function getOverduePlans(plans) {
  const now = Date.now();
  return plans.filter(p =>
    p.status === 'pending' && !p.deleted &&
    p.remindAt && p.remindAt <= now
  );
}
// 列表排序：已到期 > 有提醒且临近 > 无提醒，各组内按 createdAt 倒序
```

---

## 九、测试要点

提醒功能**无法在开发者工具完整测试**，必须真机验证：

| 测试项 | 方法 |
|---|---|
| 订阅授权弹窗 | 真机预览，检查是否弹出、accept 后额度是否 +1 |
| 定时触发器 | 云开发控制台可手动「测试」触发；或设一个 2 分钟后的提醒等待 |
| 推送到达 | 真机，微信「服务通知」里查看 |
| 点击跳转 | 从服务通知点进来，确认跳到正确的计划详情 |
| 多设备推送 | 同一账号在两个微信登录，确认都收到 |
| 重复推送 | 手动多次触发 remind-scan，确认只收到一条 |
| 额度耗尽 | 把 remaining 手动改 0，确认不推送且前端有提示 |
| 时间显示 | ⭐ 重点检查消息里的时间是否为北京时间（验证 UTC+8 处理） |

> 云开发控制台 → 云函数 → remind-scan → 「云端测试」可以手动触发，是调试定时任务的主要手段。
