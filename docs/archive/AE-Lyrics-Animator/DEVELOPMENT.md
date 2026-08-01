---
module: archive
title: DEVELOPMENT.md
tags: [AE-Lyrics-Animator]
source:
  project: AE-Lyrics-Animator
  repo: https://github.com/Simiely/AE-Lyrics-Animator
  file: DEVELOPMENT.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/AE-Lyrics-Animator/blob/main/DEVELOPMENT.md)

# 开发记录

## 概述

本项目是一个针对 Adobe After Effects 2026 中文版的歌词逐字动画工具脚本。开发过程中遇到了多个 AE API 跨版本兼容性问题，记录了解决方案。

当前版本：**v3.5**，约 1174 行，单文件 IIFE 结构。

## 关键技术节点

### 1. AE 2026 中文版的 API 差异

**问题：** AE 2026 中文版中，属性面板显示中文，但 matchName 仍然是英文。ScriptUI 操作 API 依赖 matchName 而非 displayName。且与标准英文文档描述的 matchName 存在差异。

**解决方案：** 所有属性访问均使用 matchName + 候选 fallback 列表，支持多版本兼容。关键 `addAnimProperty()` 函数对每个属性准备了多组候选名。

```javascript
// 典型 fallback 链
if (propType === "ADBE Text Position") candidates = [
    "ADBE Text Position", "ADBE Text Position 2D",
    "ADBE Text Position 3D", "Position", "位置"
];
```

### 2. Text Animators 组位置变化

**问题：** 标准 AE 文档中，Text Animators 作为图层的直接子属性访问（`layer.property("ADBE Text Animators")`）。但在 AE 2026 中文版中，Text Animators 位于 `ADBE Text Properties` 内部。

**解决方案：** 增加备选路径查找（`findAnimatorsGroup()` 函数）：

```javascript
var animatorsGroup = layer.property("ADBE Text Animators");
if (!animatorsGroup) {
    var textProps = layer.property("ADBE Text Properties");
    animatorsGroup = textProps.property("ADBE Text Animators");
}
```

### 3. Range Selector 的属性命名

**问题：** Range Selector 的 Start/End 有 4 套命名：
- `ADBE Text Percent Start / ADBE Text Percent End`（百分比模式）
- `ADBE Text Index Start / ADBE Text Index End`（索引模式）
- `ADBE Text Start / ADBE Text End`（通用简写，部分版本不支持）
- 显示名：`Start / End / 起始 / 结束`

**经验：** AE 2026 中 Index 模式的 Start/End 是隐藏属性（3D 类型），`setValue()` 会报错。Percent 模式可以正常使用。

### 4. Animator 属性组的 matchName

**问题：** Animator 内部有两个子组：`ADBE Text Selectors`（选择器）和 `ADBE Text Animator Properties`（动画属性）。在 AE 2026 中文版中，`ADBE Text Properties`（即 `ADBE Text Animator Properties`）有 103 个子属性，包含大量预置属性，`addProperty("ADBE Text Position")` 在某些情况下会失败。

**解决方案：** 先尝试 `addProperty` 创建新属性（避免触及隐藏的预置属性），失败后再回退到 `property()` 访问。

### 5. 3D 属性值类型

**问题：** Position 属性在某些版本中是 3D 属性，需要传 3 个值 `[x, y, z]`，而普通 2D 属性只需要 `[x, y]`。

**解决方案：** 检测 `propertyValueType` 动态适配（v3.5 改用 `PropertyValueType.ThreeD` 常量替代魔法数字）：

```javascript
if (pType === PropertyValueType.ThreeD) {
    entryPosProp.setValue([-pEntryOff, 0, 0]);
} else {
    entryPosProp.setValue([-pEntryOff, 0]);
}
```

### 6. textIndex 表达式变量不可用

**问题：** AE 中标准表达式变量 `textIndex`（返回当前字符在文本中的序号）在 AE 2026 中提示未定义。所有使用该变量的表达式被禁用。

**最终方案：** 放弃表达式层的索引获取，改为**每个字符独立建一个文字动画器**，每个动画器的 Range Selector 锁定到单个字符（Percent 模式），Position 表达式中直接硬编码字符索引作为相位偏移：

