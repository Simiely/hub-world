---
module: archive
title: README.md
tags: [miniprogram-item-expiry]
source:
  project: miniprogram-item-expiry
  repo: https://github.com/Simiely/miniprogram-item-expiry
  file: README.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/miniprogram-item-expiry/blob/main/README.md)

# 物品有效期小程序（云开发 + 腾讯文档智能表双向同步）

一个微信小程序，用于管理家中物品的有效期。数据主存于**微信云开发数据库**，并**双向同步**到**腾讯文档智能表**：

- 你在小程序里增删改查，家人能在腾讯文档里实时看到；
- 家人在腾讯文档里维护，也能同步回小程序（每 5 分钟自动 + 手动触发）。

> 设计取舍：用云开发做主数据源，规避了「自有备案域名」这个最大的接入门槛；腾讯文档作为「家人协同视图」，非技术的家人用熟悉的腾讯文档界面维护最顺手。

## 功能

- 物品有效期列表（按有效期升序，自动标注「剩 N 天 / 已过期 / 30 天内预警」）
- 新增 / 编辑 / 删除物品（删除会同步删除腾讯文档对应记录）
- **正向实时同步**：云库 → 腾讯文档（数据库触发器，增删改秒级）
- **反向准实时同步**：腾讯文档 → 云库（定时轮询 + 手动「同步」按钮，带变更检测仅同步变化记录）
- 哔哩哔哩粉 `#FB7299` 主题

## 架构

```
[小程序]  ↔  [云开发数据库 items]（主数据源）
                │ 数据库触发器（CREATE/UPDATE/DELETE）
                ↓
         [云函数 syncToDocs]  ──→  [腾讯文档智能表]
                ↑
         [云函数 syncFromDocs]（定时/手动）←── [腾讯文档智能表]
```

## 使用前准备

| 准备项 | 说明 |
|---|---|
| 微信小程序 AppID | [mp.weixin.qq.com](https://mp.weixin.qq.com) 注册个人/企业小程序 |
| 云开发环境 | 开发者工具内开通，记录**环境 ID** |
| 腾讯文档开放应用 | [docs.qq.com/open/dev](https://docs.qq.com/open/dev) 创建应用，拿 `appId` / `secret` |
| 智能表 | 新建一个多维表格，记录 `fileId`（URL 中）/ `sheetId` |
| 备案域名 | 用于 OAuth 回调（`redirect_uri`）——**必须你自己备案的域名** |

> ⚠️ 关于备案域名：云开发调用本身免白名单，但腾讯文档 OAuth 授权回调**仍需你自己备案的域名**。这是腾讯文档方案的残留成本。

## 部署步骤

1. **导入项目**：微信开发者工具 → 导入项目，目录选本仓库根目录（`miniprogramRoot` 已是 `./`）。
2. **改配置**：
   - `project.config.json` 的 `appid` 改成你的；
   - `config.js` 的 `env` 改成你的云开发环境 ID。
3. **建集合**：云开发控制台新建 3 个集合：
   - `items`：物品主数据（`name / expireDate / count / category / note`）
   - `mapping`：云库 `_id` ↔ 腾讯文档 `recordId` 映射（防重复同步、供删除定位）
   - `tokens`：腾讯文档 OAuth token 存储
4. **配环境变量**：每个云函数右键 → 配置环境变量，填入：
   `TDOC_APPID` / `TDOC_SECRET` / `TDOC_FILE_ID` / `TDOC_SHEET_ID` / `TDOC_REDIRECT_URI`
5. **部署云函数**：分别右键 `authDocs` / `syncToDocs` / `syncFromDocs` → 「上传并部署：云端安装依赖」。
6. **确认触发器**：
   - `syncToDocs` 绑了数据库触发器（监听 `items` 的 INSERT/UPDATE/REMOVE）；
   - `syncFromDocs` 绑了定时触发器（每 5 分钟）。
7. **完成 OAuth 授权**：访问腾讯文档授权页拿到 `code`，调用 `authDocs` 云函数换 token（细节见 `DEVELOPMENT.md`）。

## 目录结构

```
miniprogram-item-expiry/
├── app.js / app.json / app.wxss      # 小程序入口与全局样式
├── config.js                         # 环境 ID 与腾讯文档配置（占位）
├── project.config.json / sitemap.json
├── pages/
│   ├── index/                        # 列表页 + 同步/新增按钮
│   └── edit/                         # 新增/编辑页
└── cloudfunctions/
    ├── common/tdocs.js               # ★ 腾讯文档 API 封装 + Token 管理（源码）
    ├── authDocs/                     # OAuth 授权换 token
    ├── syncToDocs/                   # 云库 → 腾讯文档（数据库触发器）
    └── syncFromDocs/                 # 腾讯文档 → 云库（定时/手动）
```

> 注意：`common/tdocs.js` 是源码，部署前需复制到每个云函数目录（各函数已含副本）。

## 使用说明

- **日常管理**：打开小程序 → 新增/编辑/删除物品。改动会实时同步到腾讯文档智能表。
- **从腾讯文档同步**：家人在腾讯文档改了内容 → 点小程序首页「从腾讯文档同步」按钮（或等 5 分钟自动同步）。
- **删除**：列表项长按删除，云库与腾讯文档对应记录都会删。

## 相关文档

- 微信云开发：https://developers.weixin.qq.com/miniprogram/dev/wxcloud/
- 腾讯文档开放平台：https://docs.qq.com/open/document/saas/
- 更完整的关键问题与排错，见 **`DEVELOPMENT.md`**。
