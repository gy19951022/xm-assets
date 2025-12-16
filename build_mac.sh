#!/bin/bash
# =====================================================
# macOS 打包脚本
# 在 Mac 电脑上运行此脚本生成 .app 应用程序
# =====================================================

echo "======================================"
echo "乙方宝招标公告抓取工具 - Mac打包脚本"
echo "======================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python"
    echo "   下载地址: https://www.python.org/downloads/"
    exit 1
fi

echo "✓ Python3 已安装"
python3 --version

# 创建虚拟环境
echo ""
echo "正在创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 安装依赖
echo ""
echo "正在安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# 打包应用
echo ""
echo "正在打包应用程序..."

pyinstaller --noconfirm --onefile --windowed \
    --name "招标公告抓取工具" \
    --add-data "config.py:." \
    --add-data "scraper.py:." \
    --add-data "exporter.py:." \
    --hidden-import "requests" \
    --hidden-import "bs4" \
    --hidden-import "lxml" \
    --hidden-import "pandas" \
    --hidden-import "openpyxl" \
    --hidden-import "tqdm" \
    --collect-all "lxml" \
    gui_app.py

# 检查结果
if [ -d "dist/招标公告抓取工具.app" ]; then
    echo ""
    echo "======================================"
    echo "✅ 打包成功！"
    echo "======================================"
    echo ""
    echo "应用程序位置: dist/招标公告抓取工具.app"
    echo ""
    echo "您可以:"
    echo "  1. 双击 .app 文件直接运行"
    echo "  2. 将 .app 拖到「应用程序」文件夹"
    echo ""
    
    # 打开输出目录
    open dist/
else
    echo ""
    echo "❌ 打包失败，请检查错误信息"
    exit 1
fi


