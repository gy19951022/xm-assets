# macOS 打包说明

本文档介绍如何在 Mac 电脑上将程序打包成可直接双击运行的 `.app` 应用程序。

## 📋 前置要求

1. **macOS 系统** (10.14 或更高版本)
2. **Python 3.8+** - 如未安装，请访问 https://www.python.org/downloads/ 下载

### 检查 Python 是否已安装

打开「终端」应用，输入:

```bash
python3 --version
```

如果显示版本号（如 `Python 3.11.x`），则已安装。

## 🚀 快速打包（推荐）

### 方法一：使用打包脚本

1. 打开「终端」应用
2. 进入项目目录:
   ```bash
   cd /path/to/xm-assets
   ```
3. 给脚本添加执行权限:
   ```bash
   chmod +x build_mac.sh
   ```
4. 运行打包脚本:
   ```bash
   ./build_mac.sh
   ```
5. 等待打包完成，应用程序会自动出现在 `dist` 文件夹中

### 方法二：手动打包

如果脚本运行失败，可以手动执行以下步骤:

```bash
# 1. 进入项目目录
cd /path/to/xm-assets

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 4. 打包
pyinstaller --noconfirm --onefile --windowed \
    --name "招标公告抓取工具" \
    --add-data "config.py:." \
    --add-data "scraper.py:." \
    --add-data "exporter.py:." \
    gui_app.py

# 5. 查看结果
open dist/
```

## 📦 打包结果

打包成功后，会在 `dist` 目录下生成:

```
dist/
└── 招标公告抓取工具.app    # 双击即可运行
```

## 🎯 使用方法

1. **双击运行**: 直接双击 `招标公告抓取工具.app` 即可启动
2. **添加到应用程序**: 将 `.app` 文件拖到「应用程序」文件夹，方便日后使用
3. **添加到 Dock**: 运行后右键点击 Dock 图标，选择「选项」→「在 Dock 中保留」

## ⚠️ 常见问题

### 1. "无法打开，因为无法验证开发者"

首次运行可能会提示无法验证。解决方法:

- **方法一**: 右键点击 `.app` → 选择「打开」→ 在弹窗中点击「打开」
- **方法二**: 系统偏好设置 → 安全性与隐私 → 点击「仍要打开」

### 2. 打包后应用无法运行

尝试使用以下命令查看错误信息:

```bash
# 从终端运行应用查看错误
/path/to/dist/招标公告抓取工具.app/Contents/MacOS/招标公告抓取工具
```

### 3. 缺少模块错误

如果提示缺少模块，在打包命令中添加:

```bash
--hidden-import "模块名"
```

### 4. 应用体积太大

默认打包会包含所有依赖，如需减小体积，可以:

1. 使用 `--exclude-module` 排除不需要的模块
2. 使用 UPX 压缩（需要单独安装 UPX）

## 📱 创建 DMG 安装包（可选）

如果想创建更专业的 `.dmg` 安装包:

```bash
# 安装 create-dmg
brew install create-dmg

# 创建 DMG
create-dmg \
    --volname "招标公告抓取工具" \
    --window-size 500 300 \
    --icon-size 100 \
    --app-drop-link 350 150 \
    "招标公告抓取工具.dmg" \
    "dist/招标公告抓取工具.app"
```

## 💡 提示

- 打包后的 `.app` 文件可以直接分发给其他 Mac 用户使用
- 用户无需安装 Python 环境即可运行
- 首次运行可能需要几秒钟加载时间

---

如有问题，请检查 Python 版本和依赖是否正确安装。


