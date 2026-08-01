---
module: archive
title: ADD_ANIMALS_GUIDE.md
tags: [learning-platform]
source:
  project: learning-platform
  repo: https://github.com/Simiely/learning-platform
  file: ADD_ANIMALS_GUIDE.md
  branch: master
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/learning-platform/blob/master/ADD_ANIMALS_GUIDE.md)

# 增加新动物操作指南 / How to Add New Animals

> 适用项目：learning-platform（Django + Alpine.js 幼儿认知闪卡平台）
> 最后更新：2026-07-31（适配模块化重构：数据源改为 apps/core/data/）
>
> 📚 **相关文档**：动物总表见 [`ANIMALS.md`](./ANIMALS.md)；架构/数据模型见 [`DEVELOPER.md`](./DEVELOPER.md)；
> 踩坑记录见 [`DEV.md`](./DEV.md)；待办决策见 [`TODO.md`](./TODO.md)

---

## 📋 完整工作流程概览（重要，请按此顺序执行）

添加新动物分为 **4 个阶段**，必须严格按以下顺序执行：

```
Phase 1 ── 确定动物清单
              │
              ▼
Phase 2 ── 逐只搜索确认图片（串行：一只一只来，所有大图确认完才到下一阶段）
              │
              ▼
Phase 3 ── 批量入库（修改 apps/core/data/ + 生成音频 + seed_sync）
              │
              ▼
Phase 4 ── 手工校准 3 种模式的图片焦点
```

---

## Phase 1：确定动物清单

1. 从 `ANIMALS.md` 的「建议新增动物」或新批次规划中确定本次要添加的动物列表
2. 明确每只动物的：中文名、英文名、Emoji、分组、科普知识

---

## Phase 2：逐只搜索确认图片（串行，核心环节）

**一次只处理一只动物，串行执行。**

对清单中的每一只动物：

1. 用 **Pexels 官方 API**（首选）搜索该动物，下载约 20 张小图到素材目录
2. **通知用户文件夹路径**，由用户自行浏览挑选
3. 用户选中一张 → 下载高清原图（长边 ≥ 3000px），该动物图片确认完成
4. 用户觉得都不满意 → 再搜 20 张小图供选择
5. 确认后才进入 **下一只动物** 的图片搜索

> ⚠️ **关键规则**：所有动物的高清大图都确认完成后，才能进入 Phase 3。

### 素材存放规则

```
new-animals/
├── seaturtle.jpeg       ← 高清原图（选定的最终图片，直接放在根目录）
├── octopus.jpeg
├── ...
└── references/          ← 候选缩略图（找图阶段用，选定后清理）
    ├── seaturtle/       ← 每只动物一个子目录
    ├── octopus/
    └── ...
```

---

## Phase 3：批量入库

### 全部大图确认后，统一执行以下操作：

#### 步骤 1：修改 `apps/core/data/` ⭐（单一数据源）

打开 `apps/core/data/`，在 `ANIMALS` 列表末尾添加新动物 `Animal(...)` 实例。
**只需改这一个文件**——`seed_data.py` / `seed_sync.py` / `sync_positions.py` / `gen_audio.py`
都会自动从它读取，无需同步修改。

**Animal dataclass 格式**（11 个字段）：

```python
Animal(
    '中文名',                  # name
    '动物名_20260731XX',       # code — 格式：英文小写_日期+序号
    'English Name',           # english_name
    '🐱',                     # emoji（没有专属 emoji 的用 '⬛'）
    'animal.{ext}',           # img_file — 图片文件名（原图格式）
    'animal.mp3',             # audio_file — 音频文件名（三个目录共用）
    '科普知识文字...',          # fact — 1-2 句科普
    '50% 50%',                # image_position — iPhone 竖屏焦点（先设默认，Phase 4 校准）
    '50% 50%',                # image_position_ipad_portrait — iPad 竖屏焦点（先设默认）
    '50% 50%',                # image_position_ipad_landscape — iPad 横屏焦点（先设默认）
    'wild',                   # group — 浏览分组（必填）
),
```

**group 字段可选值**：

| 值 | 显示名称 | 含义 | 示例动物 |
|----|---------|------|---------|
| `farm` | 🏠 家里和农场 | 家养/农场动物，孩子日常能接触的 | 狗、猫、马、牛、羊 |
| `wild` | 🌍 野生动物 | 在动物园或自然中看到的动物 | 狮子、老虎、大象、熊猫 |
| `ocean` | 🌊 海洋动物 | 生活在海洋环境中的动物 | 海豚、鲸鱼、鲨鱼、企鹅 |
| `reptile` | 🦎 爬虫和昆虫 | 小型爬行动物和昆虫 | 蛇、鳄鱼、青蛙、蝴蝶 |

**Code 编号规则**：

