---
module: archive
title: README.md
tags: [carselection]
source:
  project: carselection
  repo: https://github.com/Simiely/carselection
  file: refactored/README.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/carselection/blob/main/refactored/README.md)

# 汽车选购辅助筛选

从预算、外观、内饰、动力、安全、科技、舒适等 **23 个大类、117 道题目** 全方位了解你的用车需求，生成结构化提示词供 AI 推荐车型。

## 使用方式

打开 `index.html` 即可使用，无需任何后端服务。

> 建议通过 HTTP 服务访问（如 `python -m http.server`），避免浏览器对 `file://` 协议的安全限制。

## 项目结构

```
refactored/
├── index.html               # 入口
├── css/style.css            # 全部样式
├── js/
│   ├── data/
│   │   ├── parts.js         # 合并后的全部问卷数据
│   │   ├── parts/           # 26 个独立数据分区
│   │   └── categories.js    # 分类映射
│   └── app/
│       └── main.js          # 核心逻辑
└── README.md
```

## 技术栈

纯前端，零依赖：HTML + CSS + JavaScript（Vanilla JS）

## 部署

本目录已配置 GitHub Actions 自动部署到 GitHub Pages。
