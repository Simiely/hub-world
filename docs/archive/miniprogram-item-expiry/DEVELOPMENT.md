---
module: archive
title: DEVELOPMENT.md
tags: [miniprogram-item-expiry]
source:
  project: miniprogram-item-expiry
  repo: https://github.com/Simiely/miniprogram-item-expiry
  file: DEVELOPMENT.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/miniprogram-item-expiry/blob/main/DEVELOPMENT.md)

# DEVELOPMENT.md —— 关键问题与方案参考

> 本文件记录本项目开发过程中的**关键约束、踩坑根因与解决方案**，供未来遇到类似小程序接入问题时快速查阅。
> 核心结论先行：**小程序只能跟「你自己备案的域名」通信**，这是所有外部数据接入方案的总约束。

---

## 一、小程序网络与域名硬约束（总纲）

小程序**没有 DOM、没有本地文件系统访问**，所有外部数据必须经 `wx.request` / `wx.downloadFile` 走网络拉取，且：

| 约束 | 说明 |
|---|---|
| HTTPS 强制 | 所有网络请求必须 HTTPS + 有效证书 |
| 域名白名单 | 请求域名必须在公众平台「服务器域名」配置（request / downloadFile / uploadFile 分开） |
| 备案主体一致 | 域名须国内已备案，且**备案主体须与小程序主体一致**（个人主体对应个人备案，企业对应企业） |
| 无 DOM | 不能 `innerHTML` / `document`，HTML 需解析库（towxml/marked）渲染 |
| 包体限制 | 主包 ≤ 2MB，大资源走远端按需拉或子包 |

> 本地开发可在「详情 → 本地设置」勾「不校验合法域名」临时绕过，但**上线必须配**。

---

## 二、版本与白名单差异（常见误解）

| 环境 | 域名白名单 | 访问局域网 http://192.168.x.x | 能否分享 |
|---|---|---|---|
| 开发者工具「模拟器」 | 勾"不校验"后免 | ✅（localhost=电脑） | 仅自己 |
| 开发者工具「真机调试」 | 勾"不校验"后免 | ✅（手机连同 WiFi，用 NAS 局域网 IP） | ❌ 不能分享，依赖工具 |
| **体验版** | ❌ 照常校验 | ❌ 不行 | ✅ 加体验者微信号 |
| 正式版 | ❌ 照常校验 | ❌ 不行 | ✅ 所有人 |

**关键误解纠正**：体验版 ≠ 免域名校验；开发版预览码能长期点开，是因为代码包已缓存到手机本地，与"能否联网"无关——只要它发 `wx.request`，白名单照样拦。**唯一能免白名单连局域网的是「真机调试」，但无法分享给他人。**

---

## 三、web-view 浏览网页

- `<web-view>` 相当于小程序内置浏览器，能渲染完整 H5。
- **仅企业主体可用**，个人主体无此权限。
- 需配置「业务域名」白名单（与 request 域名是两套名单），同样 HTTPS + 备案 + 主体一致 + 放校验文件到域名根。
- 只能嵌业务域名下的页面，不能当万能浏览器。

---

## 四、外部数据源接入可行性矩阵

| 数据源 | 小程序直读可行性 | 原因 |
|---|---|---|
| 对象存储 OSS/COS（自有备案域名） | ✅ | 直链 HTTPS，配白名单即可；OSS 默认域名是阿里云备案，也要绑自有备案域名 |
| 自建服务器 / 云函数 | ✅ | 最灵活，可做鉴权、格式转换 |
| **腾讯文档智能表 + 云开发中转** | ✅ | 走微信云开发通道免白名单，**天然规避备案域名门槛**（见第六节） |
| 个人网盘（百度/阿里/OneDrive） | ❌ | 需 OAuth 网页跳转，小程序无浏览器环境；无小程序 SDK |
| ddns.to / 第三方穿透域名 | ❌ | 第三方备案主体，配不进白名单；且常带访问验证 + Basic Auth 双重认证 |
| 局域网 NAS IP | ❌（仅真机调试） | 非 HTTPS、IP 不能配白名单 |

---

## 五、消息推送（订阅消息）

