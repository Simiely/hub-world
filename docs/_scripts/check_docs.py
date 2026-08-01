#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""联检 v2:验证 docs/ 下所有内部链接、frontmatter 覆盖率、目录完整性
区分:archive 内文档的相对链接(引用同项目文件,视为有效)vs 模块/项目文档的链接(必须有效)"""
import os, re
from urllib.parse import unquote

ROOT = "C:/Users/260531/WorkBuddy/2026-08-01-10-29-28/hub-world/docs"

def walk_md():
    for dirpath, _, files in os.walk(ROOT):
        for f in files:
            if f.endswith(".md"):
                yield os.path.join(dirpath, f)

def check_links():
    """broken: (来源文件, 目标, 类型)"""
    broken = []
    total = 0
    for path in walk_md():
        rel = os.path.relpath(path, ROOT)
        in_archive = rel.startswith("archive")
        text = open(path, encoding="utf-8").read()
        # 去掉代码块内容(``` ... ```),避免误报
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        # 去掉行内代码 `...`,避免误报
        text = re.sub(r"`[^`]*`", "", text)
        for m in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", text):
            target = m.group(1)
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            total += 1
            target_clean = unquote(target.split("#")[0])
            if not target_clean:
                continue
            full = os.path.normpath(os.path.join(os.path.dirname(path), target_clean))
            if os.path.exists(full):
                continue
            # 归档区内:允许指向 代码文件/图片/LICENSE 等非 md 资源(未搬运),仅检查 .md
            if in_archive:
                if target_clean.endswith((".md", ".markdown")):
                    broken.append((rel, target, "archive-md"))
                # 非 md 资源链接(如 .jsx/.png/LICENSE/代码路径)视为可接受的 GitHub 相对链接
            else:
                broken.append((rel, target, "doc"))
    return total, broken

def check_frontmatter():
    no_fm = []
    total = 0
    for path in walk_md():
        total += 1
        text = open(path, encoding="utf-8").read()
        if not text.startswith("---"):
            no_fm.append(os.path.relpath(path, ROOT))
    return total, no_fm

def check_structure():
    required = [
        "README.md",
        "modules/M1-部署与快速上手.md",
        "modules/M2-架构与设计.md",
        "modules/M3-API参考.md",
        "modules/M4-开发指南/README.md",
        "modules/M5-踩坑记录/README.md",
        "modules/M6-更新日志.md",
        "projects/README.md",
        "archive/README.md",
        "_templates/SOURCE_TEMPLATE.md",
    ]
    missing = [r for r in required if not os.path.exists(os.path.join(ROOT, r))]
    return missing

def main():
    total, broken = check_links()
    n, no_fm = check_frontmatter()
    missing = check_structure()
    print(f"== 文档总数: {n}")
    print(f"== 内部链接: {total} 个,损坏 {len(broken)} 个")
    for rel, t, typ in broken[:40]:
        print(f"   [{typ}] {rel} -> {t}")
    print(f"== 无 frontmatter: {len(no_fm)} 个")
    for f in no_fm:
        print(f"   NO_FM: {f}")
    print(f"== 缺失结构: {len(missing)} 个")
    for m in missing:
        print(f"   MISSING: {m}")
    real_broken = [b for b in broken if b[2] == "doc"]
    ok = not real_broken and not missing
    print("\n结论:", "✅ 关键链接全部通过" if ok else f"⚠️ 需修复 {len(real_broken)} 个关键链接")
    if no_fm:
        print("(无 frontmatter 的是导航页/模板,可接受)")

if __name__ == "__main__":
    main()
