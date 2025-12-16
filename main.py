# -*- coding: utf-8 -*-
"""
乙方宝招标公告抓取工具 - 主程序
自动抓取48小时内无纸化会议招标公告

跨平台支持: Windows / macOS / Linux
"""

import sys
import os
import argparse
from datetime import datetime
import logging

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from colorama import init, Fore, Style
from scraper import YfbzbScraper
from exporter import ExcelExporter
from config import SEARCH_CONFIG, OUTPUT_CONFIG

# 初始化colorama（Windows兼容）
init()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


def print_banner():
    """打印程序横幅"""
    banner = f"""
{Fore.CYAN}================================================================
|                                                              |
|      {Fore.YELLOW}乙方宝招标公告抓取工具{Fore.CYAN}                              |
|      {Fore.WHITE}Yfbzb Bid Announcement Scraper{Fore.CYAN}                       |
|                                                              |
|      {Fore.GREEN}* 自动抓取无纸化会议招标公告{Fore.CYAN}                         |
|      {Fore.GREEN}* 支持自定义时间范围和关键词{Fore.CYAN}                         |
|      {Fore.GREEN}* 生成格式化Excel报表{Fore.CYAN}                               |
|      {Fore.GREEN}* 跨平台支持 (Windows/macOS/Linux){Fore.CYAN}                  |
|                                                              |
================================================================{Style.RESET_ALL}
"""
    try:
        print(banner)
    except UnicodeEncodeError:
        # Windows终端编码问题时使用简单输出
        print("\n乙方宝招标公告抓取工具 / Yfbzb Bid Announcement Scraper\n")


def print_summary(results: list, filepath: str, elapsed_time: float):
    """打印抓取结果摘要"""
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}抓取完成!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}公告总数:{Style.RESET_ALL} {len(results)} 条")
    print(f"  {Fore.CYAN}耗时:{Style.RESET_ALL} {elapsed_time:.2f} 秒")
    print(f"  {Fore.CYAN}输出文件:{Style.RESET_ALL} {filepath}")
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='乙方宝招标公告抓取工具 - 自动抓取无纸化会议招标公告',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                          # 使用默认设置抓取
  python main.py -k "无纸化会议"           # 指定搜索关键词
  python main.py -t 24                    # 抓取最近24小时的公告
  python main.py -o ./results             # 指定输出目录
  python main.py --no-details             # 只抓取列表，不抓取详情
  python main.py --csv                    # 同时导出CSV格式
        """
    )
    
    parser.add_argument(
        '-k', '--keywords',
        nargs='+',
        default=SEARCH_CONFIG["keywords"],
        help='搜索关键词（可多个）'
    )
    
    parser.add_argument(
        '-t', '--time-range',
        type=int,
        default=SEARCH_CONFIG["time_range_hours"],
        help='时间范围（小时），默认48小时'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=OUTPUT_CONFIG["output_dir"],
        help='输出目录'
    )
    
    parser.add_argument(
        '--no-details',
        action='store_true',
        help='不抓取详情页（更快但信息较少）'
    )
    
    parser.add_argument(
        '--csv',
        action='store_true',
        help='同时导出CSV格式'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='静默模式，减少输出'
    )
    
    args = parser.parse_args()
    
    # 打印横幅
    if not args.quiet:
        print_banner()
    
    # 显示配置信息
    print(f"{Fore.CYAN}当前配置:{Style.RESET_ALL}")
    print(f"  搜索关键词: {', '.join(args.keywords)}")
    print(f"  时间范围: 最近 {args.time_range} 小时")
    print(f"  输出目录: {args.output}")
    print(f"  抓取详情: {'否' if args.no_details else '是'}")
    print()
    
    # 记录开始时间
    start_time = datetime.now()
    
    try:
        # 初始化爬虫
        print(f"{Fore.YELLOW}正在初始化爬虫...{Style.RESET_ALL}")
        scraper = YfbzbScraper(
            keywords=args.keywords,
            time_range_hours=args.time_range
        )
        
        # 执行抓取
        print(f"{Fore.YELLOW}开始抓取招标公告...{Style.RESET_ALL}\n")
        results = scraper.scrape(
            fetch_details=not args.no_details,
            show_progress=not args.quiet
        )
        
        if not results:
            print(f"\n{Fore.YELLOW}未找到符合条件的招标公告{Style.RESET_ALL}")
            return 0
        
        # 导出结果
        print(f"\n{Fore.YELLOW}正在生成Excel报表...{Style.RESET_ALL}")
        exporter = ExcelExporter(output_dir=args.output)
        filepath = exporter.export(results)
        
        # 导出CSV（如果需要）
        if args.csv:
            print(f"{Fore.YELLOW}正在生成CSV文件...{Style.RESET_ALL}")
            csv_path = exporter.export_csv(results)
            print(f"  CSV文件: {csv_path}")
        
        # 计算耗时
        elapsed_time = (datetime.now() - start_time).total_seconds()
        
        # 打印摘要
        print_summary(results, filepath, elapsed_time)
        
        # 显示部分结果预览
        if not args.quiet and results:
            print(f"{Fore.CYAN}结果预览 (前5条):{Style.RESET_ALL}")
            print("-" * 60)
            for i, item in enumerate(results[:5], 1):
                title = item.get('title', '')[:40]
                if len(item.get('title', '')) > 40:
                    title += '...'
                publish_time = item.get('publish_time', 'N/A')
                region = item.get('region', 'N/A')
                print(f"  {i}. [{publish_time}] {title}")
                print(f"     地区: {region}")
            if len(results) > 5:
                print(f"  ... 还有 {len(results) - 5} 条")
            print("-" * 60)
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}用户取消操作{Style.RESET_ALL}")
        return 1
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

