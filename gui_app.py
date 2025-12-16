# -*- coding: utf-8 -*-
"""
乙方宝招标公告抓取工具 - 图形界面版本
支持 Windows / macOS / Linux
"""

import sys
import os
import threading
import webbrowser
from datetime import datetime
from tkinter import *
from tkinter import ttk, messagebox, filedialog
import queue

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import YfbzbScraper
from exporter import ExcelExporter


class Application:
    """图形界面应用程序"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("乙方宝招标公告抓取工具")
        self.root.geometry("700x550")
        self.root.minsize(600, 450)
        
        # 设置样式
        self.setup_styles()
        
        # 消息队列用于线程通信
        self.message_queue = queue.Queue()
        
        # 是否正在运行
        self.is_running = False
        
        # 创建界面
        self.create_widgets()
        
        # 定期检查消息队列
        self.check_queue()
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        
        # 尝试使用更现代的主题
        available_themes = style.theme_names()
        if 'aqua' in available_themes:  # macOS
            style.theme_use('aqua')
        elif 'vista' in available_themes:  # Windows
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')
    
    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="🔍 乙方宝招标公告抓取工具",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # 配置区域
        config_frame = ttk.LabelFrame(main_frame, text="抓取配置", padding="15")
        config_frame.pack(fill=X, pady=(0, 15))
        
        # 关键词设置
        keyword_frame = ttk.Frame(config_frame)
        keyword_frame.pack(fill=X, pady=5)
        
        ttk.Label(keyword_frame, text="搜索关键词:").pack(side=LEFT)
        self.keyword_var = StringVar(value="无纸化会议")
        keyword_entry = ttk.Entry(keyword_frame, textvariable=self.keyword_var, width=40)
        keyword_entry.pack(side=LEFT, padx=(10, 0))
        
        # 时间范围设置
        time_frame = ttk.Frame(config_frame)
        time_frame.pack(fill=X, pady=5)
        
        ttk.Label(time_frame, text="时间范围:").pack(side=LEFT)
        self.time_var = StringVar(value="48")
        time_combo = ttk.Combobox(
            time_frame, 
            textvariable=self.time_var,
            values=["24", "48", "72", "168"],
            width=10,
            state="readonly"
        )
        time_combo.pack(side=LEFT, padx=(10, 5))
        ttk.Label(time_frame, text="小时").pack(side=LEFT)
        
        # 是否抓取详情
        self.fetch_details_var = BooleanVar(value=True)
        details_check = ttk.Checkbutton(
            config_frame, 
            text="抓取详情页（获取更多字段信息，但速度较慢）",
            variable=self.fetch_details_var
        )
        details_check.pack(anchor=W, pady=5)
        
        # 输出目录设置
        output_frame = ttk.Frame(config_frame)
        output_frame.pack(fill=X, pady=5)
        
        ttk.Label(output_frame, text="输出目录:").pack(side=LEFT)
        self.output_var = StringVar(value=os.path.join(os.getcwd(), "output"))
        output_entry = ttk.Entry(output_frame, textvariable=self.output_var, width=40)
        output_entry.pack(side=LEFT, padx=(10, 5))
        
        browse_btn = ttk.Button(output_frame, text="浏览...", command=self.browse_output)
        browse_btn.pack(side=LEFT)
        
        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=X, pady=15)
        
        self.start_btn = ttk.Button(
            btn_frame, 
            text="🚀 开始抓取",
            command=self.start_scraping
        )
        self.start_btn.pack(side=LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(
            btn_frame, 
            text="⏹ 停止",
            command=self.stop_scraping,
            state=DISABLED
        )
        self.stop_btn.pack(side=LEFT, padx=(0, 10))
        
        self.open_folder_btn = ttk.Button(
            btn_frame, 
            text="📂 打开输出目录",
            command=self.open_output_folder
        )
        self.open_folder_btn.pack(side=LEFT)
        
        # 进度区域
        progress_frame = ttk.LabelFrame(main_frame, text="运行状态", padding="15")
        progress_frame.pack(fill=BOTH, expand=True)
        
        # 进度条
        self.progress_var = DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=X, pady=(0, 10))
        
        # 状态标签
        self.status_var = StringVar(value="就绪")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        status_label.pack(anchor=W)
        
        # 日志区域
        log_frame = ttk.Frame(progress_frame)
        log_frame.pack(fill=BOTH, expand=True, pady=(10, 0))
        
        self.log_text = Text(
            log_frame, 
            height=10, 
            wrap=WORD,
            font=('Consolas', 10) if sys.platform == 'win32' else ('Monaco', 10)
        )
        self.log_text.pack(side=LEFT, fill=BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient=VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # 底部信息
        footer = ttk.Label(
            main_frame, 
            text="数据来源: 乙方宝 (www.yfbzb.com)",
            foreground="gray"
        )
        footer.pack(pady=(10, 0))
    
    def browse_output(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(initialdir=self.output_var.get())
        if directory:
            self.output_var.set(directory)
    
    def open_output_folder(self):
        """打开输出目录"""
        output_dir = self.output_var.get()
        if os.path.exists(output_dir):
            if sys.platform == 'darwin':  # macOS
                os.system(f'open "{output_dir}"')
            elif sys.platform == 'win32':  # Windows
                os.startfile(output_dir)
            else:  # Linux
                os.system(f'xdg-open "{output_dir}"')
        else:
            messagebox.showwarning("警告", "输出目录不存在")
    
    def log(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(END, f"[{timestamp}] {message}\n")
        self.log_text.see(END)
    
    def update_status(self, status):
        """更新状态"""
        self.status_var.set(status)
    
    def update_progress(self, value):
        """更新进度"""
        self.progress_var.set(value)
    
    def check_queue(self):
        """检查消息队列"""
        try:
            while True:
                msg_type, msg_data = self.message_queue.get_nowait()
                
                if msg_type == 'log':
                    self.log(msg_data)
                elif msg_type == 'status':
                    self.update_status(msg_data)
                elif msg_type == 'progress':
                    self.update_progress(msg_data)
                elif msg_type == 'done':
                    self.on_scraping_done(msg_data)
                elif msg_type == 'error':
                    self.on_scraping_error(msg_data)
        except queue.Empty:
            pass
        
        # 继续检查
        self.root.after(100, self.check_queue)
    
    def start_scraping(self):
        """开始抓取"""
        if self.is_running:
            return
        
        # 验证输入
        keyword = self.keyword_var.get().strip()
        if not keyword:
            messagebox.showerror("错误", "请输入搜索关键词")
            return
        
        # 更新UI状态
        self.is_running = True
        self.start_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        self.log_text.delete(1.0, END)
        self.progress_var.set(0)
        
        # 在后台线程运行抓取
        thread = threading.Thread(target=self.run_scraping, daemon=True)
        thread.start()
    
    def stop_scraping(self):
        """停止抓取"""
        self.is_running = False
        self.message_queue.put(('log', '用户请求停止...'))
    
    def run_scraping(self):
        """运行抓取任务（在后台线程）"""
        try:
            keyword = self.keyword_var.get().strip()
            time_range = int(self.time_var.get())
            fetch_details = self.fetch_details_var.get()
            output_dir = self.output_var.get()
            
            self.message_queue.put(('log', f'开始抓取关键词: {keyword}'))
            self.message_queue.put(('log', f'时间范围: 最近 {time_range} 小时'))
            self.message_queue.put(('status', '正在搜索招标公告...'))
            
            # 初始化爬虫
            scraper = YfbzbScraper(
                keywords=[keyword],
                time_range_hours=time_range
            )
            
            # 搜索公告列表
            self.message_queue.put(('progress', 10))
            all_results = []
            page = 1
            
            while self.is_running and page <= scraper.max_pages:
                self.message_queue.put(('log', f'正在抓取第 {page} 页...'))
                results, has_more = scraper.search_list(keyword, page)
                
                if not results:
                    break
                
                all_results.extend(results)
                self.message_queue.put(('log', f'本页获取 {len(results)} 条公告'))
                
                if not has_more:
                    break
                
                page += 1
            
            if not self.is_running:
                self.message_queue.put(('log', '抓取已停止'))
                self.message_queue.put(('done', None))
                return
            
            if not all_results:
                self.message_queue.put(('log', '未找到符合条件的公告'))
                self.message_queue.put(('done', None))
                return
            
            self.message_queue.put(('log', f'共获取 {len(all_results)} 条公告'))
            self.message_queue.put(('progress', 30))
            
            # 抓取详情
            if fetch_details:
                self.message_queue.put(('status', '正在抓取公告详情...'))
                total = len(all_results)
                
                for i, item in enumerate(all_results):
                    if not self.is_running:
                        break
                    
                    if item.get("detail_url"):
                        details = scraper.get_detail(item["detail_url"])
                        item.update(details)
                    
                    progress = 30 + (i + 1) / total * 50
                    self.message_queue.put(('progress', progress))
                    self.message_queue.put(('status', f'正在抓取详情 ({i+1}/{total})...'))
            
            if not self.is_running:
                self.message_queue.put(('log', '抓取已停止'))
                self.message_queue.put(('done', None))
                return
            
            # 导出Excel
            self.message_queue.put(('status', '正在生成Excel报表...'))
            self.message_queue.put(('progress', 90))
            
            exporter = ExcelExporter(output_dir=output_dir)
            filepath = exporter.export(all_results)
            
            self.message_queue.put(('progress', 100))
            self.message_queue.put(('log', f'Excel文件已保存: {filepath}'))
            self.message_queue.put(('done', filepath))
            
        except Exception as e:
            self.message_queue.put(('error', str(e)))
    
    def on_scraping_done(self, filepath):
        """抓取完成"""
        self.is_running = False
        self.start_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        
        if filepath:
            self.update_status(f"完成! 文件已保存")
            
            # 询问是否打开文件
            if messagebox.askyesno("完成", f"抓取完成！\n\n是否打开生成的Excel文件？"):
                if sys.platform == 'darwin':
                    os.system(f'open "{filepath}"')
                elif sys.platform == 'win32':
                    os.startfile(filepath)
                else:
                    os.system(f'xdg-open "{filepath}"')
        else:
            self.update_status("已停止")
    
    def on_scraping_error(self, error_msg):
        """抓取出错"""
        self.is_running = False
        self.start_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        self.update_status("出错")
        self.log(f"错误: {error_msg}")
        messagebox.showerror("错误", f"抓取过程中出错:\n{error_msg}")


def main():
    """主函数"""
    root = Tk()
    
    # 设置应用图标（如果有）
    # root.iconbitmap('icon.ico')
    
    # macOS特殊处理
    if sys.platform == 'darwin':
        # 使用原生菜单栏
        root.createcommand('tk::mac::Quit', root.destroy)
    
    app = Application(root)
    root.mainloop()


if __name__ == "__main__":
    main()


