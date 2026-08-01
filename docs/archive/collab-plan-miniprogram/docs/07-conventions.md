---
module: archive
title: 07-conventions.md
tags: [collab-plan-miniprogram]
source:
  project: collab-plan-miniprogram
  repo: https://github.com/Simiely/collab-plan-miniprogram
  file: docs/07-conventions.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/collab-plan-miniprogram/blob/main/docs/07-conventions.md)

# 07 · 编码规范与约定

> 上级导航：[README 总导航](./README.md)
> 写代码前请通读一遍。规范的目的是让任何人（含 AI）接手时不用猜。

---

## 一、命名约定

### 1.1 文件命名

| 类型 | 规则 | 示例 |
|---|---|---|
| 页面目录 | kebab-case | `plan-detail/` |
| 页面文件 | 与目录同名 | `plan-detail.js/.json/.wxml/.wxss` |
| 组件目录 | kebab-case | `plan-card/` |
| 服务层 | `xxx.service.js` | `plan.service.js` |
| 状态层 | `xxx.store.js` | `plan.store.js` |
| 工具/核心 | kebab-case | `event-bus.js` |
| 云函数目录 | kebab-case | `remind-scan/` |

### 1.2 变量与函数

```js
const MAX_TITLE_LENGTH = 50;      // 常量：UPPER_SNAKE_CASE
let planList = [];                 // 变量：camelCase
function buildMemberIds() {}       // 函数：camelCase，动词开头
class SyncEngine {}                // 类：PascalCase
const _privateCache = {};          // 模块内私有：下划线前缀
```

**布尔变量**必须用 `is/has/can/should` 开头：

```js
const isLoading = true;
const hasQuota = false;
const canComplete = true;
```

**异步函数**明确语义，不用 `getXxx` 表示网络请求：

```js
fetchPlanList()      // ✅ 网络请求
loadPlanList()       // ✅ 从本地加载
getPlanList()        // ✅ 同步取内存数据
```

### 1.3 事件命名

```js
// 页面方法：on + 元素 + 动作
onPlanCardTap()
onCompleteButtonTap()
onRefreshPull()

// 组件对外事件：kebab-case，不加 on
this.triggerEvent('complete', { planId });
// 使用：<plan-card bind:complete="onPlanComplete" />
```

---

## 二、目录归属决策树

不确定代码该放哪里时，按这个走：

```
这段代码...
├─ 操作了 setData / 页面生命周期？        → pages/
├─ 是纯 UI 展示、通过 triggerEvent 上抛？  → components/
├─ 包含业务规则（谁能完成、怎么算过期）？   → services/
├─ 属于同步流程（水位线、合并、队列）？     → sync/
├─ 是技术能力封装（网络、存储、日志）？     → core/
│   └─ 注意：core/ 里不能出现 plan、member 等业务词汇
└─ 是纯函数（输入→输出，无副作用）？        → utils/
```

---

## 三、异步与错误处理

### 3.1 统一用 async/await，禁止裸回调

```js
// ❌ 回调地狱
wx.getStorage({ key: 'a', success: r1 => {
  wx.request({ ..., success: r2 => { ... } })
}});

// ✅ Promise 化
const data = await storage.get('a');
const res = await cloud.call('plan', 'list');
```

`core/` 层负责把所有 wx API 包成 Promise，业务代码不出现 `success/fail` 回调。

### 3.2 错误处理三层责任

