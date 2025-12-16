# 乙方宝招标公告抓取工具

自动抓取乙方宝平台48小时内无纸化会议招标公告，提取关键字段并生成Excel表格。

**支持两种使用方式：**
- 🖥️ **图形界面版本** - 双击即可运行，适合普通用户
- ⌨️ **命令行版本** - 支持自动化和定时任务

## 🚀 功能特性

- ✅ 自动抓取乙方宝平台招标公告
- ✅ 支持按关键词搜索（默认：无纸化会议）
- ✅ 支持自定义时间范围（默认：48小时）
- ✅ 自动提取关键字段：
  - 发布时间
  - 公告发布单位
  - 项目预算
  - 招标文件获取时间
  - 招标报名截止时间
  - 报名费用
  - 投标保证金
- ✅ 生成格式化Excel报表（带样式）
- ✅ 支持CSV导出
- ✅ 跨平台支持（Windows / macOS / Linux）

## 📋 系统要求

- Python 3.8+
- 网络连接

## 📦 安装

### 1. 克隆或下载项目

```bash
git clone <repository-url>
cd xm-assets
```

### 2. 创建虚拟环境（推荐）

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 🔧 使用方法

### 基本用法

```bash
# 使用默认配置运行（抓取48小时内的无纸化会议招标公告）
python main.py
```

### 命令行参数

```bash
python main.py [选项]

选项:
  -k, --keywords      搜索关键词（可多个）
  -t, --time-range    时间范围（小时），默认48
  -o, --output        输出目录，默认 ./output
  --no-details        不抓取详情页（更快但信息较少）
  --csv               同时导出CSV格式
  -q, --quiet         静默模式，减少输出
  -h, --help          显示帮助信息
```

### 使用示例

```bash
# 抓取最近24小时的公告
python main.py -t 24

# 使用自定义关键词
python main.py -k "无纸化会议" "视频会议"

# 指定输出目录并导出CSV
python main.py -o ./results --csv

# 快速模式（不抓取详情）
python main.py --no-details

# 静默模式运行
python main.py -q
```

## 📂 输出文件

程序运行后会在 `output` 目录（或指定目录）生成Excel文件：

```
output/
└── 招标公告_无纸化会议_20241216_150000.xlsx
```

### Excel表格字段

| 字段 | 说明 |
|------|------|
| 公告标题 | 招标公告完整标题 |
| 发布时间 | 公告发布日期 |
| 公告发布单位 | 招标/采购单位名称 |
| 项目预算 | 项目预算金额 |
| 招标文件获取时间 | 文件获取起止时间 |
| 招标报名截止时间 | 投标截止日期时间 |
| 报名费用 | 标书费/报名费 |
| 投标保证金 | 保证金金额 |
| 项目类型 | 采购方式类型 |
| 项目地区 | 项目所在地区 |
| 公告类型 | 招标公告/招标预告等 |
| 详情链接 | 公告详情页URL |

## ⚙️ 配置说明

修改 `config.py` 可自定义以下配置：

```python
# 搜索配置
SEARCH_CONFIG = {
    "keywords": ["无纸化会议"],  # 默认搜索关键词
    "time_range_hours": 48,       # 默认时间范围
}

# 请求配置
REQUEST_CONFIG = {
    "timeout": 30,           # 请求超时时间
    "request_delay": 1.0,    # 请求间隔（秒）
    "max_retries": 3,        # 最大重试次数
}
```

## 📝 项目结构

```
xm-assets/
├── gui_app.py       # 图形界面版本 ⭐ (双击运行)
├── main.py          # 命令行版本
├── scraper.py       # 爬虫模块
├── exporter.py      # Excel导出模块
├── config.py        # 配置文件
├── requirements.txt # 依赖列表
├── README.md        # 使用说明
├── BUILD_MAC.md     # Mac打包说明
├── build_mac.sh     # Mac打包脚本
├── build_windows.bat # Windows打包脚本
└── output/          # 输出目录
```

## 🖥️ 图形界面版本

### 直接运行（需要Python环境）

```bash
# 安装依赖后
python gui_app.py
```

### 打包成可执行文件

#### macOS 打包

```bash
# 给脚本添加执行权限
chmod +x build_mac.sh

# 运行打包脚本
./build_mac.sh
```

打包完成后，在 `dist` 目录下会生成 `招标公告抓取工具.app`，双击即可运行。

详细说明请查看 [BUILD_MAC.md](BUILD_MAC.md)

#### Windows 打包

双击运行 `build_windows.bat`，或在命令行执行：

```bash
build_windows.bat
```

打包完成后，在 `dist` 目录下会生成 `招标公告抓取工具.exe`。

## ⚠️ 注意事项

1. **请求频率**: 程序已设置请求延迟，请勿修改为过于频繁的请求，以免对目标网站造成压力
2. **登录限制**: 乙方宝网站部分信息需要登录后才能查看，程序仅抓取公开可见的信息
3. **法律合规**: 请遵守目标网站的使用条款和相关法律法规
4. **网络问题**: 如遇网络问题导致抓取失败，程序会自动重试

## 🔄 定时任务设置

### Windows（任务计划程序）

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器（如每天执行）
4. 操作选择"启动程序"
5. 程序填写 Python 解释器路径
6. 参数填写脚本路径：`E:\gitLab\xm-assets\main.py`

### macOS / Linux（cron）

```bash
# 编辑crontab
crontab -e

# 添加定时任务（每天早上9点执行）
0 9 * * * cd /path/to/xm-assets && /path/to/python main.py -q >> /path/to/logs/scraper.log 2>&1
```

## 🐛 问题排查

### 常见问题

1. **ImportError: No module named 'xxx'**
   - 确保已激活虚拟环境并安装依赖：`pip install -r requirements.txt`

2. **请求超时或失败**
   - 检查网络连接
   - 目标网站可能暂时不可用，稍后重试

3. **Excel文件无法打开**
   - 确保安装了 openpyxl 库
   - 尝试使用其他 Excel 软件打开

4. **中文显示乱码**
   - CSV文件使用 UTF-8-BOM 编码，Excel打开时应自动识别
   - 如仍有问题，可在Excel中导入时选择 UTF-8 编码

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

