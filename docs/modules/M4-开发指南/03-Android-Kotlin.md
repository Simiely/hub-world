---
module: M4
title: M4-03 Android / Kotlin 开发指南
tags: [android, kotlin, 无障碍服务]
sources:
  - project: android-adskip
    repo: https://github.com/Simiely/android-adskip
    file: DEVELOPMENT.md
    synced_at: 2026-08-01
  - project: DarkMask
    repo: https://github.com/Simiely/DarkMask
    file: DEVELOPMENT.md
    synced_at: 2026-08-01
---

# M4-03 Android / Kotlin 开发指南

> 覆盖 android-adskip、DarkMask。共同主题:**无障碍 / 悬浮窗 / 前台服务**。

## android-adskip · 无障碍点击器

> 📌 来源:`android-adskip` · DEVELOPMENT.md / DEV.md

### 技术要点

- **无障碍服务**(AccessibilityService):检测广告按钮 → 关键词匹配 → 自动点击
- **悬浮胶囊**:可拖拽浮球(显示/隐藏/取消)
- **规则捕获**:首次点击成功自动记录 App + 按钮特征,下次秒过
- **GitHub 规则云同步**:规则/关键词备份到仓库,多设备共享
- **零轮询低功耗**:事件驱动,澎湃 OS 3 可用

### 关键权限

| 权限 | 用途 |
|---|---|
| 无障碍服务 | 核心:检测并点击按钮 |
| 悬浮窗 | 浮动胶囊 + 点击反馈 |
| 通知 | 前台保活服务 |
| 开机自启(可选) | 重启自动恢复 |

## DarkMask · 全屏降亮蒙版

> 📌 来源:`DarkMask` · README.md / DEVELOPMENT.md

### 技术要点

- **纯前台服务**(`OverlayService`),无后台进程
- 全屏蒙版:`TYPE_APPLICATION_OVERLAY` + WindowManager,覆盖状态栏与刘海
- HSL 调色 + 3 预设 + 长按存色
- 预设存储:SharedPreferences
- 通知栏快捷操作 + 下拉快捷磁贴

### 构建

```bash
./gradlew assembleDebug
# APK → app/build/outputs/apk/debug/
```

CI:GitHub Actions 自动构建(JDK 17 + Android SDK 35 + Gradle 8.9),推 main 自动触发。

---

## 相关文档

- [M1 部署与快速上手](../M1-部署与快速上手.md)
- [M5 踩坑记录 · Android](../M5-踩坑记录/02-Android坑.md)
- [返回 M4 索引](README.md)
