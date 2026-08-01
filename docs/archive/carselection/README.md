---
module: archive
title: README.md
tags: [carselection]
source:
  project: carselection
  repo: https://github.com/Simiely/carselection
  file: README.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/carselection/blob/main/README.md)

# CarSelection - 汽车选购辅助筛选

从预算、外观、内饰、动力、安全、科技、舒适等 **23 个大类、117 道题目** 全方位了解你的用车需求，生成结构化提示词供 AI 推荐车型。

## 目录

- `index.html` — 原始单文件版（7406 行）
- `refactored/` — 重构后的多文件模块化版本

## 使用方式

打开 `refactored/index.html` 即可使用，无需任何后端服务。

> 建议通过 HTTP 服务访问（如 `python -m http.server`），避免浏览器对 `file://` 协议的安全限制。

## 技术栈

纯前端，零依赖：HTML + CSS + JavaScript（Vanilla JS）

## 部署

`refactored/` 目录已配置 GitHub Actions 自动部署到 GitHub Pages。
