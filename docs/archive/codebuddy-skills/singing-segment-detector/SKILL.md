---
name: singing-segment-detector
description: 从含「多段谈话 / 多段背景音+字幕 / 多段唱歌」的长视频或音频中，提取所有唱歌片段的时间戳（JSON + SRT，带置信度）。Use when a user wants to find or segment singing parts in a mixed video (speech + BGM + on-screen text + singing), build karaoke or cover timelines, or auto-cut vocal performances. Supports two tiers - fast (rule-based, zero heavy deps, CPU) and accurate (vocal separation + model). Stable and usable, good performance.

source:
  project: codebuddy-skills
  repo: https://github.com/Simiely/codebuddy-skills
  file: singing-segment-detector/SKILL.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/codebuddy-skills/blob/main/singing-segment-detector/SKILL.md)

---

# 唱歌片段检测器 (Singing Segment Detector)

## Overview

给定一个长视频（或音频），里面夹杂着：**谈话（人声说话）**、**背景音乐+屏幕文字（无人声）**、**唱歌（人声歌唱）** 三类片段，本 skill 自动找出**所有唱歌片段的起止时间戳**，输出 JSON + SRT（带置信度）。

判定标准来自一场三方技术辩论的共识：**稳定好用 + 性能好**。核心架构：

> **抽人声 → 规则快通道(+小模型补漏) → 灰区多模态兜底 → 场景分级策略 → 后处理出时间戳**

由于纯规则下「颤音」等指标受自相关基频估计质量干扰（说话的算法抖动与唱歌真颤音量级接近、且受基频高低影响），**fast 档以「voiced 时间连续性」为主区分信号**（说话碎片化→连续性低；唱歌持续→连续性高），真正的颤音/人声特性交给 accurate 档（人声分离 + 模型）捕捉。

## When To Use

- 用户要从混剪/综艺/直播录像里**批量找出唱歌的片段时间点**
- 想做**卡拉OK/翻唱时间轴**、自动切歌、唱歌集锦
- 视频里同时有说话、BGM+字幕、唱歌，需要只挑出唱歌
- 需要快速预览（fast，零重依赖、纯 CPU）或高精度结果（accurate，需装 spleeter/demucs）

## Tiers / 场景分级策略

| 档位 | 依赖 | 速度（每 1h 视频，CPU） | 精度 | 适用 |
|------|------|------------------------|------|------|
| **fast** | numpy + ffmpeg（必装） | < 3 min | 粗筛（recall≈高，边界±0.5s） | 快速预览、批量粗定位、无 GPU/无模型环境 |
| **accurate** | + spleeter 或 demucs | < 15 min | 精（人声干声上判唱，边界更准） | 交付级时间戳、边界敏感场景 |

> fast 档若检测到系统已装 spleeter/demucs 但仍用 `--mode fast`，则直接在混合信号上判唱；accurate 档若未装分离工具，**自动降级为 fast 并告警**（不抛错、不中断）。

## Quick Start

```bash
cd singing-segment-detector

# 1) 生成一段合成验证音频（0-3s 说话 / 3-6s 唱歌 / 6-9s BGM）
python3 scripts/synthesize_test.py --output /tmp/test_mix.wav

# 2) fast 档检测
python3 scripts/detect_singing.py --input /tmp/test_mix.wav --output-dir /tmp/out

# 3) accurate 档（需先 pip install spleeter 或 demucs）
python3 scripts/detect_singing.py --input video.mp4 --mode accurate --separator demucs --output-dir /tmp/out2
```

输出（`--output-dir` 下）：
- `singing_timestamps.json` — `[{start, end, duration, confidence, score}]` + 汇总
- `singing_timestamps.srt` — 时间轴字幕（可直接拖进播放器看唱歌段）

## Workflow

