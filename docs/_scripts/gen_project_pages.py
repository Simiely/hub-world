#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量生成 35 个项目卡片页(基于 manifest 数据)"""
import json, os
from datetime import date

BASE = "C:/Users/260531/WorkBuddy/2026-08-01-10-29-28"
MANIFEST = f"{BASE}/_docs_manifest.json"
OUT = f"{BASE}/hub-world/docs/projects"
TODAY = date.today().isoformat()

# 中文名 / 分类 / 一句话描述补充
META = {
    "homekeeper": ("homekeeper", "拾光集 · 家居物品管理", "Python 后端", "FastAPI+SQLite+JWT+Web Push"),
    "obsidian-agent": ("obsidian-agent", "Obsidian AI 助手", "Python 后端", "FastAPI+Vue3+SQLite FTS5+Pydantic AI"),
    "learning-platform": ("learning-platform", "幼儿闪卡平台 Lets Learn", "Python 后端", "Django+Alpine.js"),
    "codebuddy-skills": ("codebuddy-skills", "CodeBuddy/WorkBuddy 技能集合", "Python 工具", "SKILL.md 规范"),
    "blender-car-mesh-optimizer": ("blender-car-mesh-optimizer", "车模网格优化插件", "设计插件", "Blender 单文件插件"),
    "android-adskip": ("android-adskip", "广告跳过工具 AdSkip", "Android", "Kotlin 无障碍服务"),
    "DarkMask": ("DarkMask", "夜深模式 · 全屏降亮", "Android", "Kotlin 前台服务"),
    "collab-plan-miniprogram": ("collab-plan-miniprogram", "协作计划小程序 🔒", "微信小程序", "云开发+增量同步"),
    "potty-training-miniprogram": ("potty-training-miniprogram", "宝宝如厕训练助手", "微信小程序", "本地+云双模式"),
    "miniprogram-item-expiry": ("miniprogram-item-expiry", "物品有效期小程序", "微信小程序", "云开发+腾讯文档同步"),
    "WindowTinter": ("WindowTinter", "窗口透明工具 暗幕", "桌面工具", "C# .NET 6"),
    "resources": ("resources", "软件资源库 🔒", "桌面/网页", "HTML+Python 生成器"),
    "AE-Lyrics-Animator": ("AE-Lyrics-Animator", "AE 歌词逐字动画", "设计插件", "ExtendScript"),
    "AudioScale": ("AudioScale", "AE 音频驱动缩放", "设计插件", "ExtendScript"),
    "CircleDiffusion": ("CircleDiffusion", "AE 圆形扩散生成器", "设计插件", "ExtendScript"),
    "starry-sky-generator": ("starry-sky-generator", "AE 星空粒子生成器", "设计插件", "ExtendScript"),
    "c4d-mesh-face-sorter": ("c4d-mesh-face-sorter", "C4D 网格面数排序", "设计插件", "C4D Python"),
    "c4d-userdata-manager": ("c4d-userdata-manager", "C4D 用户数据管理", "设计插件", "C4D Python"),
    "oc-plugin-activator": ("oc-plugin-activator", "OC 插件快速激活工具", "设计插件", "Windows 工具"),
    "blender-mesh-face-sorter": ("blender-mesh-face-sorter", "Blender 网格面数排序", "设计插件", "Blender Python"),
    "vray-material-replacer": ("vray-material-replacer", "3ds Max V-Ray 材质工具箱", "设计插件", "MaxScript"),
    "car-model-decimation": ("car-model-decimation", "车模减面 · 逆向优化工作流", "设计文档", "HTML 技术文档"),
    "TopoGun3-Chinese-Localization": ("TopoGun3-Chinese-Localization", "TopoGun3 简体中文汉化包", "本地化", "GLSL 语言包"),
    "carselection": ("carselection", "汽车选择工具", "网页/工具", "JavaScript"),
    "hub-world": ("hub-world", "项目导航中心(本仓库)", "导航/文档", "HTML+JSON"),
    "windows-ltsc-guide": ("windows-ltsc-guide", "Windows LTSC 选购指南", "网页指南", "HTML"),
    "ntlite-windows-guide-2": ("ntlite-windows-guide-2", "NTLite 精简 Windows 指南", "网页指南", "HTML"),
    "vmware-install-guide": ("vmware-install-guide", "VMware 虚拟机安装教程", "网页指南", "HTML"),
    "meituan-bike-reminder": ("meituan-bike-reminder", "美团骑车锁车提醒", "网页/工具", "HTML"),
    "baby-hair-braiding-guide": ("baby-hair-braiding-guide", "宝宝扎辫子指南", "网页指南", "HTML"),
    "edge-multi-account-cookie": ("edge-multi-account-cookie", "Edge 多账号 Cookie 切换", "网页/工具", "HTML"),
    "ExplorerBlurMica-whitebar-fix": ("ExplorerBlurMica-whitebar-fix", "资源管理器白条修复", "网页/工具", "HTML+脚本"),
    "windows-explorer-refresh-fix": ("windows-explorer-refresh-fix", "资源管理器刷新修复", "网页/工具", "HTML+脚本"),
    "travel-1.0": ("travel-1.0", "琅勃拉邦旅行规划", "网页指南", "HTML"),
}

