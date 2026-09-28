import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

# 自动安装依赖
def ensure_dependencies():
    required = ['pytube']
    for package in required:
        try:
            __import__(package)
        except ImportError:
            messagebox.showinfo("提示", f"正在安装 {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])

ensure_dependencies()

from pytube import YouTube
from pytube.exceptions import PytubeError


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube 视频下载器 v2.0")
        self.root.geometry("900x600")
        self.root.resizable(False, False)

        self.url_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(
            value=str(Path.home() / "Downloads" / "YouTube视频")
        )
        self.quality_var = tk.StringVar(value="最高质量")

        self.build_ui()

    def build_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="🎬 YouTube 视频下载器 v2.0", 
            font=("Microsoft YaHei", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 说明文字
        info_label = ttk.Label(
            main_frame,
            text="支持视频下载 | 完全中文界面 | 简单易用",
            font=("Microsoft YaHei", 10),
            foreground="gray"
        )
        info_label.grid(row=1, column=0, columnspan=3, pady=(0, 15))

        # 视频链接
        ttk.Label(main_frame, text="YouTube 链接：", font=("Microsoft YaHei", 11, "bold")).grid(
            row=2, column=0, sticky="w", pady=(0, 5)
        )
        ttk.Entry(main_frame, textvariable=self.url_var, width=90, font=("Microsoft YaHei", 10)).grid(
            row=2, column=1, columnspan=2, sticky="ew", pady=(0, 15)
        )

        # 保存位置
        ttk.Label(main_frame, text="保存位置：", font=("Microsoft YaHei", 11, "bold")).grid(
            row=3, column=0, sticky="w", pady=(0, 5)
        )
        ttk.Entry(main_frame, textvariable=self.output_dir_var, width=70, font=("Microsoft YaHei", 10)).grid(
            row=3, column=1, sticky="ew", pady=(0, 15)
        )
        ttk.Button(main_frame, text="📁 浏览", command=self.choose_directory, width=10).grid(
            row=3, column=2, sticky="ew", padx=(10, 0), pady=(0, 15)
        )

        # 质量选择
        ttk.Label(main_frame, text="下载质量：", font=("Microsoft YaHei", 11, "bold")).grid(
            row=4, column=0, sticky="w", pady=(0, 5)
        )
        self.quality_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.quality_var,
            values=["最高质量 (1080p+)", "高质量 (720p)", "中等质量 (480p)", "低质量 (360p)"],
            state="readonly", 
            width=40,
            font=("Microsoft YaHei", 10)
        )
        self.quality_combo.grid(row=4, column=1, sticky="w", pady=(0, 20))

        # 下载按钮
        download_btn = ttk.Button(
            main_frame, 
            text="⬇️ 开始下载", 
            command=self.start_download,
            width=30
        )
        download_btn.grid(row=5, column=0, columnspan=3, pady=(0, 15), sticky="ew")

        # 进度条
        self.progress = ttk.Progressbar(
            main_frame, 
            orient="horizontal", 
            mode="determinate",
            length=800
        )
        self.progress.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(0, 10))

        # 进度百分比
        self.percent_label = ttk.Label(
            main_frame, 
            text="0%", 
            font=("Microsoft YaHei", 10, "bold")
        )
        self.percent_label.grid(row=7, column=0, columnspan=3, sticky="w", pady=(0, 10))

        # 状态信息
        self.status_var = tk.StringVar(value="✓ 就绪，请输入 YouTube 链接")
        status_label = ttk.Label(
            main_frame, 
            textvariable=self.status_var, 
            wraplength=800,
            justify="left", 
            font=("Microsoft YaHei", 10),
            foreground="blue"
        )
        status_label.grid(row=8, column=0, columnspan=3, sticky="ew", pady=(0, 0))

        main_frame.columnconfigure(1, weight=1)

    def choose_directory(self):
        folder = filedialog.askdirectory(title="选择保存目录")
        if folder:
            self.output_dir_var.set(folder)

    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("错误", "请输入 YouTube 链接")
            return

        if not url.startswith(("http://", "https://")):
            url = "https://www.youtube.com/watch?v=" + url
            self.url_var.set(url)

        output_dir = self.output_dir_var.get().strip()
        if not output_dir:
            messagebox.showerror("错误", "请选择保存目录")
            return

        os.makedirs(output_dir, exist_ok=True)
        threading.Thread(
            target=self.download_task, 
            args=(url, output_dir), 
            daemon=True
        ).start()

    def get_quality_filter(self):
        quality = self.quality_var.get()
        if "1080" in quality:
            return 1080
        elif "720" in quality:
            return 720
        elif "480" in quality:
            return 480
        else:
            return 360

    def download_task(self, url, output_dir):
        self.status_var.set("⏳ 正在解析视频信息...")
        self.progress["value"] = 0
        self.percent_label.config(text="0%")

        try:
            # 创建 YouTube 对象
            self.status_var.set("⏳ 连接到 YouTube...")
            yt = YouTube(url)

            self.status_var.set(f"📺 标题：{yt.title}")
            self.progress["value"] = 20
            self.percent_label.config(text="20%")

            # 获取流
            quality_filter = self.get_quality_filter()
            streams = yt.streams.filter(
                progressive=True,  # 包含视频和音频
                file_extension='mp4'
            ).order_by('resolution')

            if not streams:
                self.status_var.set("⚠️ 无可用流，尝试其他方式...")
                streams = yt.streams.order_by('resolution')

            # 选择最接近的质量
            best_stream = None
            for stream in streams:
                if stream.resolution:
                    res = int(stream.resolution.rstrip('p'))
                    if res <= quality_filter:
                        best_stream = stream
                    else:
                        break

            if not best_stream:
                best_stream = streams.last()

            if not best_stream:
                raise Exception("找不到可下载的视频流")

            self.status_var.set(f"⬇️ 下载中... 分辨率: {best_stream.resolution or 'unknown'}")
            self.progress["value"] = 40
            self.percent_label.config(text="40%")

            # 下载
            filename = best_stream.download(
                output_path=output_dir,
                filename=f"{yt.title[:50]}.mp4"
            )

            self.progress["value"] = 90
            self.percent_label.config(text="90%")
            self.status_var.set("✓ 处理中...")

            self.progress["value"] = 100
            self.percent_label.config(text="100%")
            self.status_var.set("✅ 下载完成！")
            messagebox.showinfo(
                "成功", 
                f"下载完成！\n\n文件名: {os.path.basename(filename)}\n\n保存位置: {output_dir}"
            )

        except PytubeError as e:
            error_msg = str(e)
            self.status_var.set(f"❌ YouTube 错误")
            messagebox.showerror("下载失败", f"YouTube 错误：\n{error_msg[:200]}")
            self.progress["value"] = 0
            self.percent_label.config(text="0%")

        except Exception as e:
            error_msg = str(e)
            self.status_var.set(f"❌ 错误：{error_msg[:50]}")
            messagebox.showerror("下载失败", f"错误：\n{error_msg[:300]}")
            self.progress["value"] = 0
            self.percent_label.config(text="0%")


def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
