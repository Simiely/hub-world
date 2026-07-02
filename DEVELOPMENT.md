# Hub World · 开发文档

## 项目结构

```
hub-world/
├── index.html              # 主入口（单文件应用）
├── .nojekyll              # GitHub Pages 跳过 Jekyll
└── <project-name>/        # 各子项目目录
```

## 架构说明

- 单文件 SPA，`index.html` 包含两个视图：
  - `#viewWelcome`：首页（浮动卡片 + CTA）
  - `#viewCatalog`：目录页（Masonry 网格）
- 视图切换通过 CSS `opacity/visibility/transform` 过渡
- 无框架依赖，无构建步骤

## 分类系统

导航栏 tab 对应 `category` 字段：
- `web` → 网页
- `tool` → 工具
- `design` → 设计

## 样式定制

CSS 变量在 `:root` 中定义，主要可改：
- `--pink`：强调色
- `--bg` / `--bg-card`：背景色
- `--text` / `--text-muted`：文字色

## 部署

推送到 `main` 分支后，GitHub Pages 自动部署（源码模式）。  
访问地址：<ADDRESS_REMOVED>

## 注意事项

- 子项目需放在对应 `path` 的子目录下
- `path` 值不要带前导 `/` 或尾部 `/`
- 分类 tab 的 `data-cat` 需与 `projects[].category` 一致
