---
module: archive
title: TODO.md
tags: [learning-platform]
source:
  project: learning-platform
  repo: https://github.com/Simiely/learning-platform
  file: TODO.md
  branch: master
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/learning-platform/blob/master/TODO.md)

# TODO — 动物闪卡平台后续工作

> 本文件用于跨设备 / 跨 AI 会话接力。代码、迁移、媒体素材、文档均已推送至 `master`，
> 换电脑 `git clone` 即可获得完整可运行状态。下面是需要**继续推进**的事项和**已定决策**。

## 〇、文档索引（维护时先看这里）

| 想干什么 | 看哪个文档 |
|---------|-----------|
| 了解项目整体架构 / 数据模型 / 路由 | `DEVELOPER.md` |
| 新增一只动物（完整流程） | `ADD_ANIMALS_GUIDE.md` |
| 查动物数据总表（77 只、焦点、批次） | `ANIMALS.md` |
| 排错 / 踩坑记录（Safari/iPad/音频/Docker） | `DEV.md` |
| 待办与已定决策 | 本文档 |
| 项目门面 / 快速上手 | `README.md` |

## 一、待做清单

### A. 服务器实际部署（核心，尚未真做）
代码已上库，但 `db.sqlite3` 故意不入库（见 `.gitignore`）。部署时靠种子脚本确定性重建数据：
```bash
pip install -r requirements.txt
python manage.py migrate            # 应用迁移 0013，建立 Category.groups / Item.group 放开
python manage.py seed_sync          # 非破坏性同步（推荐，部署链路用这个）
python manage.py seed_data --force  # 或全量重建（会清空旧数据，仅首启/测试用）
python manage.py check_data         # 校验 DB / 媒体 / apps/core/data/ 三方一致
python manage.py collectstatic      # 用 gunicorn 生产部署时需要
```
执行后状态 = 本地当前状态（**7 分类 183 条**、每分类分组齐全、动物有图 + 全平台三语音频）。
> Docker 部署链路（docker-entrypoint.sh）已自动执行 `seed_sync` + `check_data`，无需手动。

### B. ALLOWED_HOSTS 补域名 ⚠️
`config/settings.py` 目前只含 `127.0.0.1`。部署到真实服务器前，必须通过环境变量或配置把
服务器域名 / IP 加入 `ALLOWED_HOSTS`，否则 Django 拒访。

### C. 图片焦点校准
第3~7批动物焦点已校准。如需微调，改
`apps/core/data/animals.py` 对应 `Animal` 的焦点字段（image_position / image_position_ipad_portrait /
image_position_ipad_landscape），再跑 `python manage.py sync_positions`（只同步焦点，不碰其他字段）。
焦点约定见 `DEVELOPER.md`。

### D. 后续分类/条目批次
- ✅ **动物第1~7批共 77 只已全部上线**（详见 `ANIMALS.md`）。
- ✅ **果蔬 23 种**（2026-07-31，`data/fruits.py`，emoji 图片）
- ✅ **交通工具 20 / 恐龙 16 / 太空 15 / 花卉植物 16 / 职业 16**（2026-07-31，`data/vehicles|dinosaurs|space|plants|jobs.py`，emoji 图片）
- ⏳ **补真实图片**：以上 6 个新分类后续逐个补真实照片（流程：Pexels 搜图 → 用户确认 → 填 img_file → seed_sync）
- 音频生成工具 `gen_audio.py`（仓库根目录）从 `apps/core/data/` 读取，**必须带 `--category <slug>`** 只生成新增分类，勿全量跑（会覆盖已有音频，曾致 cat/whale 损坏）。
- 图片下载工具 `download_unsplash.py`（仓库根目录）用于获取候选参考图。

### E. 本地预览服务（验证完可停）
开发期后台 dev server 在 `http://127.0.0.1:8000`，确认效果后可停止。

## 二、已定决策（无需再问，直接照做）

1. **Emoji 规则**：动物有专属 emoji 用自己；**没有专属 emoji 的统一用 `⬛` 黑色占位方块**。
   - 实例：海马、鸵鸟、河狸（无专属 emoji）→ ⬛
   - 有专属 emoji 的维持不变：蚂蚁🐜、瓢虫🐞、蜗牛🐌、刺猬🦔、仓鼠🐹、海龟🐢、章鱼🐙、海狮🦭 等。
   - `emoji_color()` 对 ⬛ 特殊处理：中间色 `#3C3C3C` → 加深后得 `#121212`（2026-07-31 定）。
2. **图片不裁正方形**：`media/images/` 现有图均为长方形，App 用 `object-fit: cover` + 焦点适配。
   高清图原样搬入即可（长边 ≥ 3000px）。
3. **媒体文件命名**：图片/音频用简单英文名做基名（如 `ant.jpg` / `ant.mp3`），
   须与 `apps/core/data/` 中该条目的 `img_file` / `audio_file` 基名一致。
