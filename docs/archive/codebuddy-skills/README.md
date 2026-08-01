---
module: archive
title: README.md
tags: [codebuddy-skills]
source:
  project: codebuddy-skills
  repo: https://github.com/Simiely/codebuddy-skills
  file: README.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/codebuddy-skills/blob/main/README.md)

# codebuddy-skills

个人维护的 **CodeBuddy / WorkBuddy 技能（Skill）集合仓库**。每个技能是一个独立、可单独打包的目录，遵循 CodeBuddy skill 规范（`SKILL.md` + `scripts/` + `references/`）。

> 设计目标：可扩展。后续新增技能按相同结构追加为**顶层目录**，CI/脚本可遍历含 `SKILL.md` 的目录批量校验与打包。

## 仓库结构

```
codebuddy-skills/
├── README.md                      # 本文件：项目介绍 + 使用
├── DEVELOPMENT.md                # 开发流程 + 关键踩坑记录（重要参考）
└── <skill-name>/                # 每个技能一个顶层目录
    ├── SKILL.md                  # 技能元数据 + 工作流（YAML frontmatter）
    ├── scripts/                  # 可直接执行的脚本
    └── references/               # 参考资料（按需加载进上下文）
```

## 已收录技能

| 技能 | 说明 | 档位 |
|------|------|------|
| [`singing-segment-detector`](./singing-segment-detector) | 从含「谈话 / 背景音+字幕 / 唱歌」的混合视频或音频中，提取**所有唱歌片段的时间戳**（JSON + SRT，带置信度） | fast（零重依赖）/ accurate（人声分离+模型） |

## 使用方法

两种方式，任选其一：

**方式 A：直接用源码目录**
将仓库里某个 `<skill-name>/` 整个目录，复制到你的技能加载目录（CodeBuddy 的 skills 目录）即可，无需解包。

**方式 B：用打包好的 `.skill`**
对技能目录运行打包脚本生成 `.skill`（本质是 zip），再导入：

```bash
# 校验
python3 <skill-creator>/scripts/quick_validate.py singing-segment-detector
# 打包
python3 <skill-creator>/scripts/package_skill.py singing-segment-detector
# 产物：singing-segment-detector.skill
```

导入后，用自然语言描述需求即可触发，例如：
> "从这段视频里找出所有唱歌的时间戳"

## 快速验证（以 singing-segment-detector 为例）

```bash
cd singing-segment-detector
python3 scripts/synthesize_test.py --output /tmp/test_mix.wav   # 生成三段式验证音频
python3 scripts/detect_singing.py --input /tmp/test_mix.wav --output-dir /tmp/out
# 输出 /tmp/out/singing_timestamps.json + .srt
```

## 新增一个技能

参见 [`DEVELOPMENT.md`](./DEVELOPMENT.md) 的「开发一个新技能」一节——包含初始化、SKILL.md 规范、校验、打包，以及本次开发中记录的关键问题与坑。
