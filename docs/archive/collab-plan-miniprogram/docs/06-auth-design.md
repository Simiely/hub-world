---
module: archive
title: 06-auth-design.md
tags: [collab-plan-miniprogram]
source:
  project: collab-plan-miniprogram
  repo: https://github.com/Simiely/collab-plan-miniprogram
  file: docs/06-auth-design.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/collab-plan-miniprogram/blob/main/docs/06-auth-design.md)

# 06 · 账号体系与安全设计

> 上级导航：[README 总导航](./README.md)
> 对应代码：`cloudfunctions/auth/` + `miniprogram/core/session.js` + `miniprogram/services/auth.service.js`

---

## 一、为什么不用微信授权登录

需求明确：**「小程序会内置账号，通过指定的账号密码登录指定账号」**。

这带来一个必须正视的架构后果：

```
业务身份 (userId)  ≠  微信身份 (openid)
      ↑                      ↑
  谁创建/谁可见/谁完成      订阅消息推给谁
```

二者通过 `user_bindings` 表关联。**这是本项目最容易出 bug 的地方**，务必理解清楚。

| 对比 | 微信授权登录 | 自建账号（本项目） |
|---|---|---|
| 身份来源 | 云函数自动拿 `wxContext.OPENID` | 用户名密码校验后签发 Token |
| 安全责任 | 微信承担 | **我们自己承担**（密码存储、Token 签发） |
| 推送 | 直接用 openid | 需查绑定表 |
| 数据库权限 | 可用「仅创建者可读写」 | **只能走云函数**，前端零权限 |
| 跨设备 | 换微信=换身份 | 同账号可多设备登录 |

---

## 二、密码安全

### 2.1 绝对红线

| ❌ 绝不允许 | ✅ 必须做到 |
|---|---|
| 数据库存明文密码 | scrypt / bcrypt 加盐哈希 |
| 用 MD5 / SHA1 哈希 | 用慢哈希（scrypt / bcrypt / PBKDF2） |
| 全局共用一个盐 | 每个账号独立随机盐 |
| 前端做密码校验 | 校验只在云函数内 |
| 云函数返回 passwordHash | 任何接口都不返回哈希和盐 |
| 日志打印密码 | 日志中密码字段一律脱敏为 `***` |

### 2.2 实现（`cloudfunctions/common/password.js`）

```js
const crypto = require('crypto');

const SCRYPT_KEYLEN = 64;
const SCRYPT_OPTS = { N: 16384, r: 8, p: 1 };  // 约 100ms，可接受

function genSalt() {
  return crypto.randomBytes(16).toString('hex');
}

function hashPassword(password, salt) {
  const buf = crypto.scryptSync(password, salt, SCRYPT_KEYLEN, SCRYPT_OPTS);
  return 'scrypt$' + buf.toString('hex');
}

function verifyPassword(password, salt, storedHash) {
  const computed = hashPassword(password, salt);
  // ⭐ 必须用时间恒定比较，防时序攻击
  const a = Buffer.from(computed);
  const b = Buffer.from(storedHash);
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(a, b);
}

module.exports = { genSalt, hashPassword, verifyPassword };
```

> 🕳️ **坑**：`scryptSync` 的 N 参数设太大（如 1048576）会导致云函数超时或内存不足。`N=16384` 在 256MB 内存下约 100ms，是安全性与性能的平衡点。
> 若报 `memory limit exceeded`，把 `auth` 云函数内存调到 512MB 或降低 N。

### 2.3 密码策略

| 项 | 规则 |
|---|---|
| 最小长度 | 8 位 |
| 复杂度 | 至少包含字母和数字 |
| 校验位置 | 前端做体验校验 + **云函数强制校验** |
| 传输 | 依赖 HTTPS（云函数调用天然加密），不做额外前端加密 |
| 登录失败限制 | 同一账号连续失败 5 次，锁定 15 分钟 |

**防爆破实现**：在 `users` 加两个字段

```js
failedCount:  0,           // 连续失败次数
lockedUntil:  null         // 锁定到期时间戳
```

---

## 三、Token 设计

### 3.1 方案选择

用**自签名 Token**（类 JWT），不引入第三方库，避免增加云函数依赖体积。

```
Token 结构：base64url(payload) + "." + HMAC-SHA256签名

payload = { uid: "u_a1b2c3", iat: 1730000000000, exp: 1732592000000 }
签名密钥 = 云函数环境变量 AUTH_SECRET（绝不硬编码在代码里）
```

### 3.2 实现（`cloudfunctions/common/token.js`）

