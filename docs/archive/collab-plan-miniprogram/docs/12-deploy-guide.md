---
module: archive
title: 12-deploy-guide.md
tags: [collab-plan-miniprogram]
source:
  project: collab-plan-miniprogram
  repo: https://github.com/Simiely/collab-plan-miniprogram
  file: docs/12-deploy-guide.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/collab-plan-miniprogram/blob/main/docs/12-deploy-guide.md)

# 12 · 部署与初始化指南 🚀

> 上级导航：[README 总导航](./README.md)
> **第一次把项目跑起来，照着本文从头到尾做一遍即可。**
> 全程约 25 分钟，其中 8 处需要你手动填写真实值。

---

## 零、开始之前

需要准备：

| 项 | 说明 | 没有怎么办 |
|---|---|---|
| 小程序 AppID | 在 [mp.weixin.qq.com](https://mp.weixin.qq.com) 注册 | 个人主体即可，免费 |
| 微信开发者工具 | [下载稳定版](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html) | — |
| Node.js ≥ 14 | 用于 `npm install` 与公共层同步脚本 | — |

> ⚠️ **测试号不行**：云开发需要正式 AppID，微信提供的「测试号」无法开通云开发。

---

## 一、填 AppID 与云环境（3 处占位符）

### 1.1 创建云环境

微信开发者工具 → 打开本项目 → 顶部「云开发」按钮 → 开通。

建议**创建两个环境**：

| 环境 | 建议名称 | 用途 |
|---|---|---|
| 开发环境 | `plan-dev` | 开发者工具、真机预览 |
| 生产环境 | `plan-prod` | 体验版、正式版 |

> 免费额度下两个环境够用。只创建一个也能跑，把下面两个 ID 填成同一个即可，
> 但**上线前务必分开** —— 否则调试时的脏数据会直接进正式库。

创建后在云开发控制台「设置 → 环境变量」页面能看到**环境 ID**（形如 `plan-dev-3g8xxxxx`）。

### 1.2 替换占位符

| 文件 | 占位符 | 填什么 |
|---|---|---|
| `project.config.json` | `TOUCH_YOUR_APPID_HERE` | 你的小程序 AppID |
| `miniprogram/config/env.js` | `REPLACE_DEV_ENV_ID` | 开发环境 ID |
| `miniprogram/config/env.js` | `REPLACE_PROD_ENV_ID` | 生产环境 ID |

> 🔴 **只在这三处填**。代码里任何其他地方都不允许出现环境 ID 硬编码 ——
> 否则提审前改漏一处就是线上事故（连到了开发库）。

检查是否漏改：

```bash
grep -rn "REPLACE_\|TOUCH_YOUR" --include="*.js" --include="*.json" miniprogram config project.config.json
```

---

## 二、安装依赖并构建 npm

```bash
npm install          # 会自动触发 postinstall → 同步云函数公共层
```

然后在**微信开发者工具**里：

> 顶部菜单「工具」→「构建 npm」→ 等待提示成功

构建后会生成 `miniprogram/miniprogram_npm/`，TDesign 组件才能用。

> 🕳️ 见 [P32](./09-pitfalls.md#-p32-使用-tdesign-组件报-component-is-not-found)：
> 忘了「构建 npm」会报 `component is not found`。
> M1 阶段的登录页刻意用了原生组件，即使没构建也能跑通登录，方便你先验证链路。

---

## 三、部署云函数

### 3.1 同步公共层（每次改完 `_shared` 都要做）

```bash
npm run sync:shared
```

> 🔴 见 [P40](./09-pitfalls.md#-p40-云函数-require-不到上级目录的公共代码)：
> 云函数独立打包，引用不到目录外的文件，
> 所以 `_shared/` 必须物理复制成每个函数的 `common/`。
> **改完 `_shared` 忘了跑这条，症状是「代码改了却没生效」。**

### 3.2 配置云函数环境变量

在**云开发控制台 → 云函数 → 对应函数 → 配置 → 环境变量**中添加：

| 云函数 | 变量名 | 值 | 说明 |
|---|---|---|---|
| `auth` | `AUTH_SECRET` | ≥16 位随机字符串 | 🔴 Token 签名密钥 |
| `init-db` | `INIT_KEY` | ≥16 位随机字符串 | 🔴 初始化接口的准入口令 |

生成随机串：

```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

> 🔴 **绝不要把这两个值写进代码或提交到仓库。**
> `AUTH_SECRET` 一旦更换，所有用户登录态立即失效 —— 这也是安全事故时的应急手段。
> 未配置 `AUTH_SECRET` 时 `auth` 函数会**直接抛错**而不是用默认值，这是故意的
> （配置缺失的默认行为必须是最安全的那个）。

### 3.3 上传

> 🔴 **上传前必做**：在项目根目录跑 `npm run sync:shared`。
> 云函数不能 `require` 上级目录（[P40](./09-pitfalls.md)），`_shared/` 要复制进各函数的 `common/`。
> 改了 `_shared/` 却忘了同步再上传，现象是「代码明明改了却没生效」，极难排查。

在开发者工具的资源管理器里，逐个右键 →「上传并部署：云端安装依赖」：

| 云函数 | 何时需要重传 |
|---|---|
| `auth` | 改了 `auth/` 或 **任何 `_shared/` 文件** |
| `init-db` | 同上（仅初始化用，上线前要删掉） |
| `plan` | M2 新增；改了 `plan/` 或 **任何 `_shared/` 文件** |

首次部署每个函数约 30-60 秒。

> `auth` 函数用了 scrypt 慢哈希（约 70ms），若日志里出现 `memory limit exceeded`，
> 把该函数内存调到 512MB。见 [P22](./09-pitfalls.md)。

---

## 四、初始化数据库 ⭐

### 4.1 建集合 + 写测试账号

在开发者工具「云开发控制台 → 云函数 → init-db → 云端测试」中，
把测试参数填成（`initKey` 换成你在 3.2 里设的值）：

```json
{
  "action": "init",
  "payload": { "initKey": "你在 3.2 设置的 INIT_KEY" }
}
```

执行成功后会返回：
- `collections`：6 个集合的创建结果
- `users`：3 个测试账号（`test1` / `test2` / `test3`，默认密码 `Test1234`）
- `indexChecklist`：**下一步要手动创建的索引清单**

想自定义测试账号密码：加 `"password": "你的密码"`（需 ≥8 位且含字母和数字）。
账号已存在时默认跳过；要强制重置加 `"force": true`。

### 4.2 🔴 逐个确认集合权限

云开发控制台 → 数据库 → 每个集合 → 右上角「权限设置」→ 选 **「仅管理端可读写」**。

6 个集合**一个都不能漏**：
`users` `user_bindings` `plans` `subscribe_quota` `push_logs` `op_logs`

> 🔴 见 [P01](./09-pitfalls.md#-p01-前端能直接读到数据库里的密码哈希)：
> 默认权限下，任何人在 console 里一行代码就能拖走**全部密码哈希**。
> 本项目用自建账号体系，`_openid` 与业务身份无关，
> 「仅创建者可读写」这一档**完全不可用**。

验证方式（在开发者工具 console 执行，**应当报权限错误**）：

```js
wx.cloud.database().collection('users').get().then(console.log).catch(console.error)
```

### 4.3 ⭐ 手动创建索引

云开发控制台 → 数据库 → 选中集合 → 「索引管理」→ 新建索引。

> 🔴 见 [P43](./09-pitfalls.md#-p43-索引忘了建数据量涨上来后同步接口突然变慢)：
> **Node SDK 没有创建索引的接口**，只能手动建。
> 测试期几十条数据感觉不出来，数据涨上来后同步接口会直接超时。

| 集合 | 索引名 | 字段（顺序不能错） | 唯一 |
|---|---|---|:---:|
| `users` | `idx_username` | `username` ↑ | ✅ |
| `users` | `idx_status` | `status` ↑ | ❌ |
| `user_bindings` | `idx_user_active` | `userId` ↑ + `active` ↑ | ❌ |
| `user_bindings` | `idx_openid` | `openid` ↑ | ❌ |
| `user_bindings` | `idx_user_openid` | `userId` ↑ + `openid` ↑ | ✅ |
| `plans` | `idx_planId` | `planId` ↑ | ✅ |
| `plans` | `idx_member_updated` | `memberIds` ↑ + `updatedAt` ↑ | ❌ |
| `plans` | `idx_member_status` | `memberIds` ↑ + `status` ↑ + `deleted` ↑ | ❌ |
| `plans` | `idx_remind_scan` | `remindStatus` ↑ + `remindAt` ↑ | ❌ |
| `subscribe_quota` | `idx_quota` | `userId` ↑ + `openid` ↑ + `templateId` ↑ | ✅ |
| `push_logs` | `idx_push_dedup` | `planId` ↑ + `openid` ↑ | ✅ |
| `op_logs` | `idx_user_at` | `userId` ↑ + `at` ↓ | ❌ |

> ⭐ 其中 `plans.idx_member_updated` 是**增量同步的主查询索引**，性能命脉，绝不能漏。
> `push_logs.idx_push_dedup` 是**推送去重的最后一道保险**，M4 阶段必须已存在。
>
> 🔴 **M2 已上线，`plans.idx_member_status` 现在就必须建好**——
> 列表页的每一次查询（`memberIds + status + deleted`）都走它。
> 不建也能跑，但会全表扫描，数据量涨上来后突然变慢，且很难联想到是索引问题（[P43](./09-pitfalls.md)）。

---

## 五、验证

编译运行小程序，应当能：

1. 启动后停在**登录页**（首次无登录态）
2. 开发版底部有测试账号快捷入口，点 `test1` 自动填充
3. 点「登录」→ 进入「待完成」页，显示「你好，测试一」和空状态
4. 「我的」页显示账号信息 → 「退出登录」→ 回到登录页
5. 用 `test2` 登录 → 数据不串（M1 阶段列表都是空的，M2 后此项才有实感）

### M1 验收自检

| 检查项 | 怎么验 |
|---|---|
| ✅ 两个账号能分别登录 | test1 退出后用 test2 登录 |
| ✅ 登录态能保持 | 关闭小程序再打开，不需要重新登录 |
| ✅ 密码错 5 次锁定 15 分钟 | 故意输错 5 次，第 6 次提示「账号已锁定，请 15 分钟后再试」 |
| ✅ 前端读不到数据库 | console 执行 4.2 里那行代码应报权限错误 |
| ✅ 无越权写法 | `grep -rn "event.userId\|payload.userId" cloudfunctions/` 结果为 0 |
| ✅ 改密后其它设备掉线 | A 设备改密，B 设备下次操作应跳登录页 |

---

## 六、常见问题

| 现象 | 原因 / 解决 |
|---|---|
| `Cannot find module './common'` | 没跑 `npm run sync:shared`，或改完 `_shared` 后没重新上传云函数（[P40](./09-pitfalls.md)） |
| `Cloud API isn't enough initialized` | `cloud.init()` 写在 `require('./common')` 之后（[P41](./09-pitfalls.md)） |
| `AUTH_SECRET 未配置或过短` | 见 3.2，配完要**重新上传函数**才生效 |
| 登录一直转圈然后超时 | 云函数没部署，或 `env.js` 里的环境 ID 填错 |
| `component is not found` | 没在开发者工具里「构建 npm」（[P32](./09-pitfalls.md)） |
| 登录报「服务异常」 | 看云函数日志：控制台 → 云函数 → 日志，搜 `[auth]` |
| 忘了测试账号密码 | 调 `init-db` 的 `resetPassword`，见下 |

**重置测试账号密码**：

```json
{
  "action": "resetPassword",
  "payload": { "initKey": "你的 INIT_KEY", "username": "test1", "password": "NewPass123" }
}
```

---

## 七、上线前必做

> 详细清单见 [11-testing-release.md](./11-testing-release.md)，这里只列**部署相关**的。

- [ ] 🔴 删除 `init-db` 云函数（它能直接改任何账号的密码）
- [ ] 🔴 停用或改掉 `test1/test2/test3` 的默认密码（`Test1234` 是公开在文档里的）
- [ ] 🔴 确认 6 个集合权限全部为「仅管理端可读写」
- [ ] 🔴 `env.js` 里生产环境 ID 填的是 `plan-prod` 而不是 dev
- [ ] 索引全部建完（尤其 `idx_member_updated`、`idx_push_dedup`）
- [ ] `AUTH_SECRET` 生产环境用了与开发环境**不同**的值
- [ ] 提审备注里写好测试账号密码（[P37](./09-pitfalls.md)：最高频驳回原因）

---

*最后更新：M1-B 完成时*
