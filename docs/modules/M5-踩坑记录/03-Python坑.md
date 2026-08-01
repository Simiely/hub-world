---
module: M5
title: M5-03 Python 踩坑记录
tags: [python, fastapi, django, 踩坑]
sources:
  - project: homekeeper
    repo: https://github.com/Simiely/homekeeper
    file: docs/03-踩坑与排错.md
    synced_at: 2026-08-01
  - project: obsidian-agent
    repo: https://github.com/Simiely/obsidian-agent
    file: docs/08-踩坑记录.md
    synced_at: 2026-08-01
  - project: learning-platform
    repo: https://github.com/Simiely/learning-platform
    file: DEV.md
    synced_at: 2026-08-01
---

# M5-03 Python 踩坑记录

> 📌 来源:`homekeeper` docs/03-踩坑与排错.md、`obsidian-agent` docs/08-踩坑记录.md、`learning-platform` DEV.md

## 部署 / Docker

### 数据持久化丢失

- **现象**:容器重启后数据丢了
- **原因**:SQLite 数据库写在容器内层
- **解决**:卷挂载 `-v $(pwd)/data:/app/data`,数据库落盘宿主机

### SECRET_KEY 默认值安全隐患

- **现象**:部署后 JWT 异常 / 安全问题
- **原因**:使用了默认 SECRET_KEY
- **解决**:`.env` 必须改随机长字符串:`python -c "import secrets;print(secrets.token_hex(32))"`

## 搜索 / 中文分词

### 中文全文检索

- **现象**:直接 LIKE 查询慢、分词不准
- **解决**:SQLite FTS5 + jieba 中文分词;可插拔换 Meilisearch

## 前端 / 触屏

### Safari 兼容(Safari 适配系列)

- **现象**:learning-platform 在 Safari 上音频播放、CSS 布局异常
- **解决**:详见 `learning-platform` DEV.md 的完整历史记录(图片焦点、音频播放、CSS 布局)

---

## 相关文档

- [完整踩坑库: homekeeper](../../archive/homekeeper/docs/03-踩坑与排错.md)
- [完整踩坑库: obsidian-agent](../../archive/obsidian-agent/docs/08-踩坑记录.md)
- [完整踩坑库: learning-platform DEV.md](../../archive/learning-platform/DEV.md)
- [返回 M5 索引](README.md)
