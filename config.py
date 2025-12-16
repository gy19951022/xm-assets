# -*- coding: utf-8 -*-
"""
配置文件 - 乙方宝招标公告抓取工具
"""

# 乙方宝网站配置
YFBZB_CONFIG = {
    # 基础URL
    "base_url": "https://www.yfbzb.com",
    
    # 搜索API URL
    "search_url": "https://www.yfbzb.com/search/invitedBidSearch",
    
    # 每页数量
    "page_size": 30,
    
    # 最大抓取页数 (防止抓取过多)
    "max_pages": 20,
}

# 搜索关键词配置
SEARCH_CONFIG = {
    # 默认搜索关键词
    "keywords": ["无纸化会议"],
    
    # 时间范围 (小时)
    "time_range_hours": 48,
}

# 请求配置
REQUEST_CONFIG = {
    # 请求超时时间 (秒)
    "timeout": 30,
    
    # 请求间隔 (秒) - 避免频繁请求
    "request_delay": 1.0,
    
    # 重试次数
    "max_retries": 3,
    
    # 请求头 - 不设置Accept-Encoding让requests自动处理
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
}

# 输出配置
OUTPUT_CONFIG = {
    # 输出目录
    "output_dir": "output",
    
    # 输出文件名前缀
    "file_prefix": "招标公告_无纸化会议",
    
    # 日期时间格式
    "datetime_format": "%Y%m%d_%H%M%S",
    
    # Excel配置
    "excel": {
        "sheet_name": "招标公告列表",
        "freeze_panes": "A2",
    }
}

# 字段映射配置 - 从网页提取的字段
FIELD_MAPPING = {
    "title": "公告标题",
    "publish_time": "发布时间",
    "publish_unit": "公告发布单位",
    "project_budget": "项目预算",
    "bid_file_time": "招标文件获取时间",
    "registration_deadline": "招标报名截止时间",
    "registration_fee": "报名费用",
    "bid_bond": "投标保证金",
    "project_type": "项目类型",
    "region": "项目地区",
    "announcement_type": "公告类型",
    "detail_url": "详情链接",
}

# 输出列顺序
OUTPUT_COLUMNS = [
    "公告标题",
    "发布时间",
    "公告发布单位",
    "项目预算",
    "招标文件获取时间",
    "招标报名截止时间",
    "报名费用",
    "投标保证金",
    "项目类型",
    "项目地区",
    "公告类型",
    "详情链接",
]

