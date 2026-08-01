---
module: M5
title: M5-02 Android 踩坑记录
tags: [android, kotlin, 无障碍, 踩坑]
sources:
  - project: android-adskip
    repo: https://github.com/Simiely/android-adskip
    file: DEV.md
    synced_at: 2026-08-01
  - project: DarkMask
    repo: https://github.com/Simiely/DarkMask
    file: DEVELOPMENT.md
    synced_at: 2026-08-01
---

# M5-02 Android 踩坑记录

> 📌 来源:`android-adskip` DEV.md / DEVELOPMENT.md、`DarkMask` DEVELOPMENT.md

## 国产 ROM 适配

### 悬浮窗 / 无障碍被系统杀掉

- **现象**:Xiaomi/OPPO/Vivo 上悬浮窗不显示、无障碍服务掉线
- **原因**:国产 ROM 有自启动管理和省电策略
- **解决**:手动开启"自启动"和"省电无限制";前台服务保活 + 通知权限

### 后台保活

- **现象**:切后台后服务被杀
- **原因**:Android 后台限制
- **解决**:前台服务(foreground service) + 常驻通知;开机自启可选恢复

## 无障碍服务

### 事件驱动 vs 轮询

- **设计取舍**:轮询会持续耗电;用无障碍事件监听 + 特征匹配,零轮询低功耗
- **要点**:关键词匹配("跳过"、"关闭广告") + 首次点击成功自动捕获规则,下次秒过

## 悬浮窗权限

- **现象**:`TYPE_APPLICATION_OVERLAY` 无法显示
- **原因**:未授予悬浮窗权限(Android 13+ 还需通知权限)
- **解决**:引导用户手动开启权限;首次启动时按钮跳转设置页

---

## 相关文档

- [M4-03 Android 开发指南](../M4-开发指南/03-Android-Kotlin.md)
- [返回 M5 索引](README.md)
