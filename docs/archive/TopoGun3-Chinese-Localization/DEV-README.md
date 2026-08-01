---
module: archive
title: DEV-README.md
tags: [TopoGun3-Chinese-Localization]
source:
  project: TopoGun3-Chinese-Localization
  repo: https://github.com/Simiely/TopoGun3-Chinese-Localization
  file: DEV-README.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/TopoGun3-Chinese-Localization/blob/main/DEV-README.md)

# 开发与技术笔记（DEV-README）

本文记录 TopoGun 3 汉化过程中的关键技术决策、踩坑与**可复用方法论**。
目标：日后遇到「某桌面程序界面汉化」类需求，可直接借鉴，避免重复踩坑。

---

## 0. 目标程序画像

- 程序：TopoGun 3（RealtimeCG），Windows 桌面应用。
- 技术栈：**Qt5**（`Qt5Core.dll` / `Qt5Widgets.dll` 等）。
- 安装目录：`C:\Program Files\TopoGun 3\`（只有 exe / dll / ico / json，**无 UI 文件**）。
- 用户配置 / UI 目录：`%APPDATA%\TopoGun3`。

## 1. 关键问题：界面文字到底存在哪？

需求方要求「汉化且不影响程序功能」。第一步必须判断文字来源，否则可能误改 exe 导致崩溃。

探查方法：

1. 提取 exe 中的可打印字符串，看界面文字是否硬编码在二进制里：
   ```python
   import re
   data = open(r"C:\Program Files\TopoGun 3\TopoGun.exe", "rb").read()
   strs = [x.decode("latin1") for x in re.findall(rb"[\x20-\x7e]{4,}", data)]
   ```
2. 检查程序是否走 Qt 官方翻译机制（`.qm` / `.ts` 文件）—— **本例没有**。
3. 在 `%APPDATA%` 找外部 UI 定义文件：发现 `menubar/` `ui/` `tools/` `piemenu.xml` 等，
   里面含可见英文 → **文字来自外部文件**。

**结论**：可只改外部文件汉化，完全不碰 exe。这是最安全路径。

## 2. 安全汉化原则（通用）

- 只翻译「显示属性」：
  - XML：`text=` / `buttonText=` / `toolTip=`
  - `.ui`：`<property name="text|title|windowTitle|toolTip|whatsThis|statusTip|placeholderText">`
- **绝不翻译**命令 / 内部标识：`name=` `target=` `icon=` `context=` `key=` `toolName=`
  `value=` 等 —— 这些被程序用来定位功能，翻译会破坏菜单 / 工具栏。
- 不改二进制、不改文件结构、不改编码。

## 3. 大坑：TopoGun 自定义 XML 不能用标准解析器重写

`menubar.xml` / `piemenu.xml` / `tools/*/data.xml` 是 **多根节点、非标准 XML**
（TopoGun 用自己的解析器读取）。

- ❌ 错误做法：用 `xml.etree.ElementTree` 解析后 `tree.write()` 重写。
  重写会归一化结构、丢失声明顺序、拆散多根，程序读不了。
- ✅ 正确做法：**属性值定点替换** —— 用正则只替换 `text="..."` 里的英文值为中文，
  文件其余字节原样保留。`.ui` 是标准 Qt 格式，可放心做属性值替换（结构稳定）。

## 4. 不可翻译项（翻了会出 bug / 无意义）

- `context="mesh"` / `context="referencemesh"`：程序内部对象类型标识。扫描正则容易
  把它们误判为显示文字（属性值里出现 `mesh` 等词），必须排除。
- `MUD` / `ZTL`：Mudbox / ZBrush 文件格式缩写，翻译会导致导入 / 导出识别失败。
- `www.topogun.com`：网址。
- 快捷键组合（`Ctrl+S` 等）、图标名、单位、纯数字、URL：原样保留。

## 5. 扫描盲区：初次漏翻的显示属性

第一版只扫了 `text` / `toolTip` / `whatsThis`，上线后界面仍有英文。补扫发现漏了：

- `statusTip`（状态栏提示）
- `placeholderText`（输入框占位灰字）
- 个别 `toolTip` 因字符串末尾带换行 `\n` 没匹配到（词典键需带 `\n` 或用更宽松正则）

**通用做法**：做汉化前，先用一个综合扫描脚本枚举**所有**显示属性
（`text|buttonText|title|windowTitle|toolTip|whatsThis|statusTip|placeholderText`
+ `.ui` 的对应 property），确保词典 100% 覆盖，再写替换。替换后脚本应报告
「未翻译项」并列出清单，避免半翻译状态。

## 6. 如何判断残留英文来自 exe 硬编码

当用户重启后仍看到英文，用「英文原始备份目录」做交叉验证：

```python
import glob, os
bak_text = ""
for f in (glob.glob("backup/**/*.ui", recursive=True) +
          glob.glob("backup/**/*.xml", recursive=True)):
    try:
        bak_text += open(f, encoding="utf-8", errors="ignore").read()
    except Exception:
        pass
exe_only = [s for s in exe_strings if s not in bak_text]
```

若某界面文字在**外部备份文件里完全不存在**，则它由 exe 直接提供，外部无法覆盖。
本例残留如 `Export Retopologized Mesh`、`About TopoGun`、`License activated` 等即属此类。

### 是否改 exe？可行性评估

中文字节（UTF-8）通常比英文 ASCII 长，原地替换会撑爆字符串空间。评估规则：

- 中文字节数 ≤ 原英文字节数 → 可安全原地替换（本例约 **78%** 的界面文字满足）。
- 超长项（如 `About TopoGun`、`Modify Mesh`）→ 无法安全替换，保留英文。

> ⚠️ 即便长度不超，改 exe 仍有风险（杀软拦截、程序可能以长度 / 哈希引用字符串导致崩溃）。
> 本项目决策：**不碰 exe**，以绝对确保功能稳定，符合「不影响程序正常功能」的前提。

## 7. 可复用方法论（Checklist）

对任何「界面汉化 / 外部配置驱动程序」类需求：

1. [ ] 先**完整备份**整个配置目录。
2. [ ] 提取 exe 字符串 + 检查 `.qm` / `.ts`，判断文字来自 exe 还是外部文件。
3. [ ] 优先找外部 UI 文件（AppData / 安装目录 / resources），**只改外部文件**。
4. [ ] 用「属性值定点替换」而非 XML 重写（除非确认是标准格式）。
5. [ ] 综合扫描**所有**显示属性，确保词典 100% 覆盖；保留命令 ID / 格式缩写 / 快捷键。
6. [ ] 用英文备份**交叉验证**定位 exe 硬编码残留。
7. [ ] 决定是否改 exe（权衡风险），本项目选择不改。
8. [ ] 校验：替换后所有文件仍能正常解析（XML well-formed / Qt 可加载）。

## 8. 本仓库文件说明

- `TopoGun3/`：汉化后的配置目录（已剔除 `license.json`、`recentfiles.dat`、`recovery.dat`、
  `topogun_log.txt` 等用户私有 / 运行时文件，以及程序自带的法律文档）。
- `install.ps1`：自动备份 + 合并复制安装脚本（PowerShell，纯 ASCII 编码，避免 GBK 乱码）。
- 复现脚本（本地，未入库）：`analyze.py` `probe.py` `extract_all.py` `apply_all.py`
  `patch_remaining.py` `comprehensive_scan.py` `eval_exe.py` 等，位于会话工作目录
  `2026-07-17-10-00-05\`，可供二次开发参考。
