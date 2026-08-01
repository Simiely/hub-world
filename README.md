# Hub World · 导航中心

> 探索所有项目 — Powered by Simiely / 世界的风吹向你

🌐 在线访问：https://simiely.github.io/hub-world/

---

## 📚 开发帮助文档中心

**35 个项目的完整文档,模块化组织、可追溯来源。**

👉 **[进入开发帮助文档中心](docs/README.md)**

| 你想… | 去这里 |
|---|---|
| 快速跑起某个项目 | [M1 部署与快速上手](docs/modules/M1-部署与快速上手.md) |
| 了解项目怎么设计 | [M2 架构与设计](docs/modules/M2-架构与设计.md) |
| 查接口 / API | [M3 API 参考](docs/modules/M3-API参考.md) |
| 写代码前看规范 | [M4 开发指南](docs/modules/M4-开发指南/README.md) |
| 遇到报错 | [M5 踩坑记录](docs/modules/M5-踩坑记录/README.md) |
| 看版本更新 | [M6 更新日志](docs/modules/M6-更新日志.md) |
| 找某个项目的全部资料 | [项目索引](docs/projects/README.md) |
| 看原始文档快照 | [归档区](docs/archive/README.md) |
| **维护文档中心(更新/规范/避坑)** | [📖 总说明 ABOUT](docs/ABOUT.md) |

---

## ✨ 功能特性

- 深/浅色主题一键切换
- 首页：浮动卡片 + 粒子背景动画
- 目录页：卡片网格 + 分类筛选（网页 / 工具 / 设计）
- 响应式，移动端适配

## 🛠 技术栈

- 纯 HTML/CSS/JS（单文件，无构建依赖）
- Google Fonts（Inter + Noto Sans SC）
- 项目数据通过 `projects.json` 外部文件管理
- GitHub Pages 托管

## 📂 添加项目

编辑 `projects.json` 文件，在 `projects` 数组中添加条目：

```json
{
  "name": "项目名",
  "desc": "项目简介",
  "icon": "📄",
  "path": "subdir",
  "tags": ["标签1", "标签2"],
  "category": "web"
}
```

**字段说明：**

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | ✅ | 项目名称，显示在卡片上 |
| `desc` | ❌ | 项目描述 |
| `icon` | ❌ | 图标（emoji 或文字），默认 📄 |
| `path` | ✅ | 子项目目录名，对应仓库内的文件夹 |
| `tags` | ❌ | 标签列表（如 `["旅行","定制"]`） |
| `category` | ❌ | 分类标识，需与导航 tab 的 `data-cat` 一致 |

**支持分类：** `web`（网页）/ `tool`（工具）/ `design`（设计）

> ⚠️ 每次修改 `projects.json` 后推送至 GitHub，Pages 构建完成后即自动更新。

## 🚀 本地预览

```bash
# 方式一：使用 HTTP 服务器（推荐）
npx serve .

# 方式二：直接用浏览器打开 index.html
# 注意：file:// 协议下 fetch 不可用，会使用内置 fallback 数据
```

## 📄 License

MIT © 2026 Simiely