| 批次 | 日期 | Code 范围 | 动物数量 |
|------|------|-----------|---------|
| 第1批 | 2026-07-23 | `{name}_2026072301` ~ `_2026072321` | 21 |
| 第2批 | 2026-07-24 | `{name}_2026072401` ~ `_2026072420` | 20 |
| 第3批 | 2026-07-29 | `{name}_2026072901` ~ `_2026072912` | 12 |
| 第4批 | 2026-07-29 | `{name}_2026072913` | 1（鹿） |
| 第5批 | 2026-07-29 | `{name}_2026072914` ~ `_2026072920` | 7 |
| 第6批 | 2026-07-30 | `{name}_2026073001` ~ `_2026073006` | 6 |
| 第7批 | 2026-07-31 | `{name}_2026073101` ~ `_2026073110` | 10 |
| 新增 | **当天日期** | `{name}_当天日期XX`（从 01 开始） | 新批次 |

#### 步骤 2：将高清图片放入 `media/images/`

```bash
cp new-animals/{animal}.jpg media/images/{animal}.jpg
```

- **原图格式直出**，不转换格式、不缩放裁剪（jpg / png / webp 等均可）
- **长边 ≥ 3000px**
- **⚠️ 文件大小 ≤ 4MB**：超过 4MB 需用 mozjpeg 压到 4MB 以内（**不降分辨率**，流程见
  `TODO.md` 决策 6：Pillow 解码 → PPM 临时文件 → `cjpeg -quality Q -optimize` 二分 → 原子替换）
- 图片文件名与 `apps/core/data/` 中 `img_file` 字段保持一致

#### 步骤 3：生成音频（3 种语言）

中文、英文、科普三个音频，文件名相同仅目录不同。推荐直接用仓库根目录的 `gen_audio.py`
（从 apps/core/data/ 自动读取全部条目；必须用 `--category <slug>` 限定分类，勿全量跑）：

```bash
python gen_audio.py --category animals   # 只生成动物分类音频（新增动物时）
python gen_audio.py --category fruits    # 只生成果蔬分类音频
python gen_audio.py --category animals goat  # 只生成动物分类下的指定基名
```

单只手工生成（命令示例）：

```bash
# 中文发音（仅动物名）
edge-tts --voice zh-CN-XiaoxiaoNeural --text "水母" --write-media media/audio/jellyfish.mp3

# 英文发音（仅动物名）
edge-tts --voice en-US-JennyNeural --text "Jellyfish" --write-media media/audio_en/jellyfish.mp3

# 科普发音（全文朗读）
edge-tts --voice zh-CN-XiaoxiaoNeural --text "水母没有大脑、没有心脏、没有血液..." --write-media media/audio_fact/jellyfish.mp3
```

> 三个文件名必须完全一致，仅目录不同

#### 步骤 4：运行种子命令

```bash
# 本地/测试环境（全量重建，会清空旧数据）
python manage.py seed_data --force

# 生产/Docker 环境（推荐，非破坏性增量同步）
python manage.py seed_sync

# 校验数据一致性（媒体文件 + DB + data/ 对齐）
python manage.py check_data
```

#### 步骤 5：更新 `ANIMALS.md`

添加新批次表格，更新快速筛选表中的批次和总数（注意：ANIMALS.md 是 apps/core/data/ 的展示版，
两者需保持一致）。

---

## Phase 4：手工校准图片焦点

所有数据入库后，**用户手动**调整 3 种模式的图片中心：

| 焦点字段 | 对应设备 | 说明 |
|---------|---------|------|
| `image_position` | **iPhone 竖屏** | 手机竖屏时的显示焦点 |
| `image_position_ipad_portrait` | **iPad 竖屏** | iPad 竖屏时的显示焦点 |
| `image_position_ipad_landscape` | **iPad 横屏** | iPad 横屏时的显示焦点 |

### 校准原则

1. **焦点对准头部/面部** — 动物的眼睛或脸部是视觉中心
2. **iPhone 焦点** — 通常是动物头部位置
3. **iPad 竖屏** — 画面更宽，动物位置可能需要左右调整
4. **iPad 横屏** — 画面最宽，动物可能偏左或偏右，需要大幅调整
5. **纵向补偿** — `centerPos()` 函数会自动对纵向做 ×0.65 上偏补偿
6. **有效范围**：5%~95% 之间

> ⚠️ **已有动物的图片焦点已手工校准，禁止擅自修改**

---

## 文件清单速查

修改/新增的文件：

```
需要修改:
  apps/core/data/                             ← ⭐ ANIMALS 列表加 Animal 实例（唯一数据源）
  ANIMALS.md                                     ← 文档更新（展示表，与 apps/core/data/ 保持一致）

需要新增（每只动物）:
  media/images/{animal}.jpg                      ← 图片
  media/audio/{animal}.mp3                       ← 中文音频
  media/audio_en/{animal}.mp3                    ← 英文音频
  media/audio_fact/{animal}.mp3                  ← 科普音频
```