```js
const crypto = require('crypto');
const SECRET = process.env.AUTH_SECRET;      // ⭐ 环境变量，不写在代码里
const TTL = 30 * 24 * 3600 * 1000;           // 30 天

function sign(userId) {
  const payload = { uid: userId, iat: Date.now(), exp: Date.now() + TTL };
  const body = Buffer.from(JSON.stringify(payload)).toString('base64url');
  const sig = crypto.createHmac('sha256', SECRET).update(body).digest('base64url');
  return `${body}.${sig}`;
}

function verify(token) {
  if (!token || typeof token !== 'string') return null;
  const [body, sig] = token.split('.');
  if (!body || !sig) return null;

  const expect = crypto.createHmac('sha256', SECRET).update(body).digest('base64url');
  // ⭐ 时间恒定比较
  if (sig.length !== expect.length) return null;
  if (!crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expect))) return null;

  let payload;
  try { payload = JSON.parse(Buffer.from(body, 'base64url').toString()); }
  catch { return null; }

  if (!payload.exp || payload.exp < Date.now()) return null;   // 过期
  return payload.uid;
}
```

> ⚠️ `AUTH_SECRET` 在云开发控制台 → 云函数 → 配置 → 环境变量中设置。**不要提交到代码仓库**。
> 更换 SECRET 会导致所有用户登录态失效（相当于强制全员重登），可作为安全事故的应急手段。

### 3.3 鉴权守卫（`cloudfunctions/common/auth-guard.js`）

```js
async function authGuard(token) {
  const userId = verify(token);
  if (!userId) throw { code: 401, msg: 'TOKEN_INVALID' };

  // 可选：查用户状态，被禁用的账号立即失效
  const u = await db.collection('users').doc(userId).get().catch(() => null);
  if (!u || u.data.status !== 'active') throw { code: 401, msg: 'USER_DISABLED' };

  return userId;
}
```

**每个云函数的第一行都必须调用它**（除 `auth.login`）。

> 🕳️ **越权漏洞坑**：绝不能这样写
> ```js
> const userId = event.userId;   // ❌ 前端传的，可任意伪造
> ```
> 攻击者改一个 userId 就能操作别人的数据。**userId 只能从 Token 解出**。

---

## 四、登录流程

```
┌─────────────────────────────────────────────────────────┐
│  前端 login 页                                            │
│    输入 username + password                              │
│    调 auth.service.login()                               │
└───────────────────────┬─────────────────────────────────┘
                        │  callFunction('auth', {action:'login', ...})
                        ▼
┌─────────────────────────────────────────────────────────┐
│  云函数 auth.login                                        │
│                                                          │
│  1. 参数校验（username/password 非空、长度）               │
│  2. 查 users where username                              │
│     └─ 不存在 → 返回「账号或密码错误」                     │
│        ⭐ 不能区分"账号不存在"和"密码错误"（防账号枚举）     │
│  3. 检查 lockedUntil，锁定中 → 返回剩余时间                │
│  4. verifyPassword                                       │
│     ├─ 失败 → failedCount+1，达5次则锁15分钟 → 返回错误    │
│     └─ 成功 → failedCount=0, lockedUntil=null            │
│  5. ⭐ 取 wxContext.OPENID（云函数自动带，无需前端传）      │
│  6. ⭐ 绑定处理：                                          │
│     a. 把该 openid 的其他 active 绑定置为 false            │
│        （同一微信改登别的账号，要断开旧账号）               │
│     b. upsert (userId, openid) 绑定为 active              │
│  7. 签发 Token                                            │
│  8. 更新 lastLoginAt                                      │
│  9. 返回 { token, user: {脱敏信息} }                       │
└───────────────────────┬─────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────┐
│  前端                                                     │
│  1. session.save({ token, userId, expireAt })            │
│  2. ⭐ 清空本地旧数据（换账号了！）                         │
│     storage.clearBusinessData(); lastSyncAt = 0           │
│  3. 触发首次全量同步                                       │
│  4. 跳转 tabBar 首页                                      │
└─────────────────────────────────────────────────────────┘
```

### 🕳️ 换账号不清缓存的坑

```js
// ❌ 登录成功后直接跳首页
wx.switchTab({ url: '/pages/todo/todo' });
// 结果：显示的还是上一个账号的计划数据！

// ✅ 必须先清业务缓存并重置水位线
storage.clearBusinessData();     // 清 plans / opQueue
storage.set('lastSyncAt', 0);    // 重置水位线，触发全量同步
```

这个 bug 在单账号测试时**发现不了**，只有切换账号才暴露。务必在测试用例里覆盖。

---

## 五、登录态管理（前端）