```javascript
// 每个字符 ci 的表达式
"[0, Math.sin(time * freq * 2 + " + ci + " * 0.8) * amp]"
```

这避免了表达式引擎中的 `textIndex` 依赖，同时实现了真正的逐字错落效果。

### 7. 调试策略

**问题：** AE ExtendScript 的 `alert()` 弹窗内容不可复制，长调试信息无法完整获取。

**解决方案：** 开发阶段实现了 `showDebugDialog()` 函数，提供一个带多行文本框的窗口，支持全选复制（Ctrl+A, Ctrl+C）。发布后移除。

### 8. 逐字独立动画器方案（替代 textIndex）

**问题：** `textIndex` 表达式变量在 AE 2026 中不可用，无法在表达式中获取当前字符索引来创建独立的相位偏移。

**最终方案：** 每个字符独立创建一个文字动画器，通过 Range Selector 锁定到单个字符：

```
字符1 → 动画器"歌词_高度_1" → Range [83.33, 100] → Position 表达式 idx=1
字符2 → 动画器"歌词_高度_2" → Range [66.67, 83.33] → Position 表达式 idx=2
...
```

**关键实现细节：**
1. Range Selector 的 Index Start/End 在 AE 2026 中是隐藏属性（3D 类型），`setValue()` 失败
2. 解决方案：先用 `addKey(startTime)` + `setValueAtKey()` 绕过隐藏限制
3. 再回退到 `expression = String(ci)` 用表达式返回常量值
4. ⚠️ **实测发现 Index 模式的问题**：Selector 默认 Units 为 Percent，仅设置 Index Start/End 而不切换 Units 会导致设置被忽略。Percent 模式可以精确隔离单个字符，无需改用 Index。

### 9. 动画起始时间偏移

**需求：** 动画应从合成中播放头所在位置开始，而非固定从 0 秒。

**实现：** 读 `comp.time` 作为基准时间，所有关键帧时间偏移：

```javascript
var startTime = comp.time;
// 所有 addKey / setValueAtKey 都使用 startTime + offset
var k1 = entryStartProp.addKey(startTime);
entryStartProp.setValueAtKey(k1, 0);
var k2 = entryStartProp.addKey(startTime + pEntryDur / pSpeed);
entryStartProp.setValueAtKey(k2, 100);
```

### 10. 预设存储与持久化（v3.5 重写）

**需求：** 用户保存的预设参数应随工程文件保存，换电脑打开仍可保留。同时不依赖工程保存操作。

**v3.5 双层存储方案：**

| 层级 | 存储方式 | 特点 |
|------|----------|------|
| 工程目录 JSON | `.aep` 同级目录 `歌词动画预设.json` | 跟工程走，不同工程独立 |
| 全局保底 | `app.settings`（AE 偏好） | 不依赖工程，随时可用 |

读取时优先读工程目录 JSON，不存在则回退到全局设置。

**关键踩坑：ExtendScript 无 JSON 对象**

v3.4 及之前使用 `app.project.xmpPacket` 存储，v3.5 改为文件存储后遇到空文件问题。根因是 ExtendScript 引擎没有内置 `JSON` 对象，`JSON.stringify()` 直接报 `ReferenceError: "JSON" is not defined`。

**解决方案：** 在存储模块前注入 JSON polyfill：

```javascript
if (typeof JSON === "undefined") { JSON = {}; }
if (typeof JSON.stringify !== "function") {
    JSON.stringify = function(obj) {
        // 手动实现序列化，支持 string/number/boolean/array/object
        // ...
    };
}
if (typeof JSON.parse !== "function") {
    JSON.parse = function(text) {
        return eval("(" + text + ")");  // ExtendScript 环境安全
    };
}
```

这个 polyfill 同时服务于工程 JSON 和 `app.settings` 两层存储。

### 11. v1.1 修复：波浪效果失效（Index → Percent 回退）

**问题：** v1.0 将高度错落的 Selector 从 Percent 模式改为 Index 模式后，波浪效果完全失效。