| 层 | 责任 |
|---|---|
| **云函数** | 返回结构化错误 `{ code: 4001, msg: 'NO_PERMISSION' }`，不 throw 到外面 |
| **core/cloud.js** | 统一拦截 401、网络错误、超时；转换为业务异常抛出 |
| **services/** | catch 业务异常 → 转成用户可读提示 → 决定是否吞掉 |
| **pages/** | 只处理 UI 反馈（loading、toast），不判断错误类型 |

```js
// services/plan.service.js
async function completePlan(planId) {
  try {
    const res = await cloud.call('plan', 'complete', { planId });
    if (res.alreadyDone) {
      return { ok: true, tip: `该计划已由 ${res.byName} 完成` };
    }
    localDb.updatePlan(planId, { status: 'done' });
    planStore.notify();
    return { ok: true };
  } catch (e) {
    logger.error('completePlan failed', e);
    return { ok: false, tip: errorMap(e.code) };   // 转成可读提示
  }
}

// pages/todo/todo.js —— 页面只管 UI
async onCompleteTap(e) {
  wx.showLoading({ mask: true });
  const r = await planService.completePlan(e.detail.planId);
  wx.hideLoading();
  if (r.tip) wx.showToast({ title: r.tip, icon: 'none' });
}
```

### 3.3 错误码规范（`common/constants.js`）

| 区间 | 含义 |
|---|---|
| `0` | 成功 |
| `401` | 未登录 / Token 失效 → 前端统一跳登录 |
| `1000-1999` | 参数错误 |
| `2000-2999` | 权限错误 |
| `3000-3999` | 业务规则错误（如计划已完成） |
| `4000-4999` | 数据不存在 |
| `5000-5999` | 服务端内部错误 |

每个错误码在 `core/error.js` 里有对应的中文提示，禁止在页面里硬编码提示文案。

---

## 四、setData 纪律

| 规则 | 反例 | 正例 |
|---|---|---|
| 合并调用 | 连续 3 次 `setData` | 合并成 1 次 |
| 路径更新 | `setData({ list: newList })` | `setData({ 'list[3].status': 'done' })` |
| 精简字段 | 把完整 plan 对象塞进 data | 只放视图用到的字段 |
| 非渲染数据 | `setData({ _rawData })` | `this._rawData = xxx` |
| 大对象 | 一次 setData 超过 100KB | 分批或精简 |

```js
// 页面里区分"渲染数据"和"原始数据"
Page({
  data: {
    list: [],        // 渲染用，字段精简
  },
  _rawPlans: null,   // 原始完整数据，挂在实例上不进 data

  render() {
    this.setData({
      list: this._rawPlans.map(p => ({
        planId: p.planId,
        title: p.title,
        remindText: formatRemind(p.remindAt),
        memberCount: p.memberIds.length,
        isOverdue: p.remindAt && p.remindAt < Date.now()
      }))
    });
  }
});
```

---

## 五、云函数规范

### 5.1 统一结构

```js
// cloudfunctions/plan/index.js
const cloud = require('wx-server-sdk');
const { ok, fail } = require('./common/response');
const { authGuard } = require('./common/auth-guard');

cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });

const handlers = {
  create:   require('./handlers/create'),
  complete: require('./handlers/complete'),
  update:   require('./handlers/update'),
  remove:   require('./handlers/remove'),
};

exports.main = async (event, context) => {
  const { action, token, payload = {} } = event;
  try {
    const handler = handlers[action];
    if (!handler) return fail(1001, 'UNKNOWN_ACTION');

    const userId = await authGuard(token);       // ⭐ 必须第一步
    const wxContext = cloud.getWXContext();

    return await handler({ userId, payload, wxContext });
  } catch (e) {
    if (e.code === 401) return fail(401, e.msg);
    console.error('[plan]', action, e);           // ⭐ 记录但不泄露给前端
    return fail(5000, 'INTERNAL_ERROR');
  }
};
```

### 5.2 云函数硬性规则

| 规则 | 原因 |
|---|---|
| userId 只能从 Token 解出 | 防越权（[P02](./09-pitfalls.md)） |
| 时间只用云函数 `Date.now()` | 客户端时间不可信 |
| 面向用户的时间格式化必须 +8 小时 | 云函数是 UTC（[P05](./09-pitfalls.md)） |
| 禁止 `.remove()`，一律软删除 | 同步需要（[P09](./09-pitfalls.md)） |
| 空值用 `null` 不用 `undefined` | update 会忽略 undefined（[P03](./09-pitfalls.md)） |
| 任何 `.get()` 前评估是否超 100 条 | 单次上限（[P04](./09-pitfalls.md)） |
| 修改 creatorId/assigneeIds 必须重算 memberIds | 冗余字段一致性 |
| 任何写操作必须更新 `updatedAt` 和 `rev` | 同步依赖 |
| 返回体禁止含 passwordHash/salt | 安全 |
| 错误详情记 `console.error`，不返回前端 | 防信息泄露 |

### 5.3 更新操作模板

所有对 `plans` 的更新都必须带上这三个字段：

```js
await db.collection('plans').where({ planId }).update({
  data: {
    ...changes,
    updatedAt: Date.now(),    // ⭐ 同步水位线依赖
    rev: _.inc(1),            // ⭐ 版本号
  }
});
```

建议封装成 `common/db.js` 的 `updatePlan(planId, changes)`，强制统一。

---

## 六、样式规范

### 6.1 全局设计变量（`app.wxss`）

```css
page {
  /* 颜色 */
  --color-primary:    #0052D9;
  --color-success:    #00A870;
  --color-warning:    #ED7B2F;
  --color-danger:     #D54941;
  --color-text:       #1A1A1A;
  --color-text-sub:   #757575;
  --color-border:     #E7E7E7;
  --color-bg:         #F5F5F5;
  --color-card:       #FFFFFF;

  /* 间距 */
  --space-xs: 8rpx;
  --space-sm: 16rpx;
  --space-md: 24rpx;
  --space-lg: 32rpx;
  --space-xl: 48rpx;

  /* 圆角 */
  --radius-sm: 8rpx;
  --radius-md: 16rpx;
  --radius-lg: 24rpx;

  /* 字号 */
  --font-xs: 22rpx;
  --font-sm: 26rpx;
  --font-md: 30rpx;
  --font-lg: 34rpx;
  --font-xl: 40rpx;
}
```

**禁止在页面 wxss 里硬编码颜色值**，一律用变量。这样后续做暗黑模式只需改变量。

### 6.2 单位与布局

| 规则 | 说明 |
|---|---|
| 尺寸用 `rpx` | 750rpx = 屏幕宽度，自动适配 |
| 字号可用 `rpx` | 保持与设计稿一致 |
| 布局优先 flex | 少用 float、absolute |
| 安全区适配 | 底部用 `padding-bottom: env(safe-area-inset-bottom)` |
| 类名 BEM 风格 | `.plan-card`、`.plan-card__title`、`.plan-card--done` |

---

## 七、注释规范

**注释写"为什么"，不写"是什么"**。

```js
// ❌ 无意义
// 设置 lastSyncAt
storage.set('lastSyncAt', serverTime);

