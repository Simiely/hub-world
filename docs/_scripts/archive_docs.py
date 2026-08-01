#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整搬运 Simiely 各仓库文档到 hub-world/docs/archive/,自动加来源 frontmatter"""
import json, os, re, time, urllib.request, urllib.error
from datetime import date

TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
if not TOKEN:
    print("请设置环境变量 GITHUB_TOKEN 后运行(需 repo 权限)")
    print("示例: GITHUB_TOKEN=ghp_xxx python archive_docs.py")
    raise SystemExit(1)
API = "https://api.github.com"
BASE = "C:/Users/260531/WorkBuddy/2026-08-01-10-29-28"
MANIFEST = f"{BASE}/_docs_manifest.json"
ARCHIVE = f"{BASE}/hub-world/docs/archive"
TODAY = date.today().isoformat()

# 排除清单:不需要搬运的文件
SKIP = {
    ".workbuddy/memory/2026-07-26.md",  # 本地记忆文件,不属于项目文档
}

def api_get(url, raw=False):
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Accept", "application/vnd.github.raw" if raw else "application/vnd.github+json")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                time.sleep(5); continue
            return None
        except Exception:
            time.sleep(3)
    return None

def add_frontmatter(repo, branch, path, content):
    """为搬运的文档添加来源 frontmatter"""
    title = os.path.basename(path)
    if content.startswith("---"):
        # 已有 frontmatter:在结尾补 source 字段
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm, body = parts[1], "---" + parts[2]
            return f"---{fm}\nsource:\n  project: {repo}\n  repo: https://github.com/Simiely/{repo}\n  file: {path}\n  branch: {branch}\n  synced_at: {TODAY}\n---{body}"
    fm = (
        "---\n"
        f"module: archive\n"
        f"title: {title}\n"
        f"tags: [{repo}]\n"
        "source:\n"
        f"  project: {repo}\n"
        f"  repo: https://github.com/Simiely/{repo}\n"
        f"  file: {path}\n"
        f"  branch: {branch}\n"
        f"  synced_at: {TODAY}\n"
        "---\n\n"
    )
    return fm + content

def main():
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    total_files = 0
    for entry in manifest:
        repo, branch = entry["name"], entry["branch"]
        files = []
        if entry["readme"]:
            files.append(entry["readme"])
        for d in entry["docs"]:
            if d != entry["readme"] and d not in files and d not in SKIP:
                files.append(d)
        if not files:
            print(f"[-] {repo}: 无文档")
            continue
        repo_dir = os.path.join(ARCHIVE, repo)
        os.makedirs(repo_dir, exist_ok=True)
        for f in files:
            # 处理目录中的文件名,保留子目录结构
            rel = f
            dest = os.path.join(repo_dir, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            url = f"{API}/repos/Simiely/{repo}/contents/{f}?ref={branch}"
            raw = api_get(url, raw=True)
            if raw is None:
                print(f"[FAIL] {repo}/{f}")
                continue
            text = raw.decode("utf-8", errors="replace")
            text = add_frontmatter(repo, branch, f, text)
            with open(dest, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
            total_files += 1
            print(f"[OK] {repo}/{f}")
            time.sleep(0.2)
    print(f"\n搬运完成,共 {total_files} 个文件")

if __name__ == "__main__":
    main()