**根因分析：** 有两个问题叠加导致失效：

1. **Units 未切换** — Selector 默认 Units 为 `Percent`，在此模式下 `Index Start/End` 属性被忽略，所有动画器均作用于全部字符
2. **属性访问脆弱** — 通过硬编码索引（`property(4)` / `property(5)`）访问 Index Start/End，在不同 AE 版本中属性顺序可能不同

**解决方案：** 回退到 Percent 模式：

```javascript
// 按字符数等分百分比范围，精确锁定单个字符
var pStart = ((ci - 1) / textLen) * 100;
var pEnd   = (ci / textLen) * 100;
hPStart.setValue(pStart);
hPEnd.setValue(pEnd);
```

**经验教训：** Index 模式需要额外设置 Selector 的 Units 属性，且在不同 AE 版本中兼容性更差。Percent 模式在所有版本中稳定可靠。

### 12. v2.0 散落分布：seedRandom + 逐字独立动画器

**需求：** 将每个字符随机散布在画面上，且大小不一，同时支持种子参数保证可复现性。

**Position 表达式（随机位置）：**

```javascript
seedRandom(pSeed + ci, true);
r = pScatterRange;
[random(-r, r), random(-r, r)]
```

`seedRandom(seed, true)` 的第二个参数 `true` 表示 timeless mode，确保每帧返回相同值。

**Scale 表达式（随机大小）：**

```javascript
seedRandom(pSeed + ci + 9999, true);
s = random(pMinScale, pMaxScale);
[s, s]
```

> ⚠️ **踩坑记录：** AE 的 Scale 属性值本身就是百分比，直接传入原始百分比值，不要除以 100。

使用 `+ 9999` 作为种子偏移，使大小随机分布**独立于**位置随机分布。

### 13. v3.0 入场/出场方向选择

**实现：** UI 增加 `dropdownlist`，4 个选项对应 4 种方向：

| 方向索引 | 方向 | 入场 Position | 出场 Position |
|---------|------|-------------|-------------|
| 0 | 从左到右 | `[-offset, 0]` | `[+offset, 0]` |
| 1 | 从右到左 | `[+offset, 0]` | `[-offset, 0]` |
| 2 | 从上到下 | `[0, -offset]` | `[0, +offset]` |
| 3 | 从下到上 | `[0, +offset]` | `[0, -offset]` |

v3.5 中 `getDirectionPos(offset, direction, is3D, isExit)` 统一处理入场和出场（`isExit` 取反）。

### 14. v3.0 散落时间控制

**问题根因：** v2.0 散落 Position 表达式是恒定的随机偏移，从第 0 帧就完全生效，与入场动画的 Position 叠加导致不可控。

**解决方案：** 增加 `fade` 渐入因子：

```javascript
seedRandom(pSeed + ci, true);
r = pScatterRange;
t = time - startTime;
fade = linear(t, scatterStart, scatterStart + scatterTrans, 0, 1);
[random(-r, r) * fade, random(-r, r) * fade]
```

v3.5 中 `buildScatterFadeExpr()` 函数封装了这段公共片段。

### 15. v3.0 随机模糊效果

**实现：** 在散落 Animator 中为每个字符添加 Blur 属性：

```javascript
seedRandom(blurSeed + ci, true);
r = random(0, 100);
if (r < blurProb) {
    seedRandom(blurSeed + ci + 5555, true);
    random(minBlur, maxBlur) * fade;
} else {
    0;
}
```

两层 `seedRandom`：第一层决定"是否模糊"，第二层独立决定"模糊多少"。

### 16. v3.2 入场/出场模式 + 面板总开关

- **逐字模式：** Range Selector Start 关键帧扫描（0→100），配合 Opacity/Blur/Position 静态值
- **一起模式：** Range Selector 覆盖全部字符，Opacity/Blur/Position 用关键帧驱动
- 每个面板新增 `checkbox` 总开关，取消勾选跳过该动画器生成

### 17. v3.3 UI 布局稳定

| 元素 | 宽度 | 说明 |
|------|------|------|
| 标签 | 110px | 中文标签完整显示 |
| 输入框 | `["fill","center"]` | 双轴 fill 撑满剩余空间 |
| 下拉菜单 | 100px | 选项文字完整 |