def module_links(repo):
    """根据项目类型推荐相关模块链接"""
    links = []
    links.append("[M1 部署](../modules/M1-部署与快速上手.md)")
    links.append("[M2 架构](../modules/M2-架构与设计.md)")
    links.append("[M4 开发指南](../modules/M4-开发指南/README.md)")
    return " · ".join(links)

def main():
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    created = 0
    for entry in manifest:
        repo = entry["name"]
        if repo not in META:
            # 未登记元数据的项目也生成基础卡片
            name, cn, cat, stack = repo, repo, "其他", entry.get("language") or "?"
        else:
            name, cn, cat, stack = META[repo]
        priv = " 🔒" if entry["private"] else ""
        desc = (entry.get("description") or "").strip() or "暂无描述"
        # 文档入口
        doc_entries = []
        if entry["readme"]:
            doc_entries.append(f"- [README]({rel_archive(repo, entry['readme'])})")
        for d in entry["docs"]:
            if d != entry["readme"]:
                doc_entries.append(f"- [{d}]({rel_archive(repo, d)})")
        docs_block = "\n".join(doc_entries) if doc_entries else "- 暂无独立文档,详见仓库 README"
        content = f"""---
module: project
title: {repo} - {cn}
tags: [{cat}, {entry.get('language') or 'other'}]
project:
  name: {repo}
  repo: https://github.com/Simiely/{repo}
  private: {str(entry['private']).lower()}
  language: {entry.get('language') or '?'}
  branch: {entry['branch']}
  description: {desc}
  synced_at: {TODAY}
---

# {repo} · {cn}

## 项目简介

{desc}

## 快速信息

| 项 | 值 |
|---|---|
| 语言 | {entry.get('language') or '?'} |
| 可见性 | {'🔒 私有' if entry['private'] else '公开'} |
| 默认分支 | {entry['branch']} |
| GitHub | [Simiely/{repo}](https://github.com/Simiely/{repo}) |

## 文档入口(归档快照)

{docs_block}

## 相关模块

{module_links(repo)}

---

[← 返回项目索引](README.md) · [← 返回文档中心](../README.md)
"""
        path = os.path.join(OUT, f"{repo}.md")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        created += 1
        print(f"[OK] {repo}")
    print(f"\n共生成 {created} 个卡片页")

def rel_archive(repo, path):
    # archive 路径是 docs/archive/<repo>/<path>
    from urllib.parse import quote
    parts = path.split("/")
    quoted = "/".join(quote(p) for p in parts)
    return f"../archive/{repo}/{quoted}"

if __name__ == "__main__":
    main()