4. **批次结构**：第1~7批共 77 只已上线（详见 `ANIMALS.md`）。
5. **依赖版本**：`requirements.txt` 已统一为本地运行环境版本（Django 6.0.7 等），部署照此安装。
6. **图片大小控制（2026-07-31 更新）**：原"原图直出不压缩"已调整——**超过 4MB 的图片需压缩到 4MB 以内**（不降分辨率）。
   已用 **mozjpeg cjpeg** 处理 15 张 >4MB 动物图（88.2MB → 51.4MB，quality 62~98，分辨率不变）。
   后续新增/更换图片若 >4MB，同样用 mozjpeg 压到 4MB 内（工具：`node_modules/mozjpeg/vendor/cjpeg.exe`，
   流程：Pillow 解码 → PPM 临时文件 → cjpeg 二分 quality → 原子替换；**Windows 下勿用 cjpeg 的 stdin/stdout**）。
   压缩不影响 DB（文件名不变），无需重新 seed。
7. **数据单一来源（多分类）**：`apps/core/data/` 目录是全部条目数据的唯一来源——
   `__init__.py`（CATEGORIES 汇总 + CardItem dataclass）+ 每分类一个数据文件（animals.py / fruits.py）。
   seed_data / seed_sync / sync_positions / check_data / gen_audio 全部从 CATEGORIES 读取。
8. **新分类图片用 emoji 代替**（2026-07-31 定）：暂不找图时 `img_file` 留空字符串即可，
   前端自动显示 emoji，后续补真实图只需填文件名 + 重新 seed_sync。
9. **gen_audio 必须 --category**（2026-07-31 定）：生成音频只跑
   `python gen_audio.py --category <slug>`；无参数全量会覆盖已有音频且中途失败留 0 字节损坏文件。
10. **Quiz 出题去重（时间正向）**（2026-07-31 定）：一轮 10 题正确答案互不重复（correct 池排除
    本轮已出答案 + 上轮答案）；已出答案不再混入后续题选项（干扰项池排除 used + prev）。
    干扰项允许跨题复用（10 题 × 4 选项 = 40 位置 > 最少分类 15 条的物理限制）。
11. **分组标签 icon/text 拆分**（2026-07-31 定）：`Category.groups` 的 label 格式为 `"emoji 文字"`，
    视图用 `label.partition(" ")` 拆成 icon + 文字（模板 gt-count=icon / gt-label=文字）。
    不要在模板里 `slice:":1"` 切 emoji（会切坏 ZWJ 组合 emoji，如 👨⚕️）。
12. **首页查询用 annotate**（2026-07-31 定）：`Category.objects.annotate(item_count=Count("items"))`
    在 SQL 层一次算完（8 次 → 1 次查询）；模板直接渲染 `cat.item_count`。

## 二五、最近完成（2026-07-31 大版本）
- ✅ **7 分类 183 条上线**：动物 77 / 果蔬 23 / 交通工具 20 / 恐龙 16 / 太空 15 / 花卉植物 16 / 职业 16
- ✅ **模块化架构**：`data/` 目录多分类（CardItem 统一 11 字段）、命令/视图/模板/JS 全动态、30+ 测试
- ✅ **代码审查与修复**：rocket 音频冲突、quiz_submit 500、quiz 题目去重、iPad 分组标签 emoji 重复、
  seed_sync 媒体回填解绑、死代码清理（quiz_type / item_detail_api / 冗余属性 / 兼容别名）
- ✅ **README / DEVELOPER / ADD_ANIMALS_GUIDE / DEV / TODO 全部与最新代码同步**

## 三、需要你（用户）提供的密钥 / 凭据

以下密钥**刻意不入库**（安全），新环境需由用户通过环境变量提供给 AI：

| 用途 | 环境变量 | 说明 |
|------|---------|------|
| 参考图搜索 | `UNSPLASH_ACCESS_KEY` | `download_unsplash.py` 调用 Unsplash API 搜图 |
| 参考图搜索 | `PEXELS_KEY` | 备用图源（Pexels API 搜图 + CDN 下载） |
| 网络代理（可选） | `HTTPS_PROXY` / `HTTP_PROXY` | 两个搜图脚本自动读取；未设置则直连 |
| 代码仓库 | GitHub PAT | 推送到 `Simiely/learning-platform` 用；推送 URL 格式为
  `https://x-access-token:<PAT>@github.com/...`（用户名固定 `x-access-token`） |

> 音频生成用 edge-tts（微软免费服务），**无需密钥**，但所在环境需能访问外网（必要时走代理）。

## 四、跨设备接力提示

- 本仓库**不含** `db.sqlite3`、`venv/`、本地 `new-animals/` 临时目录、用户级记忆里的密钥。
- `gen_audio.py` 与 `download_unsplash.py` 已入库，换电脑可直接调用。
- 若推送时遇 `github.com:443` 超时：多为 git 代理配置问题，确认代理可用后
  用 `git -c http.https://github.com.proxy=<代理地址> push ...` 显式指定。