**关键发现：**
- AE dockable Panel 宽度由 AE 主 UI 控制，`minimumSize`/`preferredSize` 在 Panel 模式下不影响实际面板宽度
- edittext `alignment = "fill"` 单字符串只作用垂直轴，必须用 `["fill", "center"]` 双轴格式

### 18. v3.4 代码重构

1. `clearAnimators()` 复用 `findAnimatorsGroup()`
2. 提取 `setBlurValue()` / `setBlurValueAtKey()`（v3.5 合并为 `setBlur(prop, val, key)`）
3. 循环变量重命名避免混淆
4. 出场模糊变量语义修正

---

## v3.5 重大更新

### 19. 字间距动态效果

**需求：** 支持初始→结束字间距线性变化，逐字独立控制。

**实现：** 每个 Animator 使用 `ADBE Text Tracking Amount` 属性，表达式：

```javascript
linear(t, startTime, startTime + duration, startVal, endVal) * 0.1
```

**踩坑：字间距值缩放**

AE 中 Tracking Amount 的单位是 1/1000 em，与字符面板的字间距值单位一致。但实测发现填入 50 的效果约等于面板填入 500。

**解决方案：** 表达式末尾 `* 0.1`，使面板填入 50 对应实际 Tracking Amount 值 5。

### 20. 代码模块化重构

**目标：** 消除 v3.4 遗留的复制粘贴式代码，提高可维护性。

#### 20.1 集中默认值 `DEFAULTS`

```javascript
var DEFAULTS = {
    entryDur: "2.0", entryBlur: "40", entryOffset: "80",
    // ... 全部 25 个参数
};
```

UI 初始化、`loadSlot`、`resetParams` 三处统一引用，消除硬编码同步风险。

#### 20.2 UI 工厂函数

| 函数 | 用途 | 消除重复 |
|------|------|----------|
| `createParamPanel(parent, title)` | 创建参数面板 | 5 处 |
| `addParamRow(parent, label, defaultVal)` | 创建参数行 | ~15 处 |
| `addDropdownRow(parent, label, items, selIndex)` | 创建下拉框行 | 4 处 |
| `addEnableCheckbox(parent, label, defaultVal)` | 创建总开关 | 5 处 |

#### 20.3 拆分 `applyAnimation`

从 356 行拆为 7 个子函数：

| 子函数 | 职责 |
|--------|------|
| `readAnimParams()` | 读取所有 UI 参数 → params 对象 |
| `applyEntryAnim(params, group, startTime)` | 入场 Animator |
| `applyExitAnim(params, group, startTime)` | 出场 Animator |
| `applyScatterAnim(params, group, startTime, textLen)` | 散落分布 |
| `applyHeightAnim(params, group, textLen)` | 高度错落 |
| `applySpacingAnim(params, group, startTime, textLen)` | 字间距动态 |
| `applyAnimation()` | 主函数：校验 → 清除 → 调度子函数 → 状态汇总（约 85 行） |

#### 20.4 合并重复辅助函数

| 合并前 | 合并后 |
|--------|--------|
| `setBlurValue` + `setBlurValueAtKey` | `setBlur(prop, val, key)` |
| `getDirectionPos` + `getExitDirectionPos` | `getDirectionPos(offset, dir, is3D, isExit)` |
| 清除逻辑重复 2 处 | `removeLyricsAnimators()` 统一调用 |

#### 20.5 新增公共函数

- `createPerCharAnimator(group, prefix, ci, textLen, propType)` — 逐字 Animator 创建骨架（散落/高度/字间距共用）
- `buildScatterFadeExpr(seed, ci, startTime, scatterStart, scatterTrans)` — 散落表达式 fade 片段

#### 20.6 其他清理

- `setStatus(msg)` 移除未使用的 `isError` 参数
- 魔法数字 `6413` → `PropertyValueType.ThreeD`
- 表达式拼接 `+=` → `[...].join("\n")`

---

## 架构设计（v3.5）

### 文件结构

