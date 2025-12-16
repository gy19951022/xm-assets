@echo off
chcp 65001 >nul
echo ======================================
echo 乙方宝招标公告抓取工具 - Windows打包脚本
echo ======================================
echo.

REM 检查Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python 已安装
python --version
echo.

REM 创建虚拟环境
echo 正在创建虚拟环境...
python -m venv venv
call venv\Scripts\activate

REM 安装依赖
echo.
echo 正在安装依赖...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

REM 打包应用
echo.
echo 正在打包应用程序...

pyinstaller --noconfirm --onefile --windowed ^
    --name "招标公告抓取工具" ^
    --add-data "config.py;." ^
    --add-data "scraper.py;." ^
    --add-data "exporter.py;." ^
    --hidden-import "requests" ^
    --hidden-import "bs4" ^
    --hidden-import "lxml" ^
    --hidden-import "pandas" ^
    --hidden-import "openpyxl" ^
    --hidden-import "tqdm" ^
    gui_app.py

REM 检查结果
if exist "dist\招标公告抓取工具.exe" (
    echo.
    echo ======================================
    echo [成功] 打包完成！
    echo ======================================
    echo.
    echo 应用程序位置: dist\招标公告抓取工具.exe
    echo.
    echo 您可以双击 .exe 文件直接运行
    echo.
    start dist
) else (
    echo.
    echo [失败] 打包失败，请检查错误信息
)

pause