- 能力：`wx.requestSubscribeMessage`（前端请求授权）+ 服务端 `subscribeMessage.send`（推送）。
- 到达位置：微信「服务通知」（红点 + 震动，体验接近系统通知）。
- 约束：
  - **必须先用户主动授权**，不能无感静默推送（合规防骚扰）。
  - 一次性订阅：授权后 7 天内可下发一条；再推需再次授权（常见做法：用户设提醒时顺手请求）。
  - 长期订阅：仅政务/医疗/交通等特定类目。
- 本项目未接入提醒，如需"有效期到期提醒"可加订阅消息（用户首次进页面请求授权，到点推送）。

---

## 六、本项目（item-expiry）关键设计决策

### 6.1 为什么用云开发做主数据源

原始诉求是"读自己 NAS 里的 md 文件"，但 NAS 方案撞上「第三方域名 / 局域网 / 备案」三道墙。
改用**云开发数据库**做主数据源后：

- 小程序 `wx.cloud.database()` 读写走**微信官方通道，免 request 白名单**；
- 个人主体可用，零外部依赖，无需自有备案域名；
- 腾讯文档作为「家人协同视图」，通过云函数中转接入。

### 6.2 双向同步架构

- **正向（云库 → 腾讯文档）**：云开发**数据库触发器**监听 `items` 的 INSERT/UPDATE/REMOVE，近实时触发 `syncToDocs` 调腾讯文档 API。新增、修改、删除**都覆盖**。
- **反向（腾讯文档 → 云库）**：腾讯文档**无原生记录变更 webhook**，只能用 `syncFromDocs` 定时触发器（每 5 分钟）轮询 + 前端手动「同步」按钮。

### 6.3 防循环同步（最重要）

` 同步ToDocs`（云库→文档）写腾讯文档后，若 `syncFromDocs`（文档→云库）把这次变更又写回云库，云库一变又触发 `syncToDocs` → 死循环。

**方案**：`syncFromDocs` 回写云库时打标记 `_syncSource: 'docs'`；`syncToDocs` 检测到该标记即跳过。

```js
// syncFromDocs 写云库
const docData = { ...fields, _syncSource: 'docs' };

// syncToDocs 开头拦截
if (event.doc && event.doc._syncSource === 'docs') {
  return { skipped: true }; // 防循环
}
```

> 注：实际上 `syncToDocs` 写腾讯文档**不会**触发 `syncFromDocs`（无 webhook），所以严格说不会无限循环；但标记仍能避免 `syncFromDocs` 把"我们自己的同步写入"误判为家人改动而做无谓回写/冲突，建议保留。

### 6.4 Token 管理

- OAuth token 存云数据库 `tokens` 集合（`tencent_docs_token` 文档）。
- `getToken()` 在读到 token 时检查 `expireAt`，过期前 1 分钟自动用 `refresh_token` 刷新并写回。
- 需腾讯文档开放应用 `appId` / `secret`，以及**你自己备案的域名**作为 `redirect_uri`（OAuth 残留成本）。

### 6.5 recordId 映射

- 云库 `_id` 与腾讯文档 `recordId` 无天然关联，用 `mapping` 集合记录 `{ docId, recordId }`。
- 删除时靠 `mapping` 反查 `recordId` 去删腾讯文档对应记录（DELETE 事件 `event.doc` 可能为空，必须用 `event.docId` 查 mapping）。

### 6.6 触发器事件要点

- 云开发数据库触发器 `operations` 配置用 `INSERT / UPDATE / REMOVE`；运行时 `event.opType` 返回 `CREATE / UPDATE / DELETE`。
- CREATE 时字段在 `event.doc`，文档 ID 在 `event.docId`。
- REMOVE 时 `event.doc` 可能为空，务必用 `event.docId`。

### 6.7 反向同步的固有延迟

腾讯文档改了 → 最多 5 分钟（定时）或用户点「同步」才回写云库。若需"家人一改立刻可见"，目前只能缩短轮询间隔（注意腾讯文档 API 频率限制）或引导用户手动同步。

---

## 七、已知风险与待补强

