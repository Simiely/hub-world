---
module: M5
title: M5 踩坑记录
tags: [踩坑, 排错, 经验]
sources:
  - project: homekeeper
    repo: https://github.com/Simiely/homekeeper
    file: docs/03-踩坑与排错.md
    synced_at: 2026-08-01
  - project: collab-plan-miniprogram
    repo: https://github.com/Simiely/collab-plan-miniprogram
    file: docs/09-pitfalls.md
    synced_at: 2026-08-01
---

# M5 踩坑记录

> 按平台聚合的踩坑与排错经验。遇到问题先翻这里,再翻对应项目的原始踩坑文档。
> 🔗 **完整经验库**:跨项目沉淀的 54+ 条经验(含本页摘录的完整版)在 [knowledge-base](https://github.com/Simiely/knowledge-base)(经验提炼层),按需直达。

## 分册导航

| 分册 | 覆盖平台 | 来源 |
|---|---|---|
| [01-微信小程序坑](01-微信小程序坑.md) | 小程序 / 云开发 | potty-training、collab-plan、item-expiry |
| [02-Android坑](02-Android坑.md) | Android / Kotlin | android-adskip、DarkMask |
| [03-Python坑](03-Python坑.md) | FastAPI / Django / 后端 | homekeeper、obsidian-agent、learning-platform |
| [04-桌面与脚本坑](04-桌面与脚本坑.md) | C# / AE / C4D / Blender / Max | WindowTinter、AE 系列、vray 等 |
| [05-AE脚本坑](05-AE脚本坑.md) | AE / ExtendScript / ScriptUI | knowledge-base（ES3/matchName/布局/表达式） |
| [06-C4D插件坑](06-C4D插件坑.md) | C4D / Python SDK | knowledge-base（2026 迁移/对话框/用户数据） |
| [07-Blender坑](07-Blender坑.md) | Blender / bpy | knowledge-base（面板/UNDO/CJK） |
| [08-Web前端坑](08-Web前端坑.md) | Web / Django / Safari | knowledge-base（Safari 布局/JS/Node 工具） |
| [09-浏览器扩展坑](09-浏览器扩展坑.md) | 浏览器扩展 / MV3 | knowledge-base（权限/SW/存储） |

> 05-09 分册摘录自 knowledge-base,只保留要点 + 链接,完整内容在经验库。

## 使用方式

1. 先按平台找分册
2. 每条记录统一格式:**现象 → 原因 → 解决方案**
3. 想了解完整上下文,链到 [归档区](../../archive/) 的对应 `DEV.md` / 踩坑文档

## 高频坑 TOP 速查

- **小程序 iPad 适配**:CSS `@media` 在 iPad 不命中,`windowWidth` 返回绘制区宽度不可靠 → 用 `screenWidth` + `.tablet` 类 + px 覆盖
- **微信云函数共享代码**:改 `_shared` 后必须 `npm run sync:shared`,否则云函数用旧代码
- **腾讯文档 OAuth**:回调必须用**备案域名**,云开发免白名单但 OAuth 不行
- **Android 悬浮窗**:澎湃 OS / MIUI 需手动开"自启动"和"省电无限制"

---

## 相关文档

- [M4 开发指南](../M4-开发指南/README.md)
- [M6 更新日志](../M6-更新日志.md)
- [← 返回文档中心](../../README.md)
