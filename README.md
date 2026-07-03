# Hub World · 导航中心

> 探索所有项目 — Powered by Simiely / 世界的风吹向你

🌐 在线访问：https://simiely.github.io/hub-world/

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
