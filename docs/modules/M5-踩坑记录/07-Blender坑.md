---
module: M5
title: M5-07 Blender 插件踩坑记录
tags: [Blender, bpy, 踩坑]
sources:
  - project: knowledge-base
    repo: https://github.com/Simiely/knowledge-base
    file: 解决方案/
    synced_at: 2026-08-03
---

# M5-07 Blender 插件踩坑记录

> 📌 本分册条目**摘录自 [knowledge-base](https://github.com/Simiely/knowledge-base)**（经验提炼层），完整条目与细节见对应链接；原始仓库见各条目的 source 字段。

## 面板与刷新

### 面板列表卡 / 自动刷新死循环

- **现象**:面板 draw 高频调用下自动刷新卡死
- **原因**:draw 每次调用都触发刷新
- **解决**:纯手动刷新 + 缓存解耦(draw 与数据刷新分离)
- **完整条目**:[Blender面板缓存与手动刷新.md](https://github.com/Simiely/knowledge-base/blob/main/解决方案/Blender面板缓存与手动刷新.md)

## 数据与撤销

### 删除物体后撤销报错

- **现象**:插件删除物体 + UNDO 后野指针崩溃
- **原因**:bpy.data 引用在删除后失效
- **解决**:让原生 Delete 处理,不自行维护引用
- **完整条目**:[BlenderUNDO与bpy.data引用陷阱.md](https://github.com/Simiely/knowledge-base/blob/main/解决方案/BlenderUNDO与bpy.data引用陷阱.md)

## UI 显示

### 中文名称显示参差

- **现象**:列表/面板中中文名称截断或对齐错乱
- **原因**:中文占 2 个显示宽度,按字符数截断会切坏
- **解决**:`ord(ch) > 0x2E80` 判断,按**显示宽度**截断
- **完整条目**:[BlenderCJK字符宽度截断.md](https://github.com/Simiely/knowledge-base/blob/main/解决方案/BlenderCJK字符宽度截断.md)

---

## 相关文档

- [M5 首页](README.md) · [M4 开发指南](../M4-开发指南/README.md) · [← 返回文档中心](../../README.md)
