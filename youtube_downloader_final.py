import os
import sys
import json
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from pathlib import Path
import urllib.request
import urllib.error
from urllib.parse import parse_qs, urlparse
import re

# 自动安装依赖
def ensure_dependencies():
    required = ['requests']
    for package in required:
        try:
            __import__(package)
        except ImportError:
            print(f"正在安装 {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])

ensure_dependencies()

import requests


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube 视频下载器 - 完美版")
        self.root.geometry("950x700")
        self.root.resizable(False, False)

        self.url_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(
            value=str(Path.home() / "Downloads" / "YouTube视频")
        )
        self.quality_var = tk.StringVar(value="最高质量")

        self.build_ui()
        self.check_ytdlp()

    def check_ytdlp(self):
        """检查并安装 yt-dlp"""
        try:
            import yt_dlp
        except ImportError:
            self.status_var.set("⏳ 首次启动，正在安装 yt-dlp，请稍候...")
            self.root.update()
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "yt-dlp", "-q"
            ])
            self.status_var.set("✅ yt-dlp 安装完成！")

    def build_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="🎬 YouTube 视频下载器 - 完美版 v3.0", 
            font=("Microsoft YaHei", 16, "bold"),
            foreground="#1f77d2"
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # 说明文字
        info_label = ttk.Label(
            main_frame,
            text="✓ 支持 1080p 高清下载 | ✓ 自动处理所有 YouTube 限制 | ✓ 中文完全支持",
            font=("Microsoft YaHei", 10),
            foreground="green"
        )
        info_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))

        # 视频链接
        ttk.Label(main_frame, text="🔗 YouTube 链接：", font=("Microsoft YaHei", 11, "bold")).grid(
            row=2, column=0, sticky="nw", pady=(0, 5)
        )
        link_frame = ttk.Frame(main_frame)
        link_frame.grid(row=2, column=1, columnspan=2, sticky="ew", pady=(0, 15))
        ttk.Entry(link_frame, textvariable=self.url_var, font=("Microsoft YaHei", 10)).pack(
            side="left", fill="both", expand=True
        )
        ttk.Button(link_frame, text="粘贴", command=self.paste_url, width=6).pack(
            side="left", padx=(5, 0)
        )

        # 保存位置
        ttk.Label(main_frame, text="📁 保存位置：", font=("Microsoft YaHei", 11, "bold")).grid(
            row=3, column=0, sticky="nw", pady=(0, 5)
        )
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=3, column=1, columnspan=2, sticky="ew", pady=(0, 15))
        ttk.Entry(path_frame, textvariable=self.output_dir_var, font=("Microsoft YaHei", 10)).pack(
            side="left", fill="both", expand=True
        )
        ttk.Button(path_frame, text="📂 浏览", command=self.choose_directory, width=8).pack(
            side="left", padx=(5, 0)
        )

        # 质量选择
        ttk.Label(main_frame, text="📊 下载质量：", font=("Microsoft YaHei", 11, "bold")).grid(
            row=4, column=0, sticky="w", pady=(0, 5)
        )
        self.quality_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.quality_var,
            values=[
                "最高质量 (1080p+)",
                "高质量 (720p)", 
                "中等质量 (480p)",
                "仅音频 (MP3)"
            ],
            state="readonly", 
            width=40,
            font=("Microsoft YaHei", 10)
        )
        self.quality_combo.grid(row=4, column=1, sticky="w", pady=(0, 20))

        # 下载按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        
        self.download_btn = ttk.Button(
            button_frame, 
            text="⬇️ 开始下载", 
            command=self.start_download,
            width=30
        )
        self.download_btn.pack(side="left", padx=(0, 10))
        
        self.cancel_btn = ttk.Button(
            button_frame,
            text="⏹️ 取消",
            command=self.cancel_download,
            state="disabled",
            width=15
        )
        self.cancel_btn.pack(side="left")

        # 进度条
        self.progress = ttk.Progressbar(
            main_frame, 
            orient="horizontal", 
            mode="determinate",
            length=900
        )
        self.progress.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(0, 5))

        # 进度百分比
        self.percent_label = ttk.Label(
            main_frame, 
            text="0%", 
            font=("Microsoft YaHei", 10, "bold")
        )
        self.percent_label.grid(row=7, column=0, columnspan=3, sticky="w", pady=(0, 10))

        # 状态信息框
        ttk.Label(main_frame, text="📝 状态信息：", font=("Microsoft YaHei", 10, "bold")).grid(
            row=8, column=0, columnspan=3, sticky="w", pady=(0, 5)
        )
        
        self.status_text = scrolledtext.ScrolledText(
            main_frame,
            height=8,
            width=100,
            font=("Microsoft YaHei", 9),
            state="disabled"
        )
        self.status_text.grid(row=9, column=0, columnspan=3, sticky="ew", pady=(0, 0))

        self.status_var = tk.StringVar(value="✓ 就绪")

        main_frame.columnconfigure(1, weight=1)
        self.is_downloading = False

    def paste_url(self):
        try:
            url = self.root.clipboard_get()
            self.url_var.set(url)
            self.append_status(f"✓ 已粘贴链接: {url[:60]}...")
        except:
            messagebox.showerror("错误", "无法从剪贴板获取内容")

    def append_status(self, message):
        """添加状态信息到文本框"""
        self.status_text.config(state="normal")
        self.status_text.insert("end", message + "\n")
        self.status_text.see("end")
        self.status_text.config(state="disabled")
        self.root.update()

    def choose_directory(self):
        folder = filedialog.askdirectory(title="选择保存目录")
        if folder:
            self.output_dir_var.set(folder)
            self.append_status(f"✓ 保存位置已更改: {folder}")

    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("错误", "请输入 YouTube 链接")
            return

        output_dir = self.output_dir_var.get().strip()
        if not output_dir:
            messagebox.showerror("错误", "请选择保存目录")
            return

        os.makedirs(output_dir, exist_ok=True)
        self.is_downloading = True
        self.download_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        
        threading.Thread(
            target=self.download_task, 
            args=(url, output_dir), 
            daemon=True
        ).start()

    def cancel_download(self):
        self.is_downloading = False
        self.append_status("⏹️ 用户取消了下载")
        self.download_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")

    def download_task(self, url, output_dir):
        try:
            import yt_dlp
            
            self.append_status(f"📥 开始下载: {url}")
            self.progress["value"] = 0
            self.percent_label.config(text="0%")

            # 选择格式
            if "仅音频" in self.quality_var.get():
                format_spec = "bestaudio/best"
                self.append_status("🎵 选择格式: MP3 音频")
            elif "1080" in self.quality_var.get():
                format_spec = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
                self.append_status("📺 选择格式: 1080p 高清")
            elif "720" in self.quality_var.get():
                format_spec = "bestvideo[height<=720]+bestaudio/best[height<=720]"
                self.append_status("📺 选择格式: 720p")
            else:
                format_spec = "bestvideo[height<=480]+bestaudio/best[height<=480]"
                self.append_status("📺 选择格式: 480p")

            def progress_hook(d):
                if not self.is_downloading:
                    raise Exception("用户取消下载")
                    
                if d['status'] == 'downloading':
                    total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                    downloaded = d.get('downloaded_bytes', 0)
                    if total > 0:
                        percent = (downloaded / total) * 100
                        self.progress["value"] = percent
                        self.percent_label.config(text=f"{percent:.1f}%")
                        
                        speed = d.get('_speed_str', 'N/A')
                        eta = d.get('_eta_str', 'N/A')
                        self.append_status(f"⬇️ 下载中... {percent:.1f}% | 速度: {speed} | 剩余: {eta}")
                        
                elif d['status'] == 'finished':
                    self.append_status("✓ 下载完成，正在处理...")
                    self.progress["value"] = 95
                    self.percent_label.config(text="95%")

            ydl_opts = {
                'format': format_spec,
                'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'progress_hooks': [progress_hook],
                'socket_timeout': 30,
            }

            # 如果是音频，添加后处理
            if "仅音频" in self.quality_var.get():
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
                self.append_status("🔧 将转换为 MP3 格式...")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
            self.progress["value"] = 100
            self.percent_label.config(text="100%")
            self.append_status(f"✅ 下载完成！")
            self.append_status(f"📂 保存位置: {output_dir}")
            self.append_status(f"📄 文件名: {os.path.basename(filename)}")
            
            messagebox.showinfo(
                "✅ 成功", 
                f"下载完成！\n\n文件已保存到：\n{output_dir}"
            )

        except Exception as e:
            error_msg = str(e)
            self.append_status(f"❌ 错误: {error_msg}")
            messagebox.showerror("下载失败", f"错误：\n{error_msg[:300]}")
            self.progress["value"] = 0
            self.percent_label.config(text="0%")

        finally:
            self.download_btn.config(state="normal")
            self.cancel_btn.config(state="disabled")
            self.is_downloading = False


def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
