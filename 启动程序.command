#!/bin/bash
# 招标公告抓取工具 - Mac启动脚本
# 双击此文件即可运行

cd "$(dirname "$0")"

echo "======================================"
echo "招标公告抓取工具"
echo "======================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python"
    echo "下载地址: https://www.python.org/downloads/"
    echo ""
    read -p "按回车键退出..."
    exit 1
fi

# 检查并安装依赖
echo "正在检查依赖..."
pip3 install -q -r requirements.txt 2>/dev/null || pip3 install --user -q -r requirements.txt

# 运行程序
echo "正在启动程序..."
python3 gui_app.py