```
歌词逐字散落动画工具.jsx（~1174 行）
├── 文件头注释（版本说明）
├── IIFE 包裹 (function(thisObj) { ... })(this)
│
├── DEFAULTS 对象（集中默认值，25 个参数）
│
├── UI 工厂函数
│   ├── createParamPanel()
│   ├── addParamRow()
│   ├── addDropdownRow()
│   └── addEnableCheckbox()
│
├── UI 构建（面板 + 5 个参数模块 + 预设管理 + 操作按钮）
│   ├── 入场参数面板
│   ├── 出场参数面板
│   ├── 高度错落面板
│   ├── 字间距动态面板
│   ├── 散落分布面板
│   └── 预设管理面板（存储1-4 / 使用1-4 / 清除 / 复位）
│
├── 基础工具函数
│   ├── getVal(ctrl, def) — 读取数值
│   ├── setStatus(msg) — 状态栏
│   ├── removeLyricsAnimators(group) — 清除歌词_前缀动画器
│   └── clearAnimators() — 清除选中图层的动画器
│
├── 属性兼容层
│   └── addAnimProperty(propsGroup, propType) — 多候选名 fallback
│
├── JSON Polyfill（ExtendScript 无内置 JSON）
│   ├── JSON.stringify()
│   └── JSON.parse()
│
├── 存储模块（双层持久化）
│   ├── 工程目录 JSON
│   │   ├── getProjectPresetFile()
│   │   ├── readFromProjectFile()
│   │   ├── writeToProjectFile() — 带诊断信息
│   │   └── deleteProjectFile()
│   ├── app.settings 全局保底
│   │   ├── readFromSettings(idx)
│   │   ├── writeToSettings(idx, params)
│   │   └── deleteFromSettings(idx)
│   └── 统一接口
│       ├── presetsCache 初始化
│       ├── saveSlot(idx) — 同时写 JSON + settings
│       ├── clearAllPresets()
│       ├── updateLoadButtons()
│       ├── loadSlot(idx)
│       └── resetParams()
│
├── 动画辅助函数
│   ├── setBlur(prop, val, key) — 兼容 2D/1D + 可选关键帧
│   ├── getDirectionPos(offset, dir, is3D, isExit) — 方向偏移
│   ├── findSelectorStartEnd(sel) — Selector 属性查找
│   ├── findAnimatorProps(anim) — Animator 属性组查找
│   ├── findAnimatorsGroup(layer) — Animators 组查找
│   ├── getTextLen(layer) — 文本长度
│   ├── lockCharRange(sel, ci, textLen) — 单字符 Percent 锁定
│   ├── createPerCharAnimator(group, prefix, ci, textLen, propType) — 逐字骨架
│   └── buildScatterFadeExpr(seed, ci, startTime, scatterStart, scatterTrans)
│
├── 动画核心
│   ├── readAnimParams() — 读取所有参数 → params 对象
│   ├── applyEntryAnim(params, group, startTime) — 入场
│   ├── applyExitAnim(params, group, startTime) — 出场
│   ├── applyScatterAnim(params, group, startTime, textLen) — 散落
│   ├── applyHeightAnim(params, group, textLen) — 高度错落
│   ├── applySpacingAnim(params, group, startTime, textLen) — 字间距
│   └── applyAnimation() — 主函数（校验 → 清除 → 调度 → 状态汇总）
│
└── 入口
    ├── 按钮绑定
    ├── 面板布局 / resize / center / show
    └── updateLoadButtons() 初始化
```

### 函数索引

