---
module: archive
title: 09-pitfalls.md
tags: [collab-plan-miniprogram]
source:
  project: collab-plan-miniprogram
  repo: https://github.com/Simiely/collab-plan-miniprogram
  file: docs/09-pitfalls.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/collab-plan-miniprogram/blob/main/docs/09-pitfalls.md)

# 09 · 踩坑记录库 ⚠️

> 上级导航：[README 总导航](./README.md)
> **这是一份活文档。** 任何调试超过 30 分钟的问题，解决后必须记录到这里。

---

## 记录格式

```markdown
### [编号] 一句话描述现象

- **现象**：具体报错信息 / 异常表现
- **原因**：根本原因
- **解决**：怎么改的（贴关键代码）
- **预防**：如何避免再犯
- **相关**：涉及文件 / 相关文档链接
```

---

## 索引

| 分类 | 编号 | 严重度 |
|---|---|---|
| [云开发与数据库](#一云开发与数据库) | P01 - P07 | 🔴🔴🔴🟡🔴🟡🟡 |
| [数据同步](#二数据同步) | P08 - P13, P51 | 🔴🔴🔴🟡🟡🟡🔴 |
| [订阅消息与定时器](#三订阅消息与定时器) | P14 - P20 | 🔴🔴🔴🔴🟡🟡🟡 |
| [账号与登录](#四账号与登录) | P21 - P24 | 🔴🔴🟡🟡 |
| [小程序框架](#五小程序框架通用) | P25 - P32 | 🟡🟡🔴🟡🟡🟡🟡🟡 |
| [性能与包体积](#六性能与包体积) | P33 - P36 | 🟡🟡🟡🟡 |
| [审核与发布](#七审核与发布) | P37 - P39 | 🔴🔴🟡 |
| [云函数工程化](#八云函数工程化) | P40 - P46 | 🔴🔴🔴🔴🟡🟡🟡 |
| [计划业务与组件](#九计划业务与组件) | P47 - P50 | 🔴🔴🟡🟡 |

🔴 = 会导致数据错误/安全问题/上不了线　🟡 = 影响体验/开发效率

---

## 一、云开发与数据库

### 🔴 P01 前端能直接读到数据库里的密码哈希

- **现象**：在开发者工具 console 里执行 `wx.cloud.database().collection('users').get()`，返回了全部用户数据，含 `passwordHash` 和 `salt`
- **原因**：集合权限默认是「仅创建者可读写」或「所有人可读」。本项目用自建账号体系，`_openid` 与业务身份无关，这个默认权限形同虚设
- **解决**：所有集合权限改为 **「仅管理端可读写」**（云控制台 → 数据库 → 集合 → 权限设置）
- **预防**：新建任何集合后，**第一件事**就是改权限。上线检查清单里必查
- **相关**：[03-data-model.md](./03-data-model.md) 安全红线章节

### 🔴 P02 前端传 userId 导致越权

- **现象**：抓包改一下 `userId` 参数，就能完成/删除别人的计划
- **原因**：云函数里写了 `const userId = event.userId`
- **解决**：`const userId = await authGuard(event.token)`，从 Token 解出
- **预防**：全局搜索 `event.userId`，应为 0 个结果。加到 code review checklist
- **相关**：[06-auth-design.md](./06-auth-design.md)

### 🔴 P03 `update` 传 `undefined` 字段不生效

- **现象**：想清空 `remindAt`，写了 `update({ data: { remindAt: undefined } })`，执行成功但字段值没变
- **原因**：云数据库序列化时会**忽略** `undefined` 字段，不是把它设为空
- **解决**：
  ```js
  // 清空字段用 null
  update({ data: { remindAt: null } })
  // 或彻底删除字段
  update({ data: { remindAt: _.remove() } })
  ```
- **预防**：约定所有"空值"一律用 `null`，代码里禁止出现 `undefined` 赋值
- **相关**：[03-data-model.md](./03-data-model.md) 字段约定

### 🟡 P04 单次查询最多返回 100 条

- **现象**：明明有 300 条数据，`.get()` 只返回 100 条，且不报错
- **原因**：云函数中 `limit` 上限是 100（小程序端是 20）
- **解决**：分页循环，或用 `.count()` 先拿总数再循环拉取
  ```js
  const PAGE = 100;
  let all = [], offset = 0;
  while (true) {
    const r = await coll.skip(offset).limit(PAGE).get();
    all = all.concat(r.data);
    if (r.data.length < PAGE) break;
    offset += PAGE;
  }
  ```
- **预防**：任何 `.get()` 前先想"数据量会不会超 100"

### 🔴 P05 云函数时区是 UTC，时间显示全错 8 小时

- **现象**：订阅消息里显示的提醒时间比实际早 8 小时；日志时间对不上
- **原因**：云函数运行环境时区是 **UTC**，`new Date().getHours()` 返回 UTC 小时
- **解决**：所有面向用户的时间格式化显式加 8 小时
  ```js
  const d = new Date(ts + 8 * 3600 * 1000);
  d.getUTCHours();   // 这才是北京时间的小时
  ```
- **预防**：云函数里**禁止**使用 `getHours()/getDate()/getMonth()` 等本地时间方法，只用 `getUTC*` 系列 + 手动偏移。封装成 `common/time.js` 统一调用
- **相关**：[05-reminder-design.md](./05-reminder-design.md)

### 🟡 P06 云函数改了代码没生效

- **现象**：明明改了云函数代码，调用行为还是老的
- **原因**：忘记**上传部署**。本地修改不会自动同步到云端
- **解决**：右键云函数目录 → 「上传并部署：云端安装依赖」
- **预防**：改完云函数养成立即上传的习惯；调试时在返回值里带一个 `version` 字段确认是否为最新代码

### 🟡 P07 云函数 npm 依赖装不上

- **现象**：上传后调用报 `Cannot find module 'xxx'`
- **原因**：选了「上传并部署：所有文件」而不是「云端安装依赖」；或 `package.json` 没写依赖
- **解决**：确保云函数目录有 `package.json` 且列了依赖，用「云端安装依赖」方式上传
- **预防**：本项目尽量只用 Node 内置模块（`crypto` 等），减少依赖，避免这类问题

---

## 二、数据同步

### 🔴 P08 用手机时间做水位线导致数据永久丢失

- **现象**：部分用户反馈"别人创建的计划我看不到"，但重装小程序后就正常了
- **原因**：`lastSyncAt = Date.now()` 用了手机本地时间。用户手机时间快了几分钟，导致这段时间内服务器的新数据被永久跳过
- **解决**：水位线只用云函数返回的 `serverTime`
- **预防**：`sync/` 目录下全局搜索 `Date.now()`，确认没有用于水位线计算
- **相关**：[04-sync-design.md](./04-sync-design.md) 铁律 1

### 🔴 P09 硬删除导致本地残留幽灵数据

- **现象**：A 删除了计划，B 的手机上一直还能看到，点进去报"计划不存在"
- **原因**：用了 `.remove()` 物理删除。增量同步只能拉到"变更的记录"，被删掉的记录查不到，客户端无从得知
- **解决**：改为软删除 `{ deleted: true, updatedAt: Date.now() }`，客户端同步到 `deleted:true` 时从本地移除
- **预防**：全局禁用 `.remove()`。在 `common/db.js` 里不导出 remove 方法
- **相关**：[04-sync-design.md](./04-sync-design.md) 铁律 2

### 🔴 P10 分页中途失败但水位线已推进，丢一整页数据

- **现象**：偶发性数据缺失，且缺失的是连续的一批
- **原因**：分页拉取时，每页都更新了 `lastSyncAt`。第 2 页失败后，水位线已经推到第 1 页末尾，重试时从第 2 页开始，但第 2 页的数据 `updatedAt` 小于水位线，永远拉不到
- **解决**：`serverTime` **只在最后一页返回**，中间页返回 `null`；客户端只有拿到非 null 的 serverTime 才更新水位线
  ```js
  serverTime: hasMore ? null : Date.now()
  ```
- **预防**：把"水位线推进"这个动作放在整个同步流程的**最后一步**，且只有全部成功才执行

### 🟡 P11 离线创建的计划变成两条

- **现象**：断网创建一条计划，联网后列表出现两条一模一样的
- **原因**：重放队列时网络超时重试，云函数每次都 `add()` 插入新记录
- **解决**：客户端生成 `planId`，云函数按 `planId` 做幂等 upsert
  ```js
  const exist = await coll.where({ planId }).count();
  if (exist.total > 0) return ok({ duplicated: true });  // 幂等返回
  await coll.add({ data: {...} });
  ```
- **预防**：所有写操作都要有幂等键

### 🟡 P12 本地存储超限

- **现象**：`setStorageSync` 报错 `exceed storage max size`
- **原因**：小程序单 key 上限 1MB，总容量 10MB。计划数超过约 2500 条时触发
- **解决**：
  - 短期：只缓存近 3 个月 + 未完成的计划
  - 长期：分片存储 `plans_0` / `plans_1`，每片 1000 条
- **预防**：`core/storage.js` 里 set 时捕获异常并降级；「我的」页调试面板显示当前缓存条数

### 🟡 P13 每个页面 onShow 都同步，接口被打爆

- **现象**：用户在列表和详情间来回切，云函数调用量暴涨
- **原因**：在多个页面的 `onShow` 里都调了 `syncAll()`
- **解决**：统一在 App 级别 `onShow` 触发，且用 `syncIfNeeded()`（距上次 > 60s 才同步）；页面只从 store 读数据
- **预防**：同步入口收敛到一处，页面不允许直接调 `syncAll`

### 🔴 P51 同步分页同毫秒批量死锁 / 错位（复合游标）

- **现象**：某用户有 100+ 条计划且 `updatedAt` 落在同一毫秒（如批量导入），增量同步**永远拉不完**（游标卡死），或偶发「漏几条 / 重复几条」
- **原因**：两层叠加
  1. **错位**：`orderBy('updatedAt','asc')` 在**同毫秒内没有稳定次级排序键**。用 `skip` 分页时（`where({updatedAt: _.gte(since)}).skip(n).limit(100)`），同一毫秒的记录每次重排顺序不同，第 2 页可能和已读页重叠或漏读
  2. **卡死**：续页若沿用 `since<=0` 的全量查询（`where({memberIds, deleted:false})`），因为所有记录的 `updatedAt` 都等于 `since`，游标用 `_.gte(since)` 永远命中全部 → 每页都满 → `hasMore` 永远 true → 无限循环
- **解决**（见 [cloudfunctions/sync/index.js](./cloudfunctions/sync/index.js) 与 [04-sync-design.md](./04-sync-design.md) 四）：
  1. **复合游标替代 skip**：续页条件用 `(updatedAt, _id)` 严格续接，`_id` 是文档主键、全局唯一，作为同毫秒内的稳定次级排序键：
     ```js
     where(_.and([
       { memberIds: userId },
       _.or([
         { updatedAt: _.gt(cursor.updatedAt) },
         _.and([ { updatedAt: _.eq(cursor.updatedAt) }, { _id: _.gt(cursor._id) } ]),
       ]),
     ]))
     ```
  2. **续页优先级高于 `since`**：一次同步里 `since`（水位线）是固定不变的，翻页只靠 `cursor` 推进。若 `cursor` 存在，绝不退回 `since<=0` 的全量分支（否则如上第 2 点卡死）
  3. `orderBy('updatedAt','asc').orderBy('_id','asc')` 保证服务端排序与游标比较语义一致
- **预防**：
  - 回归用例 `cloud-sync.test.js`「同毫秒批量 250 条」故意构造全同毫秒数据，断言**正好 3 页（100+100+50）、无重复、不卡死**；并把该 bug 改回（续页忽略 cursor）确认用例变红，证明测试有效
  - 真机走查（M6）：造 300 条数据验证分页完整
- **相关**：[04-sync-design.md](./04-sync-design.md) 铁律 3（安全窗口）/ 四（游标分页）、[cloudfunctions/sync/index.js](./cloudfunctions/sync/index.js)

---

## 三、订阅消息与定时器

### 🔴 P14 Cron 表达式写成 5 位，定时器不触发

- **现象**：定时触发器配了但从不执行，控制台也没有明显报错
- **原因**：云开发 cron 是 **7 位**（秒 分 时 日 月 周 年），标准 Linux cron 是 5 位
- **解决**：
  ```json
  "config": "0 * * * * * *"    // ✅ 每分钟，7位
  // "config": "* * * * *"      ❌ 5位，无效
  ```
- **预防**：配完后在云控制台「定时触发器」页确认状态为"已启用"，并观察下一次执行时间
- **相关**：[05-reminder-design.md](./05-reminder-design.md)

### 🔴 P15 同一条提醒推送多次

- **现象**：用户收到 2-3 条一模一样的提醒
- **原因**：定时触发器不保证只执行一次（网络抖动、实例重启会重复触发），没有幂等保护
- **解决**：三层去重
  1. 抢锁：`where({ remindStatus: 'pending' }).update({ remindStatus: 'sending' })`，`stats.updated === 0` 就跳过
  2. `push_logs` 的 `planId + openid` 建**唯一索引**
  3. 推送前查 `push_logs` 是否已有记录
- **预防**：任何定时任务都必须假设"会被重复执行"来设计

### 🔴 P16 推送报 47003 参数不符合规则

- **现象**：`subscribeMessage.send` 报 `errCode: 47003`
- **原因**（按出现频率排序）：
  1. `thing` 类型字段**超过 20 个字符**
  2. 字段值为**空字符串**
  3. `time` 类型格式不对
  4. 含换行符、表情符号
- **解决**：所有字段过统一的格式化函数
  ```js
  function toThing(s, max = 20) {
    const v = String(s || '').replace(/[\r\n\t]/g, ' ').trim();
    if (!v) return '无';
    return v.length > max ? v.slice(0, max - 1) + '…' : v;
  }
  ```
- **预防**：模板字段的赋值**只能**通过格式化函数，禁止直接传原始值

### 🔴 P17 推送报 41030 page 路径不正确

- **现象**：开发阶段测试推送一直报 41030
- **原因**：`page` 指向的页面必须存在于**已发布的线上版本**中。开发版页面还没上线
- **解决**：开发期把 `miniprogramState` 设为 `'developer'`
  ```js
  miniprogramState: process.env.NODE_ENV === 'production' ? 'formal' : 'developer'
  ```
- **预防**：把 `miniprogramState` 做成环境变量，不要硬编码 `'formal'`

### 🟡 P18 requestSubscribeMessage 静默失败

- **现象**：点按钮没弹订阅授权窗，也没报错
- **原因**：调用前有 `await`，手势上下文丢失
  ```js
  async onTap() {
    await this.save();              // ❌ 这里之后就不是手势上下文了
    await requestSubscribe();       // 静默失败
  }
  ```
- **解决**：`requestSubscribeMessage` 必须是 tap 回调里的**第一个**异步调用
- **预防**：约定所有订阅授权都封装在 `remind.service.requestSubscribe()`，且在页面里第一行调用

### 🟡 P19 查不到用户还剩几次订阅额度

- **现象**：`wx.getSetting({ withSubscriptions: true })` 返回的 `subscriptionsSetting` 是空的
- **原因**：只有用户勾选了「总是保持以上选择」才能查到；没勾选时查不到
- **解决**：自建 `subscribe_quota` 集合记账，不依赖微信接口
- **预防**：从设计阶段就假设"微信不告诉你额度"

### 🟡 P20 用户退出登录后仍收到提醒

- **现象**：账号 A 退出登录了，还是收到 A 的计划提醒
- **原因**：退出时只清了本地 session，没有解绑 `user_bindings` 里的 openid
- **解决**：`auth.logout` 云函数里把 `(userId, openid)` 绑定置 `active: false`
- **预防**：登录/登出必须成对处理绑定关系

---

## 四、账号与登录

### 🔴 P21 换账号登录后显示上个账号的数据

- **现象**：用账号 A 登录看到 A 的计划，退出后用 B 登录，列表里还是 A 的计划
- **原因**：登录成功后没清本地业务缓存，`lastSyncAt` 也没重置
- **解决**：
  ```js
  storage.clearBusinessData();   // 清 plans / opQueue
  storage.set('lastSyncAt', 0);  // 重置水位线 → 触发全量同步
  ```
- **预防**：测试用例**必须包含**「切换账号」场景。单账号测试发现不了这个 bug

### 🔴 P22 scrypt 参数过大导致云函数超时/OOM

- **现象**：登录接口报超时，或 `memory limit exceeded`
- **原因**：`scryptSync` 的 N 参数设为 1048576，内存消耗约 1GB
- **解决**：`N=16384, r=8, p=1`（约 100ms、16MB），云函数内存配 256MB 以上
- **预防**：本地先跑一次 benchmark 确认耗时和内存

### 🟡 P23 在 app.onLaunch 里 wx.redirectTo 无效

- **现象**：未登录时想跳登录页，`onLaunch` 里调 `redirectTo` 没反应
- **原因**：`onLaunch` 执行时页面栈还没建立
- **解决**：在首个页面的 `onShow` 里判断并 `wx.reLaunch`
- **预防**：登录守卫统一写在首个 tab 页的 `onShow`，不放 app 层

### 🟡 P24 tabBar 页面用 navigateTo 跳转失败

- **现象**：`wx.navigateTo({ url: '/pages/todo/todo' })` 报错
- **原因**：tabBar 页面只能用 `wx.switchTab`
- **解决**：跳 tab 页用 `switchTab`；需要传参时用全局变量或 `event-bus` 传递（switchTab 不支持 query）
- **预防**：封装 `utils/router.js`，内部自动判断目标是否为 tab 页

---

## 五、小程序框架通用

### 🟡 P25 setData 大对象导致列表卡顿

- **现象**：列表滑动掉帧，切换 tab 有明显延迟
- **原因**：把完整的计划对象（含 desc 长文本、memberIds 等）全部 setData 进视图
- **解决**：只 setData 视图用得到的字段；完整数据挂 `this._rawPlans`
- **预防**：`setData` 前问一句"视图真的需要这个字段吗"

### 🟡 P26 列表更新整个数组，性能差

- **现象**：点一下完成，整个列表重新渲染
- **解决**：用路径更新
  ```js
  this.setData({ [`list[${index}].status`]: 'done' });
  ```
- **预防**：单项变更一律用路径更新

### 🔴 P27 数组字段查询用错语法

- **现象**：`where({ memberIds: userId })` 查不到数据，或返回全部
- **原因**：混淆了"数组包含"和"数组相等"。云数据库里 `where({ memberIds: 'u_1' })` 表示**数组包含** `'u_1'`，这是对的；但如果写成 `where({ memberIds: ['u_1'] })` 就变成"数组完全等于 `['u_1']`"
- **解决**：包含查询用 `where({ memberIds: userId })`（传标量）
- **预防**：写完数组查询立刻在云控制台数据库里手动验证一次

### 🟡 P28 自定义组件的 properties 用了对象默认值

- **现象**：多个组件实例共享了同一个对象，改一个全变
- **原因**：`properties: { data: { type: Object, value: {} } }` 的 value 是引用共享的
- **解决**：在 `attached` 里初始化，或每次传新对象
- **预防**：组件 properties 的对象/数组默认值统一设为 `null`，在组件内部做兜底

### 🟡 P29 页面 onShow 重复注册监听导致内存泄漏

- **现象**：来回切页面后，一次操作触发多次回调
- **原因**：`onShow` 里 `eventBus.on(...)` 但 `onHide` 没 `off`
- **解决**：成对注册/注销
- **预防**：封装 `core/event-bus.js` 时提供 `onceScoped(page, event, fn)` 自动在页面卸载时清理

### 🟡 P30 wx API 回调地狱

- **现象**：嵌套 5 层回调，无法维护
- **解决**：统一 Promise 化
  ```js
  // utils/promisify.js
  const promisify = fn => (opts = {}) =>
    new Promise((resolve, reject) =>
      fn({ ...opts, success: resolve, fail: reject }));
  ```
- **预防**：`core/` 层把用到的 wx API 都包一层，业务代码只见 Promise

### 🟡 P31 真机与开发者工具行为不一致

- **现象**：工具里正常，真机白屏/报错
- **常见原因**：
  - 开发者工具不校验域名白名单，真机会
  - 工具的 storage 容量比真机大
  - 订阅消息、支付等能力在工具里是模拟的
  - iOS 对 `new Date('2026-07-31 19:03')` 解析失败（必须用 `/` 或 ISO 格式）
- **解决**：iOS 日期解析用 `'2026/07/31 19:03'` 或时间戳
- **预防**：**每个迭代都真机测**，不要只依赖开发者工具

### 🟡 P32 使用 TDesign 组件报 "component is not found"

- **现象**：页面报组件未找到
- **原因**：
  1. 没执行「工具 → 构建 npm」
  2. `project.config.json` 里 `packNpmManually` / `packNpmRelationList` 配置不对
  3. `usingComponents` 路径写错
- **解决**：`npm install` → 开发者工具「构建 npm」→ 检查生成的 `miniprogram_npm` 目录
- **预防**：每次新增 npm 依赖后都要重新构建 npm

---

## 六、性能与包体积

### 🟡 P33 主包超过 2MB 无法预览

- **现象**：上传时提示"主包大小超过 2M"
- **解决**：
  1. 把低频页面移到分包
  2. 图片传云存储或用 CDN
  3. TDesign 按需引入，不全局注册
  4. 开发者工具「代码依赖分析」找出大文件
- **预防**：主包预算控制在 1.2MB，留出缓冲

### 🟡 P34 冷启动慢

- **原因**：`onLaunch` 里做了网络请求或大量同步 IO
- **解决**：`onLaunch` 只做 `cloud.init` + 读 session（同步、快）；同步动作异步触发
- **预防**：`onLaunch` 里禁止出现 `await`

### 🟡 P35 云函数冷启动导致首次请求慢 2-3 秒

- **现象**：一段时间没用后，第一次操作明显卡顿
- **原因**：云函数实例被回收，冷启动需要重新加载
- **解决**：
  - 合并云函数（用 `action` 路由），减少函数数量 → 提高单个函数的调用频率 → 降低冷启动概率
  - 定时触发器本身会保活 `remind-scan`
  - 关键路径可考虑云函数预热（付费能力）
- **预防**：本项目已采用 `action` 路由模式合并函数

### 🟡 P36 首屏白屏等网络

- **解决**：本地缓存优先渲染，网络数据回来后静默更新
- **预防**：任何列表页都遵循「先本地后网络」

---

## 七、审核与发布

### 🔴 P37 因为没提供测试账号被驳回

- **现象**：提审后被拒，理由是"无法完整体验小程序功能"
- **原因**：小程序打开就是登录页，审核员没有账号进不去
- **解决**：提审时在「审核备注」里写清楚测试账号密码
  ```
  测试账号：test001
  密码：Test123456
  说明：本小程序为组织内部协作工具，账号由管理员统一分配，不开放注册。
  ```
- **预防**：提审前检查测试账号是否可用、是否有预置数据

### 🔴 P38 隐私协议未配置被驳回

- **现象**：审核提示"未按要求配置用户隐私保护指引"
- **解决**：小程序后台 →「设置」→「服务内容声明」→「用户隐私保护指引」，声明收集的信息（本项目：账号信息、设备信息用于消息推送）
- **预防**：这是所有小程序的硬性要求，第一次提审前就配好

### 🟡 P39 体验版收不到订阅消息

- **现象**：正式版能收到，体验版收不到
- **原因**：`miniprogramState` 设成了 `'formal'`，但当前是体验版
- **解决**：根据 `envVersion` 动态设置 `developer` / `trial` / `formal`
- **预防**：见 P17

---

## 八、云函数工程化

> P40 - P46 是 **M1 阶段真实踩到并已修复** 的坑，不是预判。
> 每条都附了本仓库里的对应代码位置，改代码前先看一眼。

### 🔴 P40 云函数 require 不到上级目录的公共代码

- **现象**：本地写 `require('../_shared/db')` 一切正常，上传后云端报
  `Cannot find module '../_shared/db'`
- **原因**：云函数是**独立打包**的，上传时只会打包该函数自己的目录，
  目录外的文件（哪怕在同一个仓库里）根本不会被带上去
- **解决**：公共代码放 `cloudfunctions/_shared/`，用脚本物理复制到每个函数的 `common/`：
  ```bash
  npm run sync:shared        # scripts/sync-shared.js
  ```
  函数里统一写 `require('./common')`，并把 `cloudfunctions/*/common/` 加进 `.gitignore`
- **预防**：🔴 **改完 `_shared` 必须重跑 `npm run sync:shared` 再上传**，
  否则改动不会生效，而且现象是"代码明明改了却没用"，极难排查。
  建议把它挂到 `postinstall` 与上传前的固定动作里
- **相关**：`cloudfunctions/_shared/index.js`、`scripts/sync-shared.js`

### 🔴 P41 云函数冷启动报 "Cloud API isn't enough initialized"

- **现象**：本地调试正常，云端偶发（冷启动时必现）报此错，函数直接 500
- **原因**：公共层 `db.js` 顶层就执行了 `cloud.database()`，
  而 `index.js` 里 `require('./common')` 写在 `cloud.init()` **之前**——
  CommonJS 是顺序执行的，require 那一行先跑，此时 SDK 还没初始化
  ```js
  const { coll } = require('./common');   // ❌ 这一行就炸了
  cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
  ```
- **解决**：两层保险
  1. `index.js` 里 `cloud.init()` 永远写在 `require('./common')` 之前
  2. `_shared/db.js` 里做一次幂等兜底初始化（谁先执行谁生效）
- **预防**：新建云函数时直接复制 `cloudfunctions/auth/index.js` 的头部三行
- **相关**：`cloudfunctions/_shared/db.js`

### 🔴 P42 改完密码，旧设备的 Token 还能继续用 30 天

- **现象**：怀疑密码泄露 → 改密 → 攻击者手里的 Token 照样能拉取全部计划
- **原因**：Token 是自包含的（无状态），签发后服务端不再校验密码，
  改密只影响"下次登录"，对已签发的 Token 毫无约束
- **解决**：给 `users` 加 `pwdChangedAt`，鉴权时比对 Token 的签发时间
  ```js
  // cloudfunctions/_shared/auth-guard.js
  if (user.pwdChangedAt && payload.iat < user.pwdChangedAt) {
    throw new BizError(CODE.UNAUTHORIZED, 'PASSWORD_CHANGED');
  }
  ```
  改密的那台设备要**当场换发新 Token**，否则自己也会被自己踢下线
- **预防**：任何"无状态 Token"方案都必须配一个失效判据（版本号或时间戳），
  否则"改密码"这个动作在安全上是无效的
- **相关**：`cloudfunctions/_shared/auth-guard.js`、`cloudfunctions/auth/index.js`

### 🔴 P43 索引忘了建，数据量涨上来后同步接口突然变慢

- **现象**：测试阶段几十条数据飞快，上线两周后拉取列表要 3-5 秒甚至超时
- **原因**：云开发的 Node SDK **没有创建索引的接口**，
  `init-db` 只能建集合不能建索引，很容易以为"初始化脚本跑完就齐活了"
- **解决**：索引只能在「云开发控制台 → 数据库 → 索引管理」手动创建。
  `init-db` 的返回值里带了完整的 `indexChecklist`，照着点即可
- **预防**：把建索引写进部署清单并逐项打勾，
  尤其是 `plans` 的 `memberIds + updatedAt`（增量同步主查询，缺了必卡）
- **相关**：[12-deploy-guide.md](./12-deploy-guide.md) 第四步、`cloudfunctions/init-db/index.js`

### 🟡 P44 用「时间窗」防重复跳转，把合法跳转也吞掉了

- **现象**：退出登录时网络失败，会话已清空，人却还停在原页面，
  看到的是上一个账号的残留数据
- **原因**：`redirectToLogin()` 里写了"跳转后 1 秒内不再跳"，
  这 1 秒窗口内任何**合法**跳转请求都会被静默丢弃
  ```js
  if (redirecting) return;
  redirecting = true;
  wx.reLaunch({ url, complete: () => setTimeout(() => { redirecting = false; }, 1000) });
  ```
- **解决**：去重判据换成"是否已经在登录页"——精确、自愈、不依赖时间
  ```js
  if (redirecting) return;          // 只挡同一帧内的并发
  if (isOnLoginPage()) return;      // getCurrentPages() 判断
  ```
- **预防**：凡是"用 setTimeout 做状态抑制"的地方都要问一句：
  窗口内到来的合法请求被丢了会怎样？
- **相关**：`miniprogram/core/session.js`

### 🟡 P45 预包装 wx API 时直接传函数引用，丢失 this 绑定

- **现象**：`promisify(wx.getSetting)` 在部分基础库版本上调用时报
  `Cannot read property 'xxx' of undefined`；
  低版本基础库上还可能在**模块加载期**就崩溃
- **原因**：`wx.getSetting` 作为值传出去后 `this` 不再是 `wx`；
  而且 `promisify(wx.xxx)` 写在模块顶层，加载时就读取了该属性，
  API 不存在时直接抛错，整个模块加载失败
- **解决**：包一层箭头函数，把读取推迟到调用时
  ```js
  getSetting: promisifySafe((o) => wx.getSetting(o)),
  ```
- **预防**：任何"把宿主对象的方法当值传递"的写法都要警惕
- **相关**：`miniprogram/utils/promisify.js`

### 🟡 P46 登录接口的响应时间泄露了账号是否存在

- **现象**：错误文案已经统一成"账号或密码错误"了，
  但账号不存在时 5ms 返回、账号存在密码错时 75ms 返回
- **原因**：账号不存在就直接 return 了，没走 scrypt；
  攻击者用响应耗时就能批量筛出真实账号，等于文案脱敏白做
- **解决**：账号不存在时也跑一次等价耗时的哈希运算
  ```js
  if (!user) {
    pwd.hashPassword(password, DUMMY_SALT);   // 拉平耗时
    throw new BizError(CODE.WRONG_CREDENTIAL, '账号或密码错误');
  }
  ```
- **预防**：安全相关的分支，除了"返回什么"一致，还要检查"用多久"一致；
  同理，也不要返回"还剩几次尝试机会"（同样泄露账号存在性）
- **相关**：`cloudfunctions/auth/index.js`

---

## 九、计划业务与组件

### 🔴 P47 `doc(id).get()` 返回对象不是数组，且取不到时**抛异常**不是返回空

> 这是 M2 阶段唯一一个真·线上级 bug，而且**一度被测试判定为"通过"**，值得完整记一笔。

- **现象**：分两次暴露
  1. 一开始 `plan.detail` 一律返回 `USER_DISABLED（账号已被禁用）`——
     但账号明明正常，`auth.login` 刚成功过，报错完全指错方向
  2. 改完之后单测全绿，但把 Mock 改成贴近真实 SDK 后立刻红了一片：
     所有针对"计划不存在"的用例返回的是 `5000 系统繁忙`，而不是 `4001 计划不存在`
- **原因**：**三个问题叠在一起**，每一个单独看都不致命
  1. 云数据库两种查询的返回结构**不一样**，极易记混：
     ```js
     await db.collection('plans').where({ planId }).get()  // → { data: [ {...} ] }  数组
     await db.collection('plans').doc(planId).get()        // → { data: {...} }      对象！
     ```
     代码写成 `res.data[0]`，对象取下标恒为 `undefined`
  2. **更隐蔽的一条**：`doc().get()` 取不到记录时**默认抛异常**，不是返回空。
     官方文档写得很清楚，只是没人会专门去翻：
     > `throwOnNotFound`：在调用获取记录（doc.get）时，如果获取不到，是否抛出异常，
     > 如果不抛出异常，doc.get 返回空。**默认 true**。
     >  —— [Cloud.database 文档](https://developers.weixin.qq.com/miniprogram/dev/wxcloudservice/wxcloud/reference-sdk-api/Cloud.database.html)

     所以 `if (!plan) throw new BizError(PLAN_NOT_FOUND)` 这行**永远执行不到**，
     异常先一步冒到 `createHandler` 的兜底里，变成 `INTERNAL_ERROR`。
     用户看到的是"系统繁忙"，一个本该说清楚的业务提示被吞成了系统故障
  3. 上游守卫也中招：`authGuard` 里 `try/catch` 把**任何**异常都转成了 `USER_NOT_FOUND`，
     底层的取值 bug 被伪装成账号问题
- **解决**：三层一起改
  ```js
  // ① 全局关掉：init 和 database() 两处都传，避免「谁先调 init」的顺序问题
  cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV, throwOnNotFound: false });
  const db = cloud.database({ throwOnNotFound: false });

  // ② 统一收口成一个函数，业务层禁止再裸写 doc().get()
  async function getDocById(collName, id) {
    if (!id) return null;
    try {
      const res = await coll(collName).doc(id).get();
      return (res && res.data) || null;
    } catch (e) {
      if (isDocNotFound(e)) return null;   // 只吞「记录不存在」
      throw e;                             // 🔴 真实故障必须继续上抛
    }
  }
  ```
  ```js
  // ③ 守卫不再 catch-all
  const user = await getDocById(COLL.USERS, userId);
  if (!user) throw new BizError(CODE.UNAUTHORIZED, 'USER_NOT_FOUND');
  ```
- **预防**：
  - 记死：**`where().get()` 给数组、`doc().get()` 给对象，且取不到会抛**
  - `catch` 里**绝不能无差别吞异常**。原来那句 `catch { throw USER_NOT_FOUND }`
    意味着数据库一抖动，用户就被告知"账号不存在"——真实事故被静默掩盖
  - 🔴 **Mock 必须严格复刻真实 SDK，宁可更严格。**
    这个 bug 最初逃过测试，就是因为自己写的 Mock 也返回数组、也不抛异常。
    **比没有测试更危险的是提供虚假安全感的测试**
  - 回归用例写完，**故意把修复改回去跑一遍**，确认它真的会红（本例已验证：会红 6 条）
- **相关**：`cloudfunctions/_shared/db.js`（`getDocById`）、`cloudfunctions/_shared/auth-guard.js`、
  `cloudfunctions/plan/index.js`、回归用例 `tests/cloud-plan.test.js` §12 与 `tests/shared.test.js`

### 🔴 P48 改了提醒时间，到点却没推送（remindStatus 状态机漏维护）

- **现象**：创建计划时设了提醒，后来把提醒时间改到更晚，结果到点没收到；
  或者取消提醒后仍然收到了一条
- **原因**：`remindAt` 和 `remindStatus` 是**一对**，`update` 时只改了前者。
  定时器是按 `remindStatus === 'pending'` 抢锁的（[P15](#-p15-同一条提醒推送多次)），
  一旦状态已经是 `sent` / `skipped`，改时间也不会被重新扫描到
- **解决**：把它当**状态机**维护，`update` 里按四种情况显式处理：
  ```js
  // 无 → 有：置 pending；有 → 无：置 none 并清空 remindAt
  // 时间改了：无条件重置回 pending（哪怕之前已 sent）
  // 时间没改：保持原状态不动
  patch.remindStatus = deriveRemindStatus(nextRemindAt, plan.remindAt, plan.remindStatus);
  ```
  同理，计划被 `complete` / `remove` 时要把 `remindStatus` 打成 `skipped`
- **预防**：凡是"业务字段 + 配套状态字段"的组合，**只能有一个函数能改它们**
  （这里是 `deriveRemindStatus`），禁止在各处零散赋值。
  写完在 roadmap 的 M4 验收里加一条"改时间后仍能收到"的回归用例
- **相关**：`cloudfunctions/plan/index.js`、[05-reminder-design.md](./05-reminder-design.md)

### 🟡 P49 组件在 wxml 里用了，但忘了在 json 里声明，页面静默少一块

- **现象**：`plan-detail` 页面的空状态区域什么都不显示，不报错、不白屏，
  就是那一块**凭空消失**了；控制台只有一行容易被忽略的 warning
- **原因**：`plan-detail.wxml` 写了 `<empty-state />`，但 `plan-detail.json` 的
  `usingComponents` 里没登记。未声明的标签会被当成**未知标签直接跳过渲染**
- **解决**：每个页面 json 补齐声明
  ```json
  { "usingComponents": { "empty-state": "/components/empty-state/index" } }
  ```
- **预防**：
  - 新增组件引用时，养成 **wxml 和 json 同一次改动里一起写**的习惯
  - 路径一律用**绝对路径**（`/components/...`），分包页面用相对路径极易写错
  - 页面"少了一块但不报错"，第一反应就是查 `usingComponents`
- **相关**：`miniprogram/pages/plan-detail/plan-detail.json`，与 [P32](#-p32-使用-tdesign-组件报-component-is-not-found) 同源

### 🟡 P50 点完成后卡片"跳"到列表中间，排序前后端不一致

- **现象**：在已完成页撤销一条计划，回到待完成页，它出现的位置和下拉刷新后的位置**不一样**
- **原因**：云函数 `list` 有一套排序（有提醒的按 `remindAt` 升序在前，其余按 `createdAt` 降序），
  前端 store 本地插入后又自己写了一套简化排序。
  只要两套规则有一点出入，"本地乐观更新"和"服务端返回"就会打架
- **解决**：把排序规则抽成**一个纯函数 `sortWeight(plan)`**，前后端各持一份**完全相同**的实现，
  本地插入和服务端返回都走它
  ```js
  // store/plan.store.js 与 cloudfunctions/plan/index.js 保持逐字一致
  function sortWeight(p) { /* 有 remindAt 的排前，权重相同再比 createdAt */ }
  ```
- **预防**：
  - 任何"本地先改、服务端再回"的字段（排序、计数、状态），
    计算逻辑必须**两端同源**，否则用户会看到内容"闪一下又变了"
  - M3 做同步引擎时这条会被放大——合并后重排必须复用同一个 `sortWeight`
- **相关**：`miniprogram/store/plan.store.js`、`cloudfunctions/plan/index.js`

---

## 待补充

*遇到新坑请按格式追加，并更新顶部索引表。*