### 5.1 `core/session.js`

```js
session.save({ token, userId, expireAt })
session.get()          // → { token, userId, expireAt } | null
session.getUserId()    // → userId | null
session.isValid()      // → 本地判断是否过期（不查服务器）
session.clear()        // → 清除
```

### 5.2 登录态守卫策略

| 时机 | 策略 |
|---|---|
| App `onLaunch` | 同步读本地 session，**只做本地过期判断**，不发网络请求 |
| 首个页面 `onLoad` | 无有效 session → `wx.redirectTo` 到 login 页 |
| 任意云函数返回 401 | `core/cloud.js` 统一拦截 → 清 session → 跳登录页 |
| 距过期 < 3 天 | 后台静默调 `auth.verify` 换发新 Token（滑动续期） |

> 🕳️ **坑**：不要在 `onLaunch` 里同步等待网络校验 Token。会阻塞首屏 1-2 秒。本地判断过期时间即可，真正的校验交给第一次业务请求的 401 拦截。

### 5.3 tabBar 页面的登录跳转坑

```js
// ❌ tabBar 页面不能用 redirectTo/navigateTo 跳到非 tab 页再跳回来
// ❌ 也不能在 app.onLaunch 里 wx.redirectTo（此时页面栈还没建立）

// ✅ 正确做法：在首个 tab 页的 onShow 里判断
onShow() {
  if (!session.isValid()) {
    wx.reLaunch({ url: '/pages/login/login' });   // ⭐ 用 reLaunch，清空页面栈
    return;
  }
  // ...正常逻辑
}
```

---

## 六、退出登录

```
1. 调 auth.logout 云函数
   └─ 把 (userId, 当前openid) 的绑定置 active=false   ⭐ 不再收到该账号的提醒
2. 前端 session.clear()
3. 清空所有业务缓存（plans / lastSyncAt / opQueue）
4. wx.reLaunch 到 login 页
```

> 🕳️ **坑**：忘记解绑 openid 的话，用户退出登录后**仍会收到该账号的提醒推送**，属于严重体验问题和潜在的信息泄露。

---

## 七、成员列表的脱敏

创建计划时要选协作者，需要拉取账号列表。**这是唯一会暴露账号信息的接口**，必须严格脱敏。

```js
// cloudfunctions/plan/index.js → action: 'memberList'
const userId = await authGuard(event.token);       // ⭐ 必须登录

const res = await db.collection('users')
  .where({ status: 'active' })
  .field({                                          // ⭐ 白名单式返回
    _id: true,
    nickname: true,
    avatarText: true,
    avatarColor: true
  })
  .limit(200)
  .get();
```

| ✅ 可返回 | ❌ 绝不返回 |
|---|---|
| `_id`(userId) | `passwordHash` |
| `nickname` | `salt` |
| `avatarText` / `avatarColor` | `username`（登录名，泄露会助长撞库） |
| | `lastLoginAt` / `failedCount` |

> 用 `.field({ 白名单: true })` 而不是查全量再删字段。前者从数据库层就不返回，后者一旦忘记删就泄露。

---

## 八、安全检查清单

上线前逐项确认：

- [ ] 所有集合权限为「仅管理端可读写」
- [ ] `users` 表无明文密码
- [ ] `AUTH_SECRET` 配在环境变量，未提交到仓库
- [ ] 所有云函数（除 login）第一行调 `authGuard`
- [ ] 没有任何地方使用 `event.userId`（全局搜索确认）
- [ ] 成员列表接口用 `field` 白名单
- [ ] 登录失败不区分「账号不存在」和「密码错误」
- [ ] 有登录失败次数限制
- [ ] 退出登录会解绑 openid
- [ ] 换账号登录会清空本地缓存
- [ ] 日志中无密码、无完整 Token
- [ ] 云函数返回体中无 `passwordHash` / `salt`

---

## 九、微信审核相关注意

自建账号体系在小程序审核中有特定要求：

| 要求 | 说明 |
|---|---|
| 用户隐私保护指引 | 必须在小程序后台配置，声明收集的信息类型 |
| 不得强制授权微信信息 | 本项目不用微信授权登录，天然合规 |
| 账号体系需说明来源 | 提审备注中说明「账号由企业/组织内部分配，非公开注册」 |
| 提供测试账号 | ⭐ 提审时**必须**在备注里提供可用的测试账号密码，否则审核员无法进入，必被驳回 |

> 🔴 **最高频驳回原因**：审核员打开小程序看到登录页，没有测试账号进不去 → 直接驳回。
> 提审备注模板见 [11-testing-release.md](./11-testing-release.md)。
