#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补齐归档:对缺失的文件用 URL 编码重新下载"""
import json, os, time, urllib.request, urllib.error, urllib.parse
from datetime import date

TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
if not TOKEN:
    print("请设置环境变量 GITHUB_TOKEN 后运行(需 repo 权限)")
    print("示例: GITHUB_TOKEN=ghp_xxx python backfill_archive.py")
    raise SystemExit(1)
API = "https://api.github.com"
BASE = "C:/Users/260531/WorkBuddy/2026-08-01-10-29-28"
MANIFEST = f"{BASE}/_docs_manifest.json"
ARCHIVE = f"{BASE}/hub-world/docs/archive"
TODAY = date.today().isoformat()

def api_get(repo, path, branch):
    url = f"{API}/repos/Simiely/{repo}/contents/{urllib.parse.quote(path)}?ref={branch}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Accept", "application/vnd.github.raw")
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

def add_fm(repo, branch, path, content):
    title = os.path.basename(path)
    if content.startswith("---"):
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
    added = 0
    for entry in manifest:
        repo, branch = entry["name"], entry["branch"]
        files = []
        if entry["readme"]:
            files.append(entry["readme"])
        for d in entry["docs"]:
            if d != entry["readme"] and d not in files:
                files.append(d)
        for f in files:
            dest = os.path.join(ARCHIVE, repo, f.replace("/", os.sep))
            if os.path.exists(dest):
                continue  # 已存在跳过
            raw = api_get(repo, f, branch)
            if raw is None:
                print(f"[FAIL] {repo}/{f}")
                continue
            text = raw.decode("utf-8", errors="replace")
            text = add_fm(repo, branch, f, text)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
            added += 1
            print(f"[OK] {repo}/{f}")
            time.sleep(0.2)
    print(f"\n补齐完成,新增 {added} 个文件")

if __name__ == "__main__":
    main()