1. **抽音频**：ffmpeg 把视频/音频统一抽成 16k mono wav（`extract_audio`）。
2. **（accurate 档）分离人声**：spleeter/demucs 抽 vocals 干声；失败则降级 fast（`separate_vocals`）。
3. **帧级特征**：逐帧算 RMS 能量、过零率、自相关基频 f0 与置信度；帧间做八度纠错+一致性约束稳定 f0（`frame_features` / `estimate_f0` / `_stabilize_f0`）。
4. **滑窗评分**：2.0s 滑窗内聚合 `voiced 占比 + 音高连续性 + voiced 时间连续性`，过零率过高（念稿清辅音）压分（`window_scores`）。
5. **后处理**：中值滤波去毛刺 → 最短时长过滤（默认 2.5s）→ 间隙合并（含「唱中夹说」双阈值切分：停顿<0.8s 且音高连续则视为换气合并；停顿内出现音高剧烈跳动则判定转说话切分）→ 边界内收收紧时间戳（`post_process`）。
6. **出文件**：写 JSON + SRT。

## Tuning（跨视频不必改代码）

所有阈值均可用命令行覆盖，例如对念稿类视频压低 voiced 占比阈值：

```bash
python3 scripts/detect_singing.py --input x.mp4 --voiced_ratio_thr 0.5 --min_duration 3.0
```

关键参数（见 `scripts/detect_singing.py` 顶部 `DEFAULTS`）：

| 参数 | 默认 | 含义 |
|------|------|------|
| `min_duration` | 2.5s | 最短唱歌段，低于则丢弃（过滤短促清唱/哼唧） |
| `merge_gap` | 1.0s | 段间间隙 < 此值则尝试合并 |
| `breathe_gap` | 0.8s | 唱中夹说：停顿 < 此值且音高连续 → 换气合并 |
| `voiced_ratio_thr` | 0.55 | 滑窗内 voiced 帧占比阈值 |
| `pitch_cont_thr` | 0.6 | 音高连续帧占比阈值 |
| `f0_conf_thr` | 0.30 | 基频置信度阈值（基频峰/总能量） |
| `energy_thr` | 0.012 | RMS 静音阈值 |
| `trim_thr` | 0.6 | 边界内收阈值（收紧时间戳） |
| `window_sec` | 2.0s | 滑窗长度 |

## Acceptance（工程验收口径）

- **召回 recall ≥ 95%**（唱歌段不漏）
- **精确 precision ≥ 92%**（报出的段主要是真唱歌，边界 ±0.5s 内可接受）
- fast 档每 1h 视频 CPU < 3min；accurate 档 < 15min
- **可复现**：相同输入 + 相同参数 → 相同输出（无随机种子依赖；合成测试用 `synthesize_test.py` 固定结构）
- **CI 回归**：`synthesize_test.py` 生成的「说话/唱歌/BGM」三段样本应稳定检出唱歌段且排除说话与 BGM（参考 references/ 里的回归口径）

## Fallbacks / 已知限制

- fast 档是**粗筛**，边界会有 ±0.5s 滑窗溢出，**交付级边界请用 accurate 档**。
- 纯规则对**多人合唱/和声（OOD）**、**说唱（节奏型念词）**、**极高噪声** 鲁棒性有限；这类灰区建议 accurate 档 + 多模态兜底（见 references/ 辩论共识文档）。
- 未装 ffmpeg 会直接报错提示安装；未装 spleeter/demucs 时 accurate 自动降级 fast。

## Resources

### scripts/
- `detect_singing.py` — 主检测脚本（fast/accurate 双档、全参数可覆盖、输出 JSON+SRT）。
- `synthesize_test.py` — 生成三段式验证音频（说话/唱歌/BGM），用于本地回归与 demo。

### references/
- `debate_consensus.md` — 五轮三方技术辩论共识：问题定义、三套候选方案（纯信号/分离+模型/混合多模态）、盲点深化（性能边界、数据漂移、可复现、唱中夹说切分、多人/OOD、最终工程验收清单与场景分级表）。本 skill 的架构与验收口径源自此文档。
- `full_debate.md` — 五轮辩论完整原文（R1–R5），含 A/B/C 三人逐轮方案与互相批评，供追溯方法论来源。