**无需修改的文件**（系统自动适配）：

```
  apps/core/management/commands/seed_data.py    — 自动从 apps/core/data/ 读取
  apps/core/management/commands/seed_sync.py    — 自动从 apps/core/data/ 读取
  apps/core/management/commands/sync_positions.py — 自动从 apps/core/data/ 读取
  apps/core/models.py           — Item 模型已有完整字段
  apps/core/views.py            — 视图自动从 DB 加载所有 Item
  templates/*.html              — 模板自动渲染所有 Item
  static/js/*.js                — JS 逻辑与数据量无关
  static/css/*.css              — 样式自动适应
```

---

## Pexels 图片搜索与下载

> 使用 **Pexels 官方 API**（首选）搜索图片素材。免费注册 https://www.pexels.com/api/ 获取 API Key。
> Key 通过**环境变量** `PEXELS_KEY` 提供（不入库）。网络代理通过 `HTTPS_PROXY` 提供（可选）。
> ⚠️ 免费版每月仅 200 次请求，务必节约使用，每次只搜 1 页。

### 方案 A：Pexels 官方 API（✅ 首选，已内置脚本）

仓库自带 `scripts/pexels_api_search.py`，会自动搜索并下载 20 张缩略图到 `new-animals/references/<name>/`：

```bash
export PEXELS_KEY="你的API_KEY"        # 环境变量提供 Key
python scripts/pexels_api_search.py jellyfish
```

手动调用 API 的参考代码：

```python
import requests, os

API_KEY = os.environ["PEXELS_KEY"]  # 从环境变量读取，不要硬编码
headers = {"Authorization": API_KEY}

# 搜索：每页 20 张，只取 page=1
url = f"https://api.pexels.com/v1/search?query=jellyfish&per_page=20&page=1"
data = requests.get(url, headers=headers).json()

for p in data["photos"]:
    pid = p["id"]
    alt = (p.get("alt") or "")[:55]
    thumb = p["src"]["tiny"]  # 小图 URL
    print(f"ID:{pid}  {alt}")
    print(f"  小图: {thumb}")
    print(f"  原图: https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg")
```

API 返回的结构化 JSON 包含：
- `id` — 照片 ID（用于下载原图）
- `alt` — 图片描述（确认是否匹配目标动物）
- `src.tiny` / `src.small` / `src.medium` — 不同尺寸的缩略图
- `width` / `height` — 原始分辨率

### 方案 B：Playwright 自动化搜索（备选）

如果 API 额度用完或不可用，用 Playwright + stealth 绕过 Cloudflare 直接搜索：

```bash
pip install playwright playwright-stealth
python -m playwright install chromium
```

搜索参考实现见 `scripts/pexels_api_search.py`（或直接用 pexels-reference-finder 技能），替换动物名即可使用。

### 下载高清原图（用户确认后）

用户选中图片后，下载原图到 `media/images/`：

```python
import urllib.request, ssl

pid = 3046629  # 用户选中的 Pexels 照片 ID
url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg"

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_ctx))

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
data = opener.open(req, timeout=30).read()
with open(f"media/images/{animal}.jpg", 'wb') as f:
    f.write(data)
```

> 不加 `?w=` 参数就是原始分辨率，确保长边 ≥ 3000px。

---

## 音频生成方式

使用 edge-tts（Microsoft Edge 内置神经网络语音），免费、无需 API Key。

| 用途 | 推荐语音 | 说明 |
|------|---------|------|
| 中文（动物名 + 科普） | `zh-CN-XiaoxiaoNeural` | 女声，自然清晰 |
| 英文（动物名） | `en-US-JennyNeural` | 美式女声 |

```bash
pip install edge-tts
```

---

## 调试和验证

1. **数据一致性**：运行 `python manage.py check_data`，自动校验 DB / 媒体文件 / apps/core/data/ 三方一致
2. **检查焦点**：运行 `python manage.py runserver`，在浏览器中查看各模式下的图片显示
3. **检查分组**：在浏览模式页面顶部查看 Tabs，确认新动物出现在正确的分组中
4. **检查排序**：确认拼音排序正确
5. **音频文件**：确认三个目录都有对应文件，否则播放按钮会变灰色
6. **自动化测试**：运行 `python manage.py test apps.core`（20 个测试，含数据完整性校验）

### 验证分组数量

```bash
python manage.py shell -c "
from django.db.models import Count
from apps.core.models import Item
for g, cnt in Item.objects.values('group').annotate(c=Count('id')).order_by('group'):
    print(f'{g or \"(无)\"}: {cnt}只')
"
```
