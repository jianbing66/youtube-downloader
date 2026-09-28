import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    messagebox.showerror("错误", "缺少 yt-dlp 模块，正在安装...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube 视频下载器")
        self.root.geometry("800x500")
        self.root.resizable(False, False)
        
        # 设置窗口图标（可选）
        try:
            self.root.iconbitmap(default='')
        except:
            pass

        self.url_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(
            value=str(Path.home() / "Downloads" / "YouTube视频")
        )
        self.mode_var = tk.StringVar(value="video")
        self.quality_var = tk.StringVar(value="best[ext=mp4]")
        self.audio_format_var = tk.StringVar(value="mp3")

        self.build_ui()

    def build_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # 标题
        title_label = ttk.Label(
            main_frame, text="YouTube 视频下载器", 
            font=("Microsoft YaHei", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 视频链接
        ttk.Label(main_frame, text="YouTube 链接：", font=("Microsoft YaHei", 10)).grid(
            row=1, column=0, sticky="w", pady=(0, 10)
        )
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=80)
        url_entry.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(0, 10))

        # 保存路径
        ttk.Label(main_frame, text="保存位置：", font=("Microsoft YaHei", 10)).grid(
            row=2, column=0, sticky="w", pady=(0, 10)
        )
        path_entry = ttk.Entry(main_frame, textvariable=self.output_dir_var, width=60)
        path_entry.grid(row=2, column=1, sticky="ew", pady=(0, 10))
        ttk.Button(main_frame, text="浏览", command=self.choose_directory, width=8).grid(
            row=2, column=2, sticky="ew", padx=(10, 0), pady=(0, 10)
        )

        # 下载类型选择
        ttk.Label(main_frame, text="下载类型：", font=("Microsoft YaHei", 10)).grid(
            row=3, column=0, sticky="w", pady=(0, 10)
        )
        mode_frame = ttk.Frame(main_frame)
        mode_frame.grid(row=3, column=1, sticky="w", pady=(0, 10))
        ttk.Radiobutton(mode_frame, text="视频 (MP4)", variable=self.mode_var, 
                       value="video", command=self.update_options).pack(side="left", padx=5)
        ttk.Radiobutton(mode_frame, text="音频 (MP3)", variable=self.mode_var, 
                       value="audio", command=self.update_options).pack(side="left", padx=5)

        # 视频质量选择
        ttk.Label(main_frame, text="视频质量：", font=("Microsoft YaHei", 10)).grid(
            row=4, column=0, sticky="w", pady=(0, 10)
        )
        self.quality_combo = ttk.Combobox(
            main_frame, textvariable=self.quality_var,
            values=["best[ext=mp4]", "bestvideo+bestaudio", "best"],
            state="readonly", width=30
        )
        self.quality_combo.grid(row=4, column=1, sticky="w", pady=(0, 10))

        # 音频格式选择
        ttk.Label(main_frame, text="音频格式：", font=("Microsoft YaHei", 10)).grid(
            row=5, column=0, sticky="w", pady=(0, 10)
        )
        self.audio_combo = ttk.Combobox(
            main_frame, textvariable=self.audio_format_var,
            values=["mp3", "wav", "m4a", "aac"],
            state="readonly", width=30
        )
        self.audio_combo.grid(row=5, column=1, sticky="w", pady=(0, 10))

        # 下载按钮
        download_btn = ttk.Button(
            main_frame, text="开始下载", command=self.start_download
        )
        download_btn.grid(row=6, column=0, columnspan=3, pady=(20, 10), sticky="ew")

        # 进度条
        self.progress = ttk.Progressbar(
            main_frame, orient="horizontal", mode="determinate", length=600
        )
        self.progress.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(0, 10))

        # 进度百分比标签
        self.percent_label = ttk.Label(main_frame, text="0%", font=("Microsoft YaHei", 9))
        self.percent_label.grid(row=8, column=0, columnspan=3, sticky="w", pady=(0, 10))

        # 状态信息
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(
            main_frame, textvariable=self.status_var, wraplength=700,
            justify="left", font=("Microsoft YaHei", 9)
        )
        status_label.grid(row=9, column=0, columnspan=3, sticky="ew", pady=(0, 0))

        main_frame.columnconfigure(1, weight=1)

    def update_options(self):
        """根据下载类型更新选项"""
        if self.mode_var.get() == "audio":
            self.quality_combo.config(state="disabled")
            self.audio_combo.config(state="readonly")
        else:
            self.quality_combo.config(state="readonly")
            self.audio_combo.config(state="disabled")

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
            url = "https://" + url
            self.url_var.set(url)

        output_dir = self.output_dir_var.get().strip()
        if not output_dir:
            messagebox.showerror("错误", "请选择保存目录")
            return

        os.makedirs(output_dir, exist_ok=True)
        threading.Thread(target=self.download_task, args=(url, output_dir), daemon=True).start()

    def download_task(self, url, output_dir):
        self.status_var.set("正在处理中...")
        self.progress["value"] = 0
        self.percent_label.config(text="0%")

        try:
            if self.mode_var.get() == "audio":
                self.download_audio(url, output_dir)
            else:
                self.download_video(url, output_dir)
        except Exception as exc:
            self.status_var.set(f"❌ 下载失败：{str(exc)[:100]}")
            messagebox.showerror("下载失败", f"错误详情：\n{str(exc)}")
            self.progress["value"] = 0
        else:
            self.status_var.set("✓ 下载完成！")
            self.progress["value"] = 100
            self.percent_label.config(text="100%")
            messagebox.showinfo("成功", f"下载完成！\n保存位置：{output_dir}")

    def download_video(self, url, output_dir):
        opts = {
            "format": self.quality_var.get(),
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "noplaylist": False,
            "nocheckcertificate": True,
            "quiet": False,
            "no_warnings": False,
            "progress_hooks": [self.progress_hook],
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

    def download_audio(self, url, output_dir):
        opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
            "noplaylist": False,
            "nocheckcertificate": True,
            "quiet": False,
            "no_warnings": False,
            "progress_hooks": [self.progress_hook],
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.audio_format_var.get(),
                    "preferredquality": "192",
                }
            ],
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])

    def progress_hook(self, d):
        if d["status"] == "downloading":
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            if total_bytes > 0:
                percent = (downloaded / total_bytes) * 100
                self.progress["value"] = percent
                self.percent_label.config(text=f"{percent:.1f}%")
                
                # 显示速度和时间
                speed = d.get("_speed_str", "计算中...")
                eta = d.get("_eta_str", "计算中...")
                self.status_var.set(f"⬇️ 下载中... {percent:.1f}% | 速度：{speed} | 剩余时间：{eta}")
        elif d["status"] == "finished":
            self.status_var.set("处理中... 正在转换格式...")
        elif d["status"] == "error":
            self.status_var.set("⚠️ 发生错误")


def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
