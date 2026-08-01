---
module: M3
title: M3 API 参考
tags: [API, REST, 云函数, 接口]
sources:
  - project: homekeeper
    repo: https://github.com/Simiely/homekeeper
    file: docs/05-开发指南.md
    synced_at: 2026-08-01
  - project: obsidian-agent
    repo: https://github.com/Simiely/obsidian-agent
    file: docs/05-API参考.md
    synced_at: 2026-08-01
  - project: collab-plan-miniprogram
    repo: https://github.com/Simiely/collab-plan-miniprogram
    file: docs/03-data-model.md
    synced_at: 2026-08-01
---

# M3 API 参考

> 各项目的接口一览。详细请求/响应示例见对应归档文档。

## 🏠 homekeeper · REST API

> 📌 来源:`homekeeper` · docs/05-开发指南.md + 交互式文档 `http://<host>:8000/docs`(Swagger)

| 模块 | 端点(示意) | 说明 |
|---|---|---|
| 账号 | `POST /api/auth/login` | JWT 登录 |
| 账号 | `POST /api/users` | 管理员创建用户 |
| 物品 | `GET/POST /api/items` | 物品列表 / 新增 |
| 物品 | `PUT/DELETE /api/items/{id}` | 更新 / 删除 |
| 位置 | `GET/POST /api/locations` | 位置层级树 |
| 分类 | `GET/POST /api/categories` | 分类管理 |
| 概览 | `GET /api/overview` | 统计概览 |

> 完整端点与请求/响应示例见 [归档: homekeeper docs/05-开发指南.md](../archive/homekeeper/docs/05-开发指南.md)

## 🔍 obsidian-agent · REST API

> 📌 来源:`obsidian-agent` · docs/05-API参考.md

| 模块 | 端点(示意) | 说明 |
|---|---|---|
| Vault | `GET /api/vault/tree` | 文件树 |
| Vault | `GET /api/vault/file?path=` | 读取文档 |
| Vault | `PUT /api/vault/file` | 编辑文档 |
| 搜索 | `GET /api/search?q=` | 全文检索(高亮/分页) |
| 索引 | `POST /api/index/rebuild` | 重建索引 |
| 备份 | `POST /api/backup` | 手动快照 |
| Agent | `POST /api/agent/chat` | AI 对话 |
| Agent | `GET /api/agent/sessions` | 会话列表 |

> 完整端点与请求/响应示例见 [归档: obsidian-agent docs/05-API参考.md](../archive/obsidian-agent/docs/05-API参考.md)

## ☁️ 小程序系列 · 云函数

### collab-plan-miniprogram(私有)

> 📌 来源:`collab-plan-miniprogram` · docs/03-data-model.md

| 云函数 | 职责 |
|---|---|
| `auth` | 自建账号登录/注册、Token 签发 |
| `plan` | 计划 CRUD、成员管理、完成状态 |
| `sync` | 时间戳水位线增量同步(push/pull) |
| `init-db` | 初始化数据库与索引 |
| `remind-scan` / `subscribe` | 订阅消息提醒(M4 开发中) |

### miniprogram-item-expiry

| 云函数 | 职责 |
|---|---|
| `authDocs` | 腾讯文档 OAuth 授权换 token |
| `syncToDocs` | 云库 → 腾讯文档(数据库触发器) |
| `syncFromDocs` | 腾讯文档 → 云库(定时/手动) |

### potty-training-miniprogram

| 模块 | 说明 |
|---|---|
| `utils/store.js` | 统一数据层(本地/云端自动切换) |
| `utils/cloud.js` | 云开发 CRUD + openid 检测 |

---

## 相关文档

- [M2 架构与设计](M2-架构与设计.md)
- [M4 开发指南](M4-开发指南/README.md)
- [← 返回文档中心](../README.md)
