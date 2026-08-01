# 📚 开发帮助文档中心

> 汇总 Simiely 全部 **35 个项目**(33 公开 + 2 私有)的文档,按主题模块化组织,互相链接、可追溯来源。
> 源仓库: [github.com/Simiely](https://github.com/Simiely) · 本中心主页: [hub-world 导航](https://simiely.github.io/hub-world/)

> 🧑‍🔧 **维护者请先读** [📖 文档中心总说明(ABOUT)](ABOUT.md) —— 含目录分工、更新流程、编写规范与避坑清单。

---

## 🧭 快速定位

**场景 → 文档:**

| 我想… | 去这里 |
|---|---|
| 快速跑起某个项目 | [M1 部署与快速上手](modules/M1-部署与快速上手.md) |
| 了解某个项目怎么设计 | [M2 架构与设计](modules/M2-架构与设计.md) |
| 查接口 / API | [M3 API 参考](modules/M3-API参考.md) |
| 写代码前看规范 / 技术栈 | [M4 开发指南](modules/M4-开发指南/README.md) |
| 遇到报错 / 奇怪问题 | [M5 踩坑记录](modules/M5-踩坑记录/README.md) |
| 看版本更新历史 | [M6 更新日志](modules/M6-更新日志.md) |
| 找某个项目的全部资料 | [项目索引](projects/README.md) |
| 看原始文档快照 | [归档区](archive/README.md) |

## 🗂 模块导航

| 模块 | 内容 | 聚合来源 |
|---|---|---|
| [M1 部署与快速上手](modules/M1-部署与快速上手.md) | 每个项目的安装 / 配置 / 启动 | 全部有部署流程的项目 |
| [M2 架构与设计](modules/M2-架构与设计.md) | 架构图、模块划分、技术选型、数据流 | 文档完备的项目 |
| [M3 API 参考](modules/M3-API参考.md) | REST API / 云函数 / 接口一览 | homekeeper、obsidian-agent、小程序系列 |
| [M4 开发指南](modules/M4-开发指南/README.md) | 按技术栈:Python / Android / 小程序 / 前端 / 插件脚本 | 开发文档齐全的项目 |
| [M5 踩坑记录](modules/M5-踩坑记录/README.md) | 按平台:Python / Android / 小程序 / 前端 / 工具脚本 | 各项目 DEV.md、踩坑文档 |
| [M6 更新日志](modules/M6-更新日志.md) | 各项目版本与变更汇总 | CHANGELOG、更新日志 |
| [项目索引](projects/README.md) | 35 个项目卡片页 | 全部项目 |

## 🗄 项目一览(35)

| 类别 | 项目 |
|---|---|
| 🐍 Python 后端 | homekeeper、obsidian-agent、learning-platform、codebuddy-skills、blender-car-mesh-optimizer |
| 🤖 Android | android-adskip、DarkMask |
| 📱 微信小程序 | collab-plan-miniprogram(私有)、potty-training-miniprogram、miniprogram-item-expiry |
| 🖥 桌面工具 | WindowTinter(C#)、resources(私有) |
| 🎬 设计插件 / 脚本 | AE 系列(AE-Lyrics-Animator、AudioScale、CircleDiffusion、starry-sky-generator)、C4D 系列(c4d-mesh-face-sorter、c4d-userdata-manager、oc-plugin-activator)、Blender(blender-mesh-face-sorter)、3ds Max(vray-material-replacer)、Maya(ARTv2 属 Epic,不收录) |
| 🌐 网页 / 指南 | hub-world、windows-ltsc-guide、ntlite-windows-guide-2、vmware-install-guide、car-model-decimation、edge-multi-account-cookie、ExplorerBlurMica-whitebar-fix、windows-explorer-refresh-fix、meituan-bike-reminder、baby-hair-braiding-guide、travel-1.0、carselection、TopoGun3-Chinese-Localization |
| 📄 纯文档(空仓库) | ntlite-windows-guide(size=0,已废弃,以 -2 版为准) |

## 📌 来源与更新机制

- **单一事实来源**:各 GitHub 仓库是内容源头,本中心 `archive/` 是完整快照,`modules/` 是聚合改写。
- **来源标注**:每篇文档 frontmatter 含 `sources`(项目 / 仓库 / 文件 / 同步日期),正文章节小字标注来源。
- **更新流程**:上游仓库更新 → 同步 `archive/` → 刷新 `synced_at` → 更新相关模块文档。
- **维护指南**: [如何更新本中心](_scripts/README.md)
- **规范详见**: [来源标注模板](_templates/SOURCE_TEMPLATE.md)

## 🔗 相关入口

- [hub-world 总导航(仓库首页)](../README.md)
- [GitHub 主页](https://github.com/Simiely)
- [hub-world 在线版](https://simiely.github.io/hub-world/)
