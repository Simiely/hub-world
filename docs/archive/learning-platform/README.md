---
module: archive
title: README.md
tags: [learning-platform]
source:
  project: learning-platform
  repo: https://github.com/Simiely/learning-platform
  file: README.md
  branch: master
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/learning-platform/blob/master/README.md)

# Lets Learn —— 幼儿互动学习卡片

一个基于 **Django + Alpine.js** 的幼儿识字/认知闪卡平台，支持 **浏览、卡片、练习** 三种学习模式，专为触屏（iPad / iPhone）设计。内置 **7 个分类共 183 个条目**的中英文对照学习，配三语自动发音。浏览模式支持按拼音（🀄）或英文首字母（🔤）分块浏览：

| 分类 | 条目数 | 分组 |
|------|--------|------|
| 🐾 动物 | 77 | 家里和农场 / 野生动物 / 海洋动物 / 爬虫和昆虫 |
| 🍎 果蔬 | 23 | 浆果 / 柑橘 / 热带水果 / 根茎蔬菜 / 叶菜瓜果 |
| 🚗 交通工具 | 20 | 陆地 / 轨道 / 水上 / 空中 / 工程车 |
| 🦖 恐龙 | 16 | 食肉 / 食草 / 会飞 |
| 🚀 太空 | 15 | 行星 / 恒星天体 / 航天器 / 天文现象 |
| 🌹 花卉植物 | 16 | 观赏花卉 / 野花野草 / 树木 / 水生植物 |
| 👨‍🚒 职业 | 16 | 医护 / 救援 / 交通 / 教育 / 餐饮 / 运动 / 科学 / 艺术 |

> 除动物外，其他分类图片暂用 emoji 代替（`img_file` 留空），后续再补真实图。

## 快速开始

```bash
git clone https://github.com/Simiely/learning-platform.git
cd learning-platform
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate && python manage.py seed_sync
python manage.py runserver 0.0.0.0:8000
```

打开 **http://localhost:8000** 即可使用。

---

## 你是哪种角色？

### 👶 想直接使用？
三种学习模式：
- **浏览** `/category/animals/` — 方块网格，点击弹窗详情+发音
- **卡片** `/category/animals/cards/` — 全屏翻卡，随机起始，自动发音
- **练习** `/category/animals/quiz/` — 看图选词，10 题一组，答对撒花

点击文字行或喇叭图标播放对应语音，右上角切换深色/浅色/跟随系统主题。

### 🐣 想新加一种动物？
看操作手册 → **[`ADD_ANIMALS_GUIDE.md`](./ADD_ANIMALS_GUIDE.md)**

包含：图片素材下载 → 音频生成（edge-tts）→ 数据整合 → 入库完整流程。

### 🐾 想看全部动物数据？
看动物总表 → **[`ANIMALS.md`](./ANIMALS.md)**

包含：77 只动物的中英名、emoji、图片/音频、科普文案、三套图片焦点、批次进度。

### 🧑‍💻 想开发或改代码？
看开发者文档 → **[`DEVELOPER.md`](./DEVELOPER.md)**

包含：技术栈、项目结构、数据模型、路由、修改规则、前端架构、常见问题排查、Docker 部署。

### 🐛 遇到了奇怪的问题？
看踩坑记录 → **[`DEV.md`](./DEV.md)**

包含：Safari 适配、图片焦点、音频播放、CSS 布局等全部历史问题与解决方案。

### 📋 想知道接下来做什么？
看待办清单 → **[`TODO.md`](./TODO.md)**

---

## License

MIT
