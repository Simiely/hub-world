# Hub World · 导航中心

> 探索所有项目 — Powered by Simiely / 世界的风吹向你

🌐 在线访问：https://simiely.github.io/hub-world/

---

## ✨ 功能特性

- 暗色主题，粉红渐变强调色
- 首页：浮动卡片 + 粒子背景动画
- 目录页：Masonry 瀑布流 + 分类筛选（网页 / 工具 / 设计）
- 点击统计（localStorage）
- 响应式，移动端适配

## 🛠 技术栈

- 纯 HTML/CSS/JS（单文件，无构建依赖）
- Google Fonts（Inter + Noto Sans SC）
- GitHub Pages 托管

## 📂 添加项目

编辑 `index.html` 中的 `projects` 数组：

```js
var projects = [
  {
    name: '项目名',
    desc: '项目描述',
    icon: '📄',
    path: 'subdir',
    tags: ['标签'],
    category: 'web',
  },
];
```

## 🚀 本地预览

```bash
npx serve .
# 或直接在浏览器打开 index.html
```

## 📄 License

MIT © 2026 Simiely
