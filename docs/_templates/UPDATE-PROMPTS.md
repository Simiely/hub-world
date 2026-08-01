# 更新提示词模板(UPDATE-PROMPTS)

> 用 AI 更新文档中心时,直接复制对应场景的提示词发给 AI 即可。
> AI 收到后应:读维护指南 → 按流程执行 → 联检 → 推送。
> 需要 AI 提前知道的核心文件:
> - 总说明: `docs/ABOUT.md`
> - 维护指南: `docs/_scripts/README.md`
> - 来源规范: `docs/_templates/SOURCE_TEMPLATE.md`
> - 联检脚本: `docs/_scripts/check_docs.py`

---

## 场景 1:某个项目更新了文档(最常见)

> 用法:把 `<项目名>`、`<改动内容>` 替换后发送。

```
帮我更新 hub-world 文档中心。

项目 <项目名> 有文档更新,改动内容是:<简要说明改动,如"新增了 X 功能的使用文档"/"重构了 API" >。

请按 docs/_scripts/README.md 的更新流程执行:
1. 先读 docs/ABOUT.md 和 docs/_scripts/README.md 了解规范
2. 同步该项目的归档文档到 docs/archive/<项目名>/ 下(需 GITHUB_TOKEN 环境变量)
3. 更新 modules/ 下涉及该项目的聚合文档(提炼、改写)
4. 刷新相关文档 frontmatter 的 synced_at 为今天
5. 运行 check_docs.py 联检,确认无坏链
6. 提交并推送到 GitHub main 分支

完成后告诉我改了哪些文件。
```

## 场景 2:新增一个项目

```
帮我往 hub-world 文档中心新增项目 <项目名>。

项目信息:<GitHub 地址 / 语言 / 一句话描述 / 主要文档位置>

请按 docs/ABOUT.md「场景 B:新增一个项目」执行:
1. 归档文档到 docs/archive/<项目名>/
2. 生成项目卡片页到 docs/projects/<项目名>.md
3. 在 modules/ 对应分册补充条目(M1 部署 / M4 开发指南 / M5 踩坑等)
4. 更新 projects/README.md 和 docs/README.md 的项目一览表
5. check_docs.py 联检后推送

完成后告诉我新增了哪些文件。
```

## 场景 3:记录一个新踩的坑

```
我在项目 <项目名> 遇到了一个问题,记录到文档中心:

现象:<现象描述>
原因:<根因>
解决方案:<解法>

请:
1. 先按规范写入项目仓库的 DEV.md 源头(如果方便)
2. 同步到 docs/archive/<项目名>/DEV.md
3. 在 docs/modules/M5-踩坑记录/ 对应平台分册补充一条(格式:现象 → 原因 → 解决方案)
4. 刷新该分册 synced_at,联检后推送
```

## 场景 4:批量刷新全部项目文档

```
帮我把 hub-world 文档中心的所有项目文档重新同步一遍:
1. 用 GITHUB_TOKEN 全量重跑 docs/_scripts/archive_docs.py 更新归档
2. 重跑 gen_project_pages.py 刷新项目卡片页
3. 检查 modules/ 各文档与归档内容是否一致,不一致的更新并刷新 synced_at
4. check_docs.py 联检后推送
```

## 场景 5:修正文档中心的错误

```
docs/ 文档中心里有错误:<指出哪篇文档、哪里不对、正确内容是什么>

请:
1. 判断错误来源:modules 里写错 → 直接改;archive 与 GitHub 原文不一致 → 以原文为准重新同步
2. 不要直接改 archive 正文(它是快照,只由同步脚本更新)
3. 刷新涉及文档的 synced_at,联检后推送
```

---

## 通用要求(所有场景)

- **token**:维护脚本从环境变量 `GITHUB_TOKEN` 读 token,**不要**把 token 写进任何代码或文档。
- **联检**:推送前必须 `python docs/_scripts/check_docs.py`,确认"关键链接全部通过"。
- **归档保真**:`docs/archive/` 是源文档快照,正文不改写,只由同步脚本覆盖。
- **来源标注**:聚合文档每章节保留 `> 📌 来源:<项目> · <文件>` 标注。
- **推送**:走 clone → 修改 → commit → push 的流程,别覆盖远程历史。
