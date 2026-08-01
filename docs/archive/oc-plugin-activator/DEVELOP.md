---
module: archive
title: DEVELOP.md
tags: [oc-plugin-activator]
source:
  project: oc-plugin-activator
  repo: https://github.com/Simiely/oc-plugin-activator
  file: DEVELOP.md
  branch: main
  synced_at: 2026-08-01
---
> 🔗 [查看 GitHub 原文](https://github.com/Simiely/oc-plugin-activator/blob/main/DEVELOP.md)

# 开发文档 — 关键记录

## 项目结构

```
oc_tool.py      主程序
icon.ico        图标（超椭圆 n=3 圆角）
config.json     自动生成
.github/workflows/build-exe.yml
```

## 开发

```bash
pip install pyinstaller
python oc_tool.py
pyinstaller --onefile --windowed --icon icon.ico --name "Activator" oc_tool.py
```

## 关键问题记录

### 1. Bad screen distance 错误

**现象：** `ttk.Style` + `clam` 主题下 `padding=(0,14)` 报错。

**根因：** ttk 的 padding tuple 在某些 tk 版本被转为 `"0 14"` 字符串传给了 Tcl，Tcl 解析失败。

**解决：** 完全抛弃 ttk，只用 `tk.Button/Label/Frame`，颜色用 `bg/fg` 写死。控件构造器不传任何 padx/pady tuple，统一放到 `pack/grid` 中。

### 2. PyInstaller 路径陷阱

**现象：** exe 运行时 `__file__` 指向 `C:\Temp\_MEIxxxxx` 临时解压目录，不是 exe 所在目录。

**解决：** 用 `sys.executable` 获取 exe 真实路径，`sys.frozen` 判断是否打包状态。

```python
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
```

### 3. 目标目录有锁文件导致复制中断

**现象：** 复制 AppData 时，Autodesk 等程序锁住了目标目录下的文件，`shutil.rmtree` 失败。

**解决：** 不删除目标目录，直接用 `shutil.copytree(src, dst, dirs_exist_ok=True)` 合并覆盖。每个文件单独 try/except，锁住的跳过不影响其他。

### 4. ICO 多尺寸生成

**现象：** PIL 的 `Image.save(format='ICO', sizes=[...])` 始终只输出单帧。

**解决：** PIL 负责透明度处理（numpy 矩阵运算），ImageMagick 的 `convert` 负责多尺寸合并。

### 5. 上传后透明通道丢失

**现象：** 用户上传的 PNG 透明图被系统转成 JPEG，Alpha 通道消失。

**解决：** 仓库里同时保留 `icon_source.png`（透明底源文件），CI 构建时用 ImageMagick 重新生成 ICO。实际用 numpy 计算像素到白色的欧氏距离做渐变透明。

### 6. 超椭圆圆角（小米风格）

小米 logo 用 |x/a|³ + |y/b|³ = 1 的超椭圆公式，过渡比圆弧更平滑。

```python
n = 3.0
scale = 0.98
nx = abs(X - cx) / (cx * scale)
ny = abs(Y - cy) / (cy * scale)
val = nx**n + ny**n
alpha = clip((1 + soft - val) / soft, 0, 1) * 255
```

### 7. 深色标题栏

纯 tkinter 无法改标题栏颜色。调用 Windows API：

```python
from ctypes import windll, c_int, byref
HWND = windll.user32.GetParent(root.winfo_id())
windll.dwmapi.DwmSetWindowAttribute(HWND, 20, byref(c_int(2)), c_int(4))
```

### 8. GitHub Actions Node.js 兼容

2026 年 6 月起 GitHub Actions 强制 Node.js 24 运行时，`actions/checkout@v4` 等报 deprecation 警告但可正常工作。后续需升级到原生 Node.js 24 版本。
