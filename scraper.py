# -*- coding: utf-8 -*-
"""
爬虫模块 - 乙方宝招标公告抓取
"""

import re
import time
import requests
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlencode, quote
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple
from tqdm import tqdm
import logging

from config import YFBZB_CONFIG, REQUEST_CONFIG, SEARCH_CONFIG

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class YfbzbScraper:
    """乙方宝招标公告爬虫"""
    
    def __init__(self, keywords: List[str] = None, time_range_hours: int = None):
        """
        初始化爬虫
        
        Args:
            keywords: 搜索关键词列表
            time_range_hours: 时间范围（小时）
        """
        self.base_url = YFBZB_CONFIG["base_url"]
        self.search_url = YFBZB_CONFIG["search_url"]
        self.page_size = YFBZB_CONFIG["page_size"]
        self.max_pages = YFBZB_CONFIG["max_pages"]
        
        self.keywords = keywords or SEARCH_CONFIG["keywords"]
        self.time_range_hours = time_range_hours or SEARCH_CONFIG["time_range_hours"]
        
        self.headers = REQUEST_CONFIG["headers"]
        self.timeout = REQUEST_CONFIG["timeout"]
        self.request_delay = REQUEST_CONFIG["request_delay"]
        self.max_retries = REQUEST_CONFIG["max_retries"]
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 计算时间范围
        self.cutoff_time = datetime.now() - timedelta(hours=self.time_range_hours)
    
    def _make_request(self, url: str, params: dict = None) -> Optional[str]:
        """
        发送HTTP请求
        
        Args:
            url: 请求URL
            params: 请求参数
            
        Returns:
            响应HTML内容
        """
        # 修改headers，移除Accept-Encoding让requests自动处理
        headers = self.headers.copy()
        headers.pop('Accept-Encoding', None)  # 让requests自动处理压缩
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                # 自动检测编码
                if response.encoding is None or response.encoding == 'ISO-8859-1':
                    response.encoding = response.apparent_encoding or 'utf-8'
                
                return response.text
            except requests.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.request_delay * 2)
        
        logger.error(f"请求失败，已达最大重试次数: {url}")
        return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        解析日期字符串
        
        Args:
            date_str: 日期字符串
            
        Returns:
            datetime对象
        """
        if not date_str:
            return None
        
        # 清理日期字符串
        date_str = date_str.strip().replace('****', '').strip()
        
        # 常见日期格式
        formats = [
            "%Y/%m/%d",
            "%Y-%m-%d",
            "%Y年%m月%d日",
            "%Y/%m/%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y年%m月%d日 %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%Y-%m-%d %H:%M",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # 尝试提取年月日
        match = re.search(r'(\d{4})[/-年](\d{1,2})[/-月](\d{1,2})', date_str)
        if match:
            try:
                return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            except ValueError:
                pass
        
        return None
    
    def _is_within_time_range(self, date: Optional[datetime]) -> bool:
        """
        检查日期是否在时间范围内
        
        Args:
            date: 日期对象
            
        Returns:
            是否在范围内
        """
        if not date:
            return True  # 无法解析日期时，保留该记录
        return date >= self.cutoff_time
    
    def search_list(self, keyword: str, page: int = 1) -> Tuple[List[Dict], bool]:
        """
        搜索招标公告列表
        
        Args:
            keyword: 搜索关键词
            page: 页码
            
        Returns:
            (公告列表, 是否还有更多)
        """
        # 构建搜索URL - 使用正确的参数格式
        params = {
            "type": 0,
            "defaultSearch": "false",
            "keyword": keyword,  # 注意是小写的keyword
            "pageNo": page,
            "pageSize": self.page_size,
            "noticeType": 3,
            "invitedBidType": 3,
            "timeType": 1,
            "searchType": 2,
            "searchMode": 1,
        }
        
        html = self._make_request(self.search_url, params)
        if not html:
            logger.error("请求返回空内容")
            return [], False
        
        logger.debug(f"获取到HTML内容，长度: {len(html)}")
        
        soup = BeautifulSoup(html, 'lxml')
        results = []
        has_more = False
        
        # 查找表格 - 使用id定位
        table = soup.find('table', id='treeTable')
        if not table:
            # 回退到class查找
            table = soup.find('table', class_='table-hover')
        if not table:
            # 再回退到普通查找
            tables = soup.find_all('table')
            logger.debug(f"页面中的表格数量: {len(tables)}")
            if tables:
                table = tables[0]
        if not table:
            logger.warning("未找到招标列表表格")
            # 打印部分HTML帮助调试
            logger.debug(f"HTML预览: {html[:1000]}")
            return [], False
        
        logger.debug(f"找到表格，id={table.get('id')}, class={table.get('class')}")
        
        # 查找所有行（跳过表头）
        rows = table.find_all('tr')[1:]  # 跳过表头行
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 4:
                try:
                    # 提取标题和链接
                    title_cell = cells[0]
                    link_tag = title_cell.find('a')
                    
                    if link_tag:
                        title = link_tag.get_text(strip=True)
                        detail_url = link_tag.get('href', '')
                        if detail_url and not detail_url.startswith('http'):
                            detail_url = urljoin(self.base_url, detail_url)
                    else:
                        title = title_cell.get_text(strip=True)
                        detail_url = ""
                    
                    # 提取其他字段
                    announcement_type = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                    region = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                    publish_date = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                    
                    # 解析并检查日期
                    date_obj = self._parse_date(publish_date)
                    if not self._is_within_time_range(date_obj):
                        # 已超出时间范围，停止抓取
                        logger.info(f"发现超出时间范围的公告: {publish_date}")
                        return results, False
                    
                    results.append({
                        "title": title,
                        "announcement_type": announcement_type,
                        "region": region,
                        "publish_time": publish_date,
                        "detail_url": detail_url,
                    })
                except Exception as e:
                    logger.warning(f"解析列表行失败: {e}")
                    continue
        
        # 检查是否有下一页
        pagination = soup.find('ul', class_='pagination') or soup.find_all('a', string=re.compile(r'下一页'))
        if pagination:
            has_more = True
        
        # 如果当前页有结果，可能还有更多
        if len(rows) >= self.page_size:
            has_more = True
        
        return results, has_more
    
    def get_detail(self, url: str) -> Dict:
        """
        获取招标公告详情
        
        Args:
            url: 详情页URL
            
        Returns:
            详情信息字典
        """
        details = {
            "publish_unit": "",
            "project_budget": "",
            "bid_file_time": "",
            "registration_deadline": "",
            "registration_fee": "",
            "bid_bond": "",
            "project_type": "",
        }
        
        html = self._make_request(url)
        if not html:
            return details
        
        soup = BeautifulSoup(html, 'lxml')
        
        try:
            # 查找详情内容区域
            content = soup.find('div', class_='detail-content') or soup.find('div', class_='content')
            if not content:
                # 尝试查找包含公告内容的区域
                content = soup
            
            text = content.get_text()
            
            # 提取发布单位/采购单位
            patterns_unit = [
                r'(?:采购单位|招标单位|发布单位|项目单位|采购人)[：:]\s*([^\n\r]+)',
                r'企\s*业[：:]\s*([^\n\r]+)',
            ]
            for pattern in patterns_unit:
                match = re.search(pattern, text)
                if match:
                    unit = match.group(1).strip()
                    # 清理隐藏内容标记
                    unit = re.sub(r'\*+|点击登录查看', '', unit).strip()
                    if unit and unit != '':
                        details["publish_unit"] = unit
                        break
            
            # 提取项目预算
            patterns_budget = [
                r'(?:项目预算|预算金额|采购预算|预算)[：:]\s*([\d,.]+)\s*(?:万)?元',
                r'(?:总投资|投资额|合同金额)[：:]\s*([\d,.]+)\s*(?:万)?元',
            ]
            for pattern in patterns_budget:
                match = re.search(pattern, text)
                if match:
                    details["project_budget"] = match.group(1) + "元"
                    break
            
            # 提取招标文件获取时间
            patterns_file_time = [
                r'(?:采购文件|招标文件)(?:.*?)(?:获取|下载)(?:.*?)(?:时间|日期)[：:]\s*([^\n\r]+)',
                r'(?:文件获取时间|获取招标文件时间)[：:]\s*([^\n\r]+)',
                r'获取时间[：:]\s*([^\n\r]+)',
            ]
            for pattern in patterns_file_time:
                match = re.search(pattern, text)
                if match:
                    file_time = match.group(1).strip()
                    file_time = re.sub(r'\*+', '', file_time).strip()
                    if file_time:
                        details["bid_file_time"] = file_time[:100]  # 限制长度
                        break
            
            # 提取报名截止时间/报价截止时间
            patterns_deadline = [
                r'(?:报名截止|投标截止|报价截止)(?:时间|日期)?[：:]\s*([^\n\r]+)',
                r'(?:截止时间|截止日期)[：:]\s*([^\n\r]+)',
                r'报名.*?(?:至|到)\s*(\d{4}[/-年]\d{1,2}[/-月]\d{1,2}[日]?\s*\d{1,2}[：:]\d{1,2})',
            ]
            for pattern in patterns_deadline:
                match = re.search(pattern, text)
                if match:
                    deadline = match.group(1).strip()
                    deadline = re.sub(r'\*+', '', deadline).strip()
                    if deadline:
                        details["registration_deadline"] = deadline[:100]
                        break
            
            # 提取报名费用/标书费
            patterns_fee = [
                r'(?:报名费|标书费|招标文件费|资料费)[：:]\s*([\d,.]+)\s*元?',
                r'(?:报名费|标书费)[：:]\s*(?:人民币)?\s*([\d,.]+)',
            ]
            for pattern in patterns_fee:
                match = re.search(pattern, text)
                if match:
                    fee = match.group(1).strip()
                    if fee and fee != '0':
                        details["registration_fee"] = fee + "元"
                    else:
                        details["registration_fee"] = "0元/免费"
                    break
            
            # 提取投标保证金
            patterns_bond = [
                r'(?:投标保证金|保证金金额|保证金)[：:]\s*([\d,.]+)(?:\s*元)?',
                r'保证金[：:]\s*(?:人民币)?\s*([\d,.]+)',
            ]
            for pattern in patterns_bond:
                match = re.search(pattern, text)
                if match:
                    bond = match.group(1).strip()
                    if bond and float(bond.replace(',', '')) > 0:
                        details["bid_bond"] = bond + "元"
                    break
            
            # 提取项目类型
            patterns_type = [
                r'(?:项目类型|采购类型|招标类型)[：:]\s*([^\n\r]+)',
                r'(?:采购方式|招标方式)[：:]\s*([^\n\r]+)',
            ]
            for pattern in patterns_type:
                match = re.search(pattern, text)
                if match:
                    project_type = match.group(1).strip()
                    project_type = re.sub(r'\*+', '', project_type).strip()
                    if project_type:
                        details["project_type"] = project_type[:50]
                        break
        
        except Exception as e:
            logger.warning(f"解析详情页失败: {e}")
        
        return details
    
    def scrape(self, fetch_details: bool = True, show_progress: bool = True) -> List[Dict]:
        """
        执行抓取任务
        
        Args:
            fetch_details: 是否抓取详情页
            show_progress: 是否显示进度条
            
        Returns:
            抓取结果列表
        """
        all_results = []
        
        for keyword in self.keywords:
            logger.info(f"开始搜索关键词: {keyword}")
            logger.info(f"时间范围: 最近 {self.time_range_hours} 小时")
            
            page = 1
            keyword_results = []
            
            while page <= self.max_pages:
                logger.info(f"正在抓取第 {page} 页...")
                
                results, has_more = self.search_list(keyword, page)
                
                if not results:
                    logger.info("当前页无结果，停止抓取")
                    break
                
                keyword_results.extend(results)
                logger.info(f"本页获取 {len(results)} 条公告")
                
                if not has_more:
                    logger.info("已到达最后一页或超出时间范围")
                    break
                
                page += 1
                time.sleep(self.request_delay)
            
            logger.info(f"关键词 '{keyword}' 共获取 {len(keyword_results)} 条公告")
            
            # 抓取详情
            if fetch_details and keyword_results:
                logger.info("开始抓取公告详情...")
                
                iterator = tqdm(keyword_results, desc="抓取详情") if show_progress else keyword_results
                
                for item in iterator:
                    if item.get("detail_url"):
                        details = self.get_detail(item["detail_url"])
                        item.update(details)
                        time.sleep(self.request_delay)
            
            all_results.extend(keyword_results)
        
        logger.info(f"抓取完成，共获取 {len(all_results)} 条公告")
        return all_results


def main():
    """测试函数"""
    scraper = YfbzbScraper()
    results = scraper.scrape(fetch_details=True)
    
    for i, item in enumerate(results[:5], 1):
        print(f"\n{'='*50}")
        print(f"公告 {i}:")
        for key, value in item.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()

