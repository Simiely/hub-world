---
module: archive
title: README.md
tags: [oc-plugin-activator]
source:
  project: oc-plugin-activator
  repo: https://github.com/Simiely/oc-plugin-activator
  file: README.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/oc-plugin-activator/blob/main/README.md)

# OC插件 快速激活工具

[![Build Windows EXE](https://github.com/Simiely/oc-plugin-activator/actions/workflows/build-exe.yml/badge.svg)](https://github.com/Simiely/oc-plugin-activator/actions/workflows/build-exe.yml)

一键清空 OctaneRender 残留 + 部署资源的 Windows 工具。深色界面，自动获取用户名。

## 使用

把程序放入包含以下三个文件夹的目录：

```
你的文件夹/
├── Activator.exe
├── thirdparty/
├── OctaneRender/
└── octane/
```

打开程序 → 选 C4D 的 plugins 目录 → 先②清空残留 → 后③复制资源 → 运行 C4D

插件失效时重复"清空+复制"即可。

> ⚠️ 如无特殊情况，本项目将不再更新，当前版本已满足日常使用需求。

## 按钮

| 按钮 | 作用 |
|------|------|
| ⑥ 📂 打开启动路径 | 打开 Windows 开机启动目录 |
| 📂 打开 OctaneRender 文件夹 | 打开 Local + Roaming 两个目录 |
| ② 清空 OctaneRender 残留文件 | 清空 Local、Roaming、octane 目录 |
| ③ 复制资源到目标路径 | 部署 thirdparty、OctaneRender、octane |

## 下载

[Releases 页面](https://github.com/Simiely/oc-plugin-activator/releases) → 下载最新版 Activator.exe

---

20260623 / 世界的风吹向你 / Workbuddy技术支持 / 开源软件
