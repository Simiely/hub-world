---
module: archive
title: DEVELOPMENT.md
tags: [codebuddy-skills]
source:
  project: codebuddy-skills
  repo: https://github.com/Simiely/codebuddy-skills
  file: DEVELOPMENT.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/codebuddy-skills/blob/main/DEVELOPMENT.md)

# DEVELOPMENT.md — 开发指南 + 关键问题记录

本仓库收录的技能从 **五轮三方技术辩论共识** 中诞生（详见 `singing-segment-detector/references/`）。本文记录**开发流程**与**关键踩坑**，供后续新增/维护技能时直接参考，避免重复踩坑。

---

## 一、开发一个新技能（标准流程）

1. **初始化结构**
   ```
   <skill-name>/
   ├── SKILL.md          # YAML frontmatter(name/description) + 工作流
   ├── scripts/          # 可执行脚本（Python/Bash）
   └── references/       # 按需加载的参考资料
   ```
2. **写 SKILL.md**
   - `name`：kebab-case，全局唯一。
   - `description`：**最关键字段**。写清「做什么 + 何时用 + 触发场景（具体任务/文件类型）」。这是技能能否被准确触发的关键。
3. **实现脚本**：优先零重依赖（如仅依赖 `numpy` + 系统命令），把重依赖（模型/分离工具）做成可选降级。
4. **校验**（必须过）
   ```bash
   python3 <skill-creator>/scripts/quick_validate.py <skill-name>
   ```
5. **打包**
   ```bash
   python3 <skill-creator>/scripts/package_skill.py <skill-name>
   # 产物：<skill-name>.skill（zip），已自动剔除 __pycache__
   ```
6. **回归自测**：若有合成测试样本，跑一遍确认输出稳定可复现，再提交。

---

## 二、关键问题与坑（重要参考）

### 1. SKILL.md frontmatter 校验两大坑
| 现象 | 原因 | 解决 |
|------|------|------|
| `Description cannot contain angle brackets (< or >)` | description 里出现 `<3min` 这类写法 | 改成文字，如「3 分钟内」 |
| `mapping values are not allowed here` / `Invalid YAML` | description 值里出现未加引号的冒号，如 `two tiers: fast` 被当成 YAML key:value | 把冒号改成连字符 `two tiers - fast`，或对整段加引号 |

> 经验：`quick_validate.py` 用的是严格 YAML 解析，frontmatter 里任何 `<` `>` `:` 都容易炸。写完务必跑一遍校验。

### 2. 文件编码 / 中文显示假象
- 某次 `Write` 后 `Read` 显示成乱码（mojibake），但用 Python `io.open(p, encoding="utf-8").read()` 读出来**完全正常**——是读取端渲染问题，不是文件真坏。
- **结论**：判断中文文件是否损坏，用 Python 读而非依赖 Read 显示；修改中文文件优先用 Python 片段而非反复 Edit 比对。

### 3. 自相关基频置信度的致命坑（音频类技能通用）
- ❌ 错误：`conf = peak / np.mean(acf[range])`（用**有符号**自相关均值做分母）。
- 后果：正负自相关相互抵消 → 均值变负 → 被 `clip(0,1)` 截成 0 → **所有帧 f0_conf=0 → 检出 0 段**。
- ✅ 正确：`conf = peak / acf0`，其中 `acf0 = np.sum(frame**2)`（零延迟自相关 = 总能量），有界 [0,1]，纯周期音≈0.5、噪声≈0。
- 配套：基频取「**最低频率的显著局部峰**」，避免把谐波误判为基频（八度错误）。

### 4. 「颤音」不可靠作 fast 档主判据（核心方法论结论）
- 纯自相关 f0 估计的**帧抖动量级 ≈ 真实唱歌颤音量级**，且**受基频高低影响**：低频说话的算法抖动会被放大成「假颤音」（如 112Hz 说话 + 0.7Hz 抖动 → 11 半音；而 261Hz 真颤音 ≈ 3 半音）。
- **结论**：fast 档改用 **voiced 时间连续性** 作为主区分信号（说话碎片化→连续性低；唱歌持续→连续性高）；真正的颤音/人声特性交给 **accurate 档**（人声分离 + 模型）捕捉。这一划分正是三方辩论「规则快通道 + 模型补漏 + 多模态兜底」共识的体现。

### 5. 帧间基频稳定（`_stabilize_f0`）的中值陷阱
- k=3 中值：**过于平滑** → 模糊音节跳变 → 把「音阶移动」误判成「单音内颤音」（假阳性）。
- k=1 中值：**过于宽松** → 谐波锁定引起的帧间抖动被当成颤音（假阳性）。
- ✅ 最终方案：**八度纠错**（相邻帧比值≈2 拉回低八度）+ **一致性约束**（只允许 ±2.5 半音小抖动与八度跳变通过，非八度跳变继承前一可靠帧）+ **轻度 3 帧中值**。

### 6. 滑窗边界溢出与收紧
- ±1.0s 滚动滑窗会让检出的段边界向两侧溢出约 0.5s（窗口跨在真假边界上）。
- ✅ 加 **边界内收**（`trim_thr`，默认 0.6）：段两端若 score 仅略高于阈值（过渡帧），向内裁掉收紧时间戳，前提裁后段长仍 ≥ `min_duration`。
- 残余 ~0.24s 早溢出在 fast 档可接受；**交付级边界请用 accurate 档**。

### 7. 合成测试样本的数组越界
- BGM 琶音 / 说话音节拼接到定长数组时**超出长度** → broadcast 报错 `shapes (1920,) (2880,)`。
- ✅ 修复：拼装时做边界截断 `end = min(st + len(s), len(buf)); buf[st:end] += s[:end-st]`。

### 8. 依赖策略（刻意为之）
- fast 档**只用 `numpy` + 系统 `ffmpeg`**，不依赖 `librosa` / `webrtcvad`（环境未装）。
- 好处：零重依赖、纯 CPU、可复现、易部署。重依赖（spleeter/demucs）仅作 accurate 档可选，未装时**自动降级 fast 并告警**，不抛错、不中断。

### 9. 脚本运行目录
- 脚本内用相对/绝对路径，调用时**必须在技能目录下**运行（如 `cd singing-segment-detector && python3 scripts/detect_singing.py ...`），从 `/workspace` 直接跑会报 `can't open file '/workspace/scripts/...'`。

---

## 三、验收口径（沿用唱歌检测技能的标准，可作其他技能参考）

| 指标 | 目标 |
|------|------|
| 召回 recall | ≥ 95%（目标片段不漏） |
| 精确 precision | ≥ 92%（报出的段主要是真目标，边界 ±0.5s 内可接受） |
| 速度 | fast 档远低于 accurate 档（具体阈值随任务定） |
| 可复现 | 相同输入 + 相同参数 → 相同输出（无随机种子依赖） |
| CI 回归 | 合成/固定样本应稳定通过 |

---

## 四、提交与发布习惯（与本人其他项目一致）
- 脚本稳定后提交 GitHub；需要分发时打包 `.skill`。
- 配套 README 写清「做什么 + 怎么用」；本文（DEVELOPMENT.md）持续记录关键问题与方案，便于回溯。
- 系统级/不可逆操作先确认再执行；新工具先最小步骤验证再扩展。
