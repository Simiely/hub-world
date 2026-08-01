# 文档中心维护指南

> 如何更新 hub-world 里的开发帮助文档中心,保证"更新不乱"。

## 目录速览

```
docs/
├── README.md                 # 文档中心索引(导航总入口)
├── modules/                  # 聚合模块文档(日常阅读与维护的主战场)
│   ├── M1-部署与快速上手.md
│   ├── M2-架构与设计.md
│   ├── M3-API参考.md
│   ├── M4-开发指南/          # 按技术栈分册
│   ├── M5-踩坑记录/          # 按平台分册
│   └── M6-更新日志.md
├── projects/                 # 35 个项目卡片页(自动生成)
├── archive/                  # 各项目原始文档快照(自动搬运)
│   └── README.md             # 归档区索引
├── _templates/               # 来源标注 / 归档 / 卡片模板
└── _scripts/                 # 维护脚本
    ├── archive_docs.py       # 全量搬运:仓库文档 → archive/(需 GitHub token)
    ├── backfill_archive.py   # 增量补齐:下载缺失的归档文件
    ├── gen_project_pages.py  # 重新生成 projects/ 卡片页
    └── check_docs.py         # 联检:链接 / frontmatter / 结构
```

## 更新流程(上游仓库变了之后)

1. **更新归档区**(搬运最新文档):
   ```bash
   # 编辑 _scripts/archive_docs.py 中的 TOKEN,然后:
   python _scripts/archive_docs.py        # 全量(会跳过已存在文件需先删,或用 backfill)
   python _scripts/backfill_archive.py    # 只下载缺失的
   ```

2. **更新项目卡片页**(描述/语言变化时):
   ```bash
   python _scripts/gen_project_pages.py
   ```

3. **更新聚合模块文档**:根据 archive/ 里同步到的新内容,手动更新 `modules/` 下的 M1-M6(它们由人维护,因为需要提炼与改写)。**务必刷新 frontmatter 里的 `synced_at`**。

4. **联检**:
   ```bash
   python _scripts/check_docs.py
   ```
   确认"关键链接全部通过"后提交。

## 来源标注规范

- 每篇文档 frontmatter 必须有 `sources` / `source` 字段(项目 / 仓库 / 文件 / 分支 / 同步日期)。
- 聚合文档中每个章节用 `> 📌 来源:<项目> · <文件>` 标注。
- 完整规范见 [_templates/SOURCE_TEMPLATE.md](../_templates/SOURCE_TEMPLATE.md)。

## 常见操作

| 需求 | 做法 |
|---|---|
| 新增一个项目 | ① 在 projects.json 加条目(HTML 导航用)② 跑 gen_project_pages.py ③ 归档其文档 |
| 新写一篇踩坑记录 | 写进对应项目仓库的 DEV.md,然后同步 archive + 更新 M5 分册 |
| 某模块文档内容过时 | 比对 archive 里对应来源文档,更新 modules/ 内容并刷新 synced_at |
| 检查是否有坏链接 | python _scripts/check_docs.py |
