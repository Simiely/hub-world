---
module: M5
title: M5-08 Web 前端踩坑记录
tags: [Web, Django, Safari, 踩坑]
sources:
  - project: knowledge-base
    repo: https://github.com/Simiely/knowledge-base
    file: 解决方案/
    synced_at: 2026-08-03
---

# M5-08 Web 前端踩坑记录

> 📌 本分册条目**摘录自 [knowledge-base](https://github.com/Simiely/knowledge-base)**（经验提炼层），完整条目与细节见对应链接；原始仓库见各条目的 source 字段。

## iOS Safari 布局（移动端 Web 最高频）

### 100vh / bfcache / flex+min-height / safe-area 四坑

- **现象**:iPad 第二次打开铺不满屏、刘海遮挡、布局塌缩
- **原因**:① `100vh` 含地址栏且 bfcache 用旧值;② Safari flex+min-height 同时用会塌缩;③ `viewport-fit=cover` 无 safe-area 配套
- **解决**:JS `--vh`(`window.innerHeight*0.01`)替代 100vh;body 保持无 flex;`env(safe-area-inset-*)` 避让刘海
- **完整条目**:[iOSSafari布局三坑.md](https://github.com/Simiely/knowledge-base/blob/main/解决方案/iOSSafari布局三坑.md)

### Safari 关键 JS 库不用 CDN

- **现象**:Safari 页面突然卡顿
- **原因**:Tracking Prevention 拦截 CDN 域 localStorage 访问
- **解决**:关键 JS 库下载到本地 static/ 同域托管
- **完整条目**:[关键JS库本地托管不用CDN.md](https://github.com/Simiely/knowledge-base/blob/main/解决方案/关键JS库本地托管不用CDN.md)

## Django 后端

### 改内容丢用户数据

- **现象**:每次改内容数据就重建,用户进度丢失
- **解决**:数据表用稳定唯一键(code) + `update_or_create` 增量同步,从不删除
- **完整条目**:[数据表稳定唯一键与增量同步.md](https://github.com/Simiely/knowledge-base/blob/main/解决方案/数据表稳定唯一键与增量同步.md)

## 前端 JS

### IIFE 缺分号 / Alpine 写入

- **现象**:整段 script 失效、Alpine 改了不生效
- **原因**:IIFE 前缺分号被解析成调用;Alpine 修改嵌套对象需走 `this.xxx` 路径
- **完整条目**:[前端JS两坑IIFE分号与Alpine写入.md](https://github.com/Simiely/knowledge-base/blob/main/解决方案/前端JS两坑IIFE分号与Alpine写入.md)

## Node / 本地工具

- 本地服务防浏览器缓存旧代码(`Cache-Control: no-store`):[本地服务防浏览器缓存旧代码.md](https://github.com/Simiely/knowledge-base/blob/main/解决方案/本地服务防浏览器缓存旧代码.md)
- 请求必须带超时 + UI finally 恢复:[请求必须带超时与UI状态finally恢复.md](https://github.com/Simiely/knowledge-base/blob/main/解决方案/请求必须带超时与UI状态finally恢复.md)
- 本地工具被其他端口调用开 CORS:[本地工具服务跨域被拦需开CORS.md](https://github.com/Simiely/knowledge-base/blob/main/解决方案/本地工具服务跨域被拦需开CORS.md)
- 历史快照数据建模三原则(去重键+上限+升序):[历史快照数据建模三原则.md](https://github.com/Simiely/knowledge-base/blob/main/解决方案/历史快照数据建模三原则.md)

---

## 相关文档

- [M5 首页](README.md) · [M4 开发指南](../M4-开发指南/README.md) · [← 返回文档中心](../../README.md)