| 函数名 | 行号 | 功能 |
|--------|------|------|
| `createParamPanel` | 32 | 创建参数面板（工厂函数） |
| `addParamRow` | 43 | 创建参数行（工厂函数） |
| `addDropdownRow` | 54 | 创建下拉框行（工厂函数） |
| `addEnableCheckbox` | 65 | 创建总开关（工厂函数） |
| `getVal` | 265 | 从控件读取数值 |
| `setStatus` | 270 | 设置状态栏文本 |
| `removeLyricsAnimators` | 275 | 移除歌词_前缀动画器 |
| `clearAnimators` | 288 | 清除选中图层动画器 |
| `addAnimProperty` | 313 | 安全添加属性（多候选名） |
| `getProjectPresetFile` | 385 | 获取工程目录预设文件路径 |
| `readFromProjectFile` | 397 | 从 JSON 文件读取预设 |
| `writeToProjectFile` | 412 | 写入预设到 JSON（带诊断） |
| `readFromSettings` | 484 | 从 app.settings 读取 |
| `writeToSettings` | 494 | 写入到 app.settings |
| `saveSlot` | 527 | 保存预设（双层写入） |
| `loadSlot` | 580 | 加载预设到 UI |
| `resetParams` | 620 | 复位为默认值 |
| `setBlur` | 656 | 安全设置 Blur 值（2D/1D） |
| `getDirectionPos` | 670 | 方向偏移计算（入场/出场） |
| `findSelectorStartEnd` | 686 | 查找 Selector Start/End |
| `findAnimatorProps` | 697 | 查找 Animator 属性组 |
| `findAnimatorsGroup` | 712 | 查找 Animators 组 |
| `getTextLen` | 730 | 获取文本长度 |
| `lockCharRange` | 741 | 锁定单字符 Percent 范围 |
| `createPerCharAnimator` | 752 | 创建逐字 Animator 骨架 |
| `buildScatterFadeExpr` | 766 | 散落渐入表达式片段 |
| `readAnimParams` | 776 | 读取所有参数 |
| `applyEntryAnim` | 820 | 入场动画器 |
| `applyExitAnim` | 900 | 出场动画器 |
| `applyScatterAnim` | 980 | 散落分布动画器 |
| `applyHeightAnim` | 1035 | 高度错落动画器 |
| `applySpacingAnim` | 1053 | 字间距动画器 |
| `applyAnimation` | 1076 | 主函数（调度） |

### Animator 命名规范

所有生成的动画器以 `歌词_` 前缀命名，便于清除时识别：

| Animator | 命名格式 | 示例 |
|----------|----------|------|
| 入场 | `歌词_入场` | `歌词_入场` |
| 出场 | `歌词_出场` | `歌词_出场` |
| 高度错落 | `歌词_高度_{ci}` | `歌词_高度_1`, `歌词_高度_2` |
| 字间距 | `歌词_字间距_{ci}` | `歌词_字间距_1` |
| 散落分布 | `歌词_散落_{ci}` | `歌词_散落_1` |

### 预设数据结构

存储到 JSON / app.settings 的预设对象：

```javascript
{
    "1": {  // 槽位 1
        "d": "2.0",       // 入场持续时间
        "b": "40",         // 入场模糊
        "o": "80",         // 入场偏移
        "dir": 0,          // 入场方向
        "emode": 0,        // 入场模式
        "enbl": true,      // 入场启用
        "es": "3.5",       // 出场开始时间
        "ed": "2.0",       // 出场持续时间
        // ... 其余字段
        "ss1": "0",        // 字间距起始
        "ss2": "50",       // 字间距结束
        "ss3": "2.0",      // 字间距持续
        "ss4": "0",        // 字间距开始时间
        "spenbl": false,   // 字间距启用
        // ...
    },
    "2": { ... },
    "3": { ... },
    "4": { ... }
}
```

## 开发环境

- Adobe After Effects 2026 中文版
- Windows 系统
- 语法检查：`node --check`（Node.js 用于 ES3 语法验证，不能运行 AE API）
- 无构建工具，单文件部署

## 兼容性

测试环境：
- Adobe After Effects 2026 中文版
- Windows 系统

理论上兼容 AE CC 及以上版本（可能需要调整部分 matchName）。

## 版本演进

| 版本 | 核心变更 |
|------|----------|
| v1.0 | 高度错落（逐字波浪） |
| v2.0 | 散落分布（随机位置 + 随机大小） |
| v3.0 | 方向选择 + 随机模糊 + 时间控制 |
| v3.2 | 面板总开关 + 逐字/一起模式 |
| v3.3 | UI 布局稳定 |
| v3.4 | 首次代码重构 |
| v3.5 | 字间距动态 + 双层存储 + 模块化重构 |
