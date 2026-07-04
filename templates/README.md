# 🎯 通用产品落地页模板 &mdash; 使用说明

本模板基于 [C4D Mesh Face Sorter](https://github.com/Simiely/c4d-mesh-face-sorter) 产品落地页提取而成，提供一套**深色主题、全屏滚动吸附**的品牌页面骨架。

---

## 📋 快速开始

### 给 AI 助手的操作步骤

1. **复制模板文件** — 将 `template.html` 复制到你的项目目录
2. **编辑 CONFIG 对象** — 打开文件，找到顶部 `var CONFIG = { ... }` 区块，**
   将所有字段的值替换为你的项目内容**
3. **保存并预览** — 直接在浏览器中打开 `.html` 文件即可看到效果
4. **微调** — 如果颜色不合适，修改 `CONFIG.accentColor`（默认玫瑰红 `#E55D6B`）
5. **部署** — 将完成的 HTML 部署到任何静态托管服务（GitHub Pages、Vercel 等）

### 注意事项

- **保持 CONFIG 所有键名不变**，不要删除或重命名字段
- **文本字段支持 HTML**：`<em>` 斜体强调，`<b>` 加粗，`<br>` 换行
- **不需要的内容留空字符串** `""` 即可
- **主题色统一**：修改 `accentColor` 一处即可全局换色
- **emoji 图标**：`icon` 字段可替换为任意 emoji 或 Unicode 字符
- **导航栏 GitHub 链接和版本号都跳转到 `repoUrl`**，版本号 hover 效果为**主题色填充反白**（非下划线）

---

## 🏗️ 模板结构

```
template.html
├── ★ CONFIG 对象（可编辑区域）
│   ├── pageTitle / brand / version       ← 页面基本信息
│   ├── accentColor                        ← 全局主题色
│   ├── hero { ... }                       ← 首屏（大标题 + 功能卡片 + 轮播）
│   │   └── tickerItems                   ← 底部轮播词数组（见下方备注说明）
│   ├── problem { ... }                    ← 痛点屏（问题描述 + 数据统计）
│   ├── features { ... }                   ← 功能介绍屏（6 宫格卡片）
│   ├── usage { ... }                      ← 使用引导屏（4 步骤 + 流程条）
│   ├── install { ... }                    ← 安装指南屏（步骤 + 代码/兼容信息）
│   ├── cta { ... }                        ← 行动号召屏（按钮 + 版权信息）
│   └── dotLabels [...]                    ← 右侧导航点标签
│
├── CSS 样式（不需要修改）
├── HTML 骨架（不需要修改）
├── 渲染脚本（注入 CONFIG 内容 → DOM）
└── 交互脚本（滚动监听 / 导航点 / 视差效果 — 不需要修改）
```

---

## 🎨 模板特性

| 特性 | 说明 |
|------|------|
| 全屏滚动吸附 | `scroll-snap-type: y mandatory` 每屏自动对齐 |
| 入场动画 | 元素淡入上移，支持 8 级延迟 (d1~d8) |
| 鼠标视差 | 痛点屏背景径向渐变跟随鼠标 |
| 背景噪点 | SVG 噪点纹理叠加，增加质感 |
| 响应式 | 860px / 520px 自适应布局切换 |
| 深色主题 | 默认 `--bg: #161110`，玫瑰红强调色 |
| 字体 | Bricolage Grotesque（标题）+ Geist（正文） |
| 无依赖 | 纯 HTML + CSS + JS，零第三方库 |

---

## ⚙️ CONFIG 字段详解

### 基础字段

```javascript
pageTitle: "浏览器标题栏文字",
brand:     "导航栏品牌名",
version:   "v1.0.0",
accentColor: "#E55D6B",   // 全局主题色（CSS --rose 变量）
repoUrl:   "https://github.com/用户/仓库",
issuesUrl: "https://github.com/用户/仓库/issues",
authorName: "作者名",
authorUrl: "https://github.com/作者",
license:   "MIT License"
```

### hero 首屏

- `titleLine1` / `titleLine2` — 大标题第一/二行（纯文本）
- `titleEmphasis` — 标题中的强调词（主题色 + 斜体）
- `featureLabel` — 功能卡片左上角小标签（纯文本）
- `featureText` — 功能卡片主文案（支持 `<b>` 加粗）
- `subtitle` — 首屏底部副标题（支持 `<b>`）
- `badgeLabel` — 右侧 badge 标签（纯文本）
- `badgeIcon` — badge 区图标（emoji）
- `tags` — 标签数组（`["标签1", "标签2", ...]`）
- `tickerItems` — 底部轮播文字数组（轮播词）
  > **备注**：轮播词在页面底部循环滚动展示，轮播词之间自动用 ✦ 分隔。
  > 示例中使用了 GitHub PAT 令牌作为占位轮播词：
  > `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
  > 实际使用时替换为产品关键词、口号或特性列表即可。

### problem 痛点屏

- `eyebrow` — 前置标签（纯文本）
- `title` — 痛点标题（支持 `<br>` `<em>`）
- `description` — 痛点描述（支持 `<strong>` `<b>`）
- `stats` — 统计数据数组
  ```javascript
  [
    { number: "1.2M", label: "统计数据\\n单位标签" },  // \\n 换行
    { number: "500",  label: "统计数据\\n单位标签" },
    { number: "1",    label: "统计数据\\n单位标签" }
  ]
  ```

### features 功能屏

- `sectionNumber` — 编号（如 "02"）
- `title` — 标题前半（纯文本）
- `titleEmphasis` — 标题后半（主题色强调）
- `items` — 功能卡片数组，每个包含 `icon`（emoji）、`name`、`desc`

### usage 使用引导屏

- `steps` — 步骤卡片数组
  ```javascript
  [
    { icon: "📦", name: "步骤名", desc: "描述", accent: true },  // accent=true 有背景色
    { icon: "🔍", name: "步骤名", desc: "描述", accent: false },
    // ... 建议4个
  ]
  ```
- `flowLabels` — 底部流程指示条（支持 `"→"` 箭头）

### install 安装屏

- `steps` — 安装步骤数组 `{ title, desc }`
- `codeSnippet` — 代码块 HTML（支持 `<br>`、`<span class="hl">`高亮、`<span class="cm">`注释）
- `compatInfo` — 兼容性信息 HTML
- `downloadUrl` / `downloadLabel` — 下载按钮

### cta 行动号召屏

- `eyebrow` — 前置标语（纯文本）
- `title` — 大标题（支持 `<em>` `<br>`）
- `buttons` — 按钮数组
  ```javascript
  [
    { url: "链接", label: "按钮文字", primary: true },   // 实心按钮
    { url: "链接", label: "按钮文字", primary: false }   // 描边按钮
  ]
  ```
- `metaHtml` — 底部元信息（支持完整的 HTML）

### dotLabels 导航点

字符串数组，长度必须为 6，如 `["Home", "Problem", "Features", "Usage", "Install", "CTA"]`

---

## 💡 典型使用场景

- **开源项目落地页** — GitHub 仓库的产品介绍页
- **SaaS 产品推广** — 功能导向的工具型产品
- **插件/工具发布页** — 类似原页面的 C4D 插件场景
- **个人作品集** — 展示项目的统一模板

---

## 📄 文件清单

```
onepage/
├── template.html    ← 可复用的产品落地页 HTML 模板
└── README.md        ← 本说明文档（for AI assistants）
```
