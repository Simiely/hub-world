---
module: archive
title: README.md
tags: [TopoGun3-Chinese-Localization]
source:
  project: TopoGun3-Chinese-Localization
  repo: https://github.com/Simiely/TopoGun3-Chinese-Localization
  file: README.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/TopoGun3-Chinese-Localization/blob/main/README.md)

# TopoGun 3 简体中文汉化包

非官方的 TopoGun 3（RealtimeCG）简体中文界面汉化。

TopoGun 3 没有提供官方中文语言包，界面文字默认全部为英文。本项目通过替换程序在
`%APPDATA%\TopoGun3` 下的界面定义文件（Qt `.ui` 与自定义 `.xml`），将所有可见文字
翻译为简体中文。

## 项目简介

- **汉化对象**：TopoGun 3 的界面配置文件（菜单、工具栏、工具面板、对话框、提示等）。
- **安全原则**：
  - **不修改 `TopoGun.exe`** —— 所有改动只发生在外部 UI 文件，程序二进制完全不动。
  - **可逆** —— 安装前自动备份原配置，随时可一键还原。
  - **仅改显示文字** —— 命令 ID（`name=` / `target=` / `icon=` / `context=` / `key=`
    / `toolName=`）一律保留，不影响任何功能。

## 适用范围

| 界面范围 | 状态 |
|----------|------|
| 主菜单 / 工具栏 | ✅ 已汉化 |
| 15 个工具面板（Bridge / Brush / Cut / Draw / Extrude …） | ✅ 已汉化 |
| 右键圆盘菜单（Pie Menu） | ✅ 已汉化 |
| 快捷键管理界面 | ✅ 已汉化 |
| 偏好设置对话框 | ✅ 已汉化 |
| 烘焙 / 重拓扑 / 减面 / 遮罩等对话框 | ✅ 已汉化 |
| 悬浮提示（tooltip）/ 状态栏提示 / 输入框占位符 | ✅ 已汉化 |

### 已知限制（非汉化遗漏，属刻意保留）

- **少量英文来自 `TopoGun.exe` 内部硬编码**（如 About 对话框、部分子菜单项、许可界面、
  运行时状态消息）。这些字符串在任何外部 UI 文件里都不存在，无法靠外部文件覆盖。
  为保证「不影响程序正常功能」，本项目**刻意不改 exe**。
- 文件格式缩写 **`MUD`**（Mudbox）、**`ZTL`**（ZBrush）与官网 **`www.topogun.com`**
  保留英文 —— 翻译前者会破坏导入/导出识别，后者翻译毫无意义。

## 安装方法

两种方式任选其一。**手动方式无需运行任何脚本，最稳妥。**

### 方法一：手动安装（推荐，纯文件管理器操作）

1. **完全退出** TopoGun 3（包括后台进程）。
2. 备份原配置（建议）：
   - 打开文件资源管理器，在地址栏输入 `%APPDATA%\TopoGun3` 并回车；
   - 把该 `TopoGun3` 文件夹复制一份，重命名为 `TopoGun3.bak`。
3. 打开本仓库里的 `TopoGun3` 文件夹，**按 `Ctrl+A` 全选其中全部内容**。
4. 回到 `%APPDATA%\TopoGun3` 窗口，按 `Ctrl+V` 粘贴；
   若弹出「替换或跳过文件」对话框，选择 **「替换目标中的文件」**（对所有冲突项应用）。
5. 重新启动 TopoGun 3。

> 说明：本仓库的 `TopoGun3` 文件夹**不含** `license.json` 等你的个人授权 / 运行时文件，
> 因此粘贴时只会覆盖界面文件，你的授权信息会被原样保留，不会丢失。
> 注意：**不要**直接把整个 `TopoGun3` 文件夹「拖进」AppData —— 那样会变成嵌套的
> `TopoGun3\TopoGun3\`。务必先进入文件夹、全选**内部内容**再粘贴。

### 方法二：安装脚本（自动备份）

如果你愿意运行 PowerShell 脚本，可用脚本一键完成（自动备份 + 合并复制）：

1. 完全退出 TopoGun 3。
2. 右键 `install.ps1` → 「使用 PowerShell 运行」
   （或命令行：`powershell -ExecutionPolicy Bypass -File install.ps1`）。
3. 重新启动 TopoGun 3。

脚本会先把 `%APPDATA%\TopoGun3` 备份到 `TopoGun3_backup_<时间戳>`，再以
**合并**方式复制中文文件，保留你自己的 `license.json` 等个人文件。

> 提示：`%APPDATA%` 通常对应 `C:\Users\<你的用户名>\AppData\Roaming`。
> 若程序提示「重置 UI」后中文消失，是因为程序用 `defaults/` 模板还原；本仓库已
> 一并汉化 `defaults/`，重新安装一次即可。

## 卸载 / 还原

- 用安装脚本生成的 `TopoGun3_backup_<时间戳>` 文件夹覆盖回 `%APPDATA%\TopoGun3`；
  或手动把备份的 `TopoGun3.bak` 复制回去。

## 目录结构

```
TopoGun3-Chinese-Localization/
├── README.md            # 本文件：项目介绍与使用说明
├── DEV-README.md        # 技术笔记：关键问题与可复用方法论
├── install.ps1          # 安装脚本（自动备份 + 合并复制）
└── TopoGun3/            # 汉化后的配置目录（拖放覆盖包）
    ├── menubar/  toolbars/  piemenu/  shortcuts/
    ├── tools/  ui/  preferences/  defaults/
    └── icons/  textures/  shaders/  reports/
```

## 免责声明

本项目与 TopoGun 官方无关，仅对界面配置文件做翻译，不修改程序本体。请配合你合法授权的
TopoGun 3 副本使用。汉化文件不包含任何官方资源的版权内容；仓库已剔除 `license.json`
等用户私有文件。