// ✅ 说明原因
// 必须用服务器时间，用本地时间会因手机时钟偏差导致数据永久丢失（见 docs/09-pitfalls.md P08）
storage.set('lastSyncAt', serverTime);
```

**踩过的坑必须在代码里留链接**：

```js
// ⚠️ 必须在 tap 回调第一行调用，前面有 await 会丢失手势上下文
// 详见 docs/09-pitfalls.md P18
const sub = await remindService.requestSubscribe();
```

**关键函数写 JSDoc**：

```js
/**
 * 增量同步：先重放离线队列，再拉取服务器差异
 * @param {Object}  opts
 * @param {boolean} opts.force  跳过 60s 节流，强制同步
 * @returns {Promise<{added:number, updated:number, removed:number}>}
 * @throws  {SyncError} 网络异常或服务端错误时抛出，调用方需 catch
 */
async function syncAll(opts = {}) { ... }
```

---

## 八、Git 提交规范

```
<type>(<scope>): <subject>

feat(sync):     实现水位线增量拉取
fix(remind):    修复云函数 UTC 时区导致提醒时间早 8 小时
docs(pitfalls): 补充 P40 分包预加载失效问题
refactor(core): 抽离 storage schema 版本管理
perf(todo):     列表改为路径更新，减少 setData 体积
chore(deps):    升级 TDesign 到 1.x
```

| type | 用途 |
|---|---|
| `feat` | 新功能 |
| `fix` | 修 bug |
| `docs` | 只改文档 |
| `refactor` | 重构，无功能变化 |
| `perf` | 性能优化 |
| `test` | 测试相关 |
| `chore` | 构建、依赖、配置 |

`scope` 用模块名：`sync` `auth` `plan` `remind` `core` `ui` `docs`

---

## 九、代码提交前自检

- [ ] 页面里没有 `wx.cloud.callFunction` / `wx.setStorage` / `wx.request`
- [ ] service 里没有 `setData`
- [ ] core/utils 里没有业务词汇（plan/member/remind）
- [ ] 云函数没有用 `event.userId`
- [ ] 云函数的更新操作都带了 `updatedAt` 和 `rev`
- [ ] 没有 `.remove()` 硬删除
- [ ] 没有硬编码的颜色值
- [ ] 没有 console.log 残留（用 logger）
- [ ] 新增字段已更新 [03-data-model.md](./03-data-model.md)
- [ ] 行为变更已记录 [10-changelog.md](./10-changelog.md)
- [ ] 踩的坑已记录 [09-pitfalls.md](./09-pitfalls.md)