| 风险 | 现状 | 建议 |
|---|---|---|
| 同步失败丢数据 | `syncToDocs` 调腾讯文档 API 可能因网络/token 失败 | 加失败重试 + 死信记录；加每日全量对账云函数兜底 |
| 冲突 | 两边同时改同一条记录 | 目前以「最后写入」为准；可加 `updatedAt` 时间戳冲突检测 |
| API 端点偏差 | 腾讯文档开放 API 端点/字段以官方文档为准，本项目为骨架 | 部署前到开放平台核对 `API_BASE` / `OAUTH_BASE` 及字段名 |
| 批量操作频控 | 一次批量增删会逐条触发云函数 | 注意腾讯文档 API 调用频率限制，大批量走全量对账 |
| 未接提醒 | 无到期提醒 | 可加订阅消息（见第五节） |

---

## 八、腾讯文档 API 端点核对清单（部署前必做）

> 本项目 `cloudfunctions/common/tdocs.js` 的端点为常见形态，请按官方最新文档核对：
> https://docs.qq.com/open/document/saas/

- [ ] OAuth 授权页 URL 与 token 端点（`OAUTH_BASE`）
- [ ] 智能表记录列表 / 新增 / 更新 / 删除端点（`API_BASE/smartdoc/v2/...`）
- [ ] 记录 ID 字段名（`recordId` vs `id`）
- [ ] 字段结构（`fields` 包裹 vs 平铺）
- [ ] 鉴权头格式（`Bearer` vs `token` 参数）
- [ ] fileId / sheetId 取值方式（文档 URL 解析）

---

## 九、复用清单（下次做类似小程序照此排查）

1. 数据源能不能进小程序？→ 先看「是不是你自己备案的域名」。
2. 不想备案？→ 优先云开发（免白名单）；或做 H5 局域网网页（零备案，但入口在浏览器）。
3. 要家人协同编辑？→ 腾讯文档智能表 + 云函数中转（OAuth 回调仍需备案域名）。
4. 要实时双向同步？→ 云库用触发器实时出，外部源无 webhook 就只能轮询入。
5. 防循环 → 回写打源标记。
6. token → 过期自动刷新 + 持久化。
7. 映射 → 外部记录 ID 与本地 ID 用映射表关联，删除时靠它定位。

---

## 十、syncFromDocs 变更检测优化（v1.1）

**问题**：原 `syncFromDocs` 每 5 分钟全量轮询，对每条记录无条件 `update`：

- 数据库**写次数** ≈ 记录数 × 288 次/天（30×24×12），轻松逼近「写 3 万/天」上限；
- 逐条 `where({recordId})` 把**读次数**推到「记录数 × 288/天」，逼近「读 5 万/天」上限。
- 撞线后超出的读写直接报错失败，同步中断。

**方案**：

1. **变更检测（省写）**：用字段指纹 `fp = [name, expireDate, count, category, note].join('|')` 存进 `mapping.fp`。同步时若 `mapping.fp === 当前指纹` 则 `skipped` 跳过写，**只有真正变化的记录才 `update`**。
2. **批量拉 mapping（省读）**：用 `db.command.in(recordIds)` 一次性（分批 100）拉全部 mapping，把每次同步的数据库读从「记录数」降到「几条」。

**效果（以 100 条物品为例）**：

| 指标 | 优化前 | 优化后 |
|---|---|---|
| 写次数/天 | ~28,800（逼近 3 万） | 仅变化记录（日常趋近 0） |
| 读次数/天 | ~28,800 | ~ceil(100/100)×288 ≈ 288 |

**注意**：

- 指纹比对是弱一致性（字段值相等即认为未变），适合本场景；若需严格版本，可改为比对腾讯文档记录的系统更新时间（需 API 暴露该字段）。
- `mapping` 结构由 `{ docId, recordId }` 扩展为 `{ docId, recordId, fp }`，升级后首次同步会对已有记录补全 `fp`（无 fp 视为需更新，正常写入一次）。
- 仍**未做「文档删除 → 本地删除」**检测（避免额外读开销与误删风险）；若需该能力，可遍历 mapping 反查 recordId 是否仍在本次拉取集合，再删本地。
