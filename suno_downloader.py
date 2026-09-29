import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from pathlib import Path
import json
import re
from datetime import datetime

# 自动安装依赖
def ensure_dependencies():
    required = ['requests', 'beautifulsoup4']
    for package in required:
        try:
            __import__(package)
        except ImportError:
            print(f"正在安装 {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])

ensure_dependencies()

import requests
from bs4 import BeautifulSoup


class SunoDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Suno AI 歌曲下载器 - 完整版")
        self.root.geometry("1000x750")
        self.root.resizable(False, False)

        self.url_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(
            value=str(Path.home() / "Downloads" / "Suno歌曲")
        )
        self.download_format_var = tk.StringVar(value="MP3 + 歌词 + 元数据")

        self.is_downloading = False
        self.current_thread = None
        
        self.build_ui()

    def build_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="🎵 Suno AI 歌曲下载器 - 完整版 v3.0", 
            font=("Microsoft YaHei", 16, "bold"),
            foreground="#ff6b6b"
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # 说明文字
        info_label = ttk.Label(
            main_frame,
            text="✓ 支持 MP3 高质量下载 | ✓ 自动提取歌词 | ✓ 批量下载支持 | ✓ 完整元数据保存",
            font=("Microsoft YaHei", 10),
            foreground="green"
        )
        info_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))

        # 歌曲链接/ID
        ttk.Label(main_frame, text="🔗 歌曲链接或 ID：", font=("Microsoft YaHei", 11, "bold")).grid(
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

        # 说明
        ttk.Label(
            main_frame,
            text="💡 支持格式：https://suno.com/song/xxx | https://suno.com/s/xxx | 或直接输入 ID",
            font=("Microsoft YaHei", 9),
            foreground="gray"
        ).grid(row=3, column=0, columnspan=3, sticky="w", pady=(0, 15))

        # 保存位置
        ttk.Label(main_frame, text="📁 保存位置：", font=("Microsoft YaHei", 11, "bold")).grid(
            row=4, column=0, sticky="nw", pady=(0, 5)
        )
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=4, column=1, columnspan=2, sticky="ew", pady=(0, 15))
        ttk.Entry(path_frame, textvariable=self.output_dir_var, font=("Microsoft YaHei", 10)).pack(
            side="left", fill="both", expand=True
        )
        ttk.Button(path_frame, text="📂 浏览", command=self.choose_directory, width=8).pack(
            side="left", padx=(5, 0)
        )

        # 下载格式选择
        ttk.Label(main_frame, text="📊 下载内容：", font=("Microsoft YaHei", 11, "bold")).grid(
            row=5, column=0, sticky="w", pady=(0, 5)
        )
        self.format_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.download_format_var,
            values=[
                "MP3 + 歌词 + 元数据",
                "仅 MP3",
                "仅歌词",
                "完整信息 (JSON)"
            ],
            state="readonly", 
            width=40,
            font=("Microsoft YaHei", 10)
        )
        self.format_combo.grid(row=5, column=1, sticky="w", pady=(0, 20))

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        
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
        self.cancel_btn.pack(side="left", padx=(0, 10))

        self.open_folder_btn = ttk.Button(
            button_frame,
            text="📂 打开文件夹",
            command=self.open_output_folder,
            state="disabled",
            width=15
        )
        self.open_folder_btn.pack(side="left")

        # 进度条
        self.progress = ttk.Progressbar(
            main_frame, 
            orient="horizontal", 
            mode="determinate",
            length=900
        )
        self.progress.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(0, 5))

        # 进度百分比
        self.percent_label = ttk.Label(
            main_frame, 
            text="0%", 
            font=("Microsoft YaHei", 10, "bold")
        )
        self.percent_label.grid(row=8, column=0, columnspan=3, sticky="w", pady=(0, 10))

        # 状态信息框
        ttk.Label(main_frame, text="📝 详细日志：", font=("Microsoft YaHei", 10, "bold")).grid(
            row=9, column=0, columnspan=3, sticky="w", pady=(0, 5)
        )
        
        self.status_text = scrolledtext.ScrolledText(
            main_frame,
            height=10,
            width=115,
            font=("Courier New", 9),
            state="disabled",
            bg="#f5f5f5"
        )
        self.status_text.grid(row=10, column=0, columnspan=3, sticky="ew", pady=(0, 0))

        main_frame.columnconfigure(1, weight=1)

    def paste_url(self):
        try:
            url = self.root.clipboard_get()
            self.url_var.set(url)
            self.append_status(f"✓ 已粘贴: {url[:80]}...")
        except:
            messagebox.showerror("错误", "无法从剪贴板获取内容")

    def append_status(self, message):
        """添加状态信息到文本框"""
        self.status_text.config(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert("end", f"[{timestamp}] {message}\n")
        self.status_text.see("end")
        self.status_text.config(state="disabled")
        self.root.update()

    def choose_directory(self):
        folder = filedialog.askdirectory(title="选择保存目录")
        if folder:
            self.output_dir_var.set(folder)
            self.append_status(f"✓ 保存位置: {folder}")

    def open_output_folder(self):
        output_dir = self.output_dir_var.get()
        if os.path.exists(output_dir):
            os.startfile(output_dir)
        else:
            messagebox.showerror("错误", "文件夹不存在")

    def extract_song_id(self, url_or_id):
        """提取歌曲 ID - 支持多种格式"""
        url_or_id = url_or_id.strip()
        
        self.append_status(f"📍 尝试解析: {url_or_id[:100]}")
        
        # 移除查询参数 (如 ?time=73)
        url_or_id = url_or_id.split('?')[0]
        
        # 方法 1: /s/ 格式 (https://suno.com/s/xxxxx)
        match = re.search(r'/s/([^\s/?&#]+)', url_or_id)
        if match:
            song_id = match.group(1)
            self.append_status(f"✓ 从 /s/ 格式提取 ID: {song_id}")
            return song_id
        
        # 方法 2: /song/ 格式 (https://suno.com/song/xxxxx)
        match = re.search(r'song[/\-=]([^\s/?&#]+)', url_or_id)
        if match:
            song_id = match.group(1)
            self.append_status(f"✓ 从 /song/ 格式提取 ID: {song_id}")
            return song_id
        
        # 方法 3: /c/ 格式 (https://suno.com/c/xxxxx)
        match = re.search(r'/c/([^\s/?&#]+)', url_or_id)
        if match:
            song_id = match.group(1)
            self.append_status(f"✓ 从 /c/ 格式提取 ID: {song_id}")
            return song_id
        
        # 方法 4: 直接 ID (任何长度的字符串)
        clean_id = re.sub(r'[^a-zA-Z0-9\-_]', '', url_or_id)
        if len(clean_id) >= 10:  # ID 足够长
            self.append_status(f"✓ 识别为直接 ID: {clean_id}")
            return clean_id
        
        return None

    def start_download(self):
        url_or_id = self.url_var.get().strip()
        if not url_or_id:
            messagebox.showerror("错误", "请输入歌曲链接或 ID")
            return

        song_id = self.extract_song_id(url_or_id)
        if not song_id:
            messagebox.showerror("错误", "无法解析链接或 ID，请检查输入格式")
            return

        output_dir = self.output_dir_var.get().strip()
        if not output_dir:
            messagebox.showerror("错误", "请选择保存目录")
            return

        os.makedirs(output_dir, exist_ok=True)
        self.is_downloading = True
        self.download_btn.config(state="disabled")
        self.cancel_btn.config(state="normal")
        self.open_folder_btn.config(state="disabled")
        self.status_text.config(state="normal")
        self.status_text.delete("1.0", tk.END)
        self.status_text.config(state="disabled")
        
        self.current_thread = threading.Thread(
            target=self.download_task, 
            args=(song_id, output_dir), 
            daemon=True
        )
        self.current_thread.start()

    def cancel_download(self):
        self.is_downloading = False
        self.append_status("⏹️ 用户取消了下载")
        self.download_btn.config(state="normal")
        self.cancel_btn.config(state="disabled")

    def download_task(self, song_id, output_dir):
        try:
            self.append_status(f"🔍 正在获取歌曲信息...")
            self.append_status(f"歌曲 ID: {song_id}")
            self.progress["value"] = 10
            self.percent_label.config(text="10%")

            # 获取歌曲信息
            song_info = self.get_song_info(song_id)
            if not song_info:
                raise Exception("无法获取歌曲信息。\n\n可能原因：\n1. 歌曲 ID 不正确\n2. 歌曲已删除或私密\n3. 网络连接问题\n\n请检查：\n- 链接是否正确\n- 歌曲是否公开\n- 网络是否正常")

            title = song_info.get('title', f'suno_{song_id}')
            # 清理文件名中的非法字符
            title = re.sub(r'[<>:"/\\|?*]', '_', title)
            
            artist = song_info.get('artist', 'Suno AI')
            audio_url = song_info.get('audio_url', '')
            lyrics = song_info.get('lyrics', '')

            self.append_status(f"🎵 歌曲: {title}")
            self.append_status(f"👤 艺术家: {artist}")
            
            if not audio_url:
                self.append_status("⚠️ 警告: 未找到音频链接，尝试备用方案...")
                audio_url = self.get_audio_url_fallback(song_id)
            
            self.progress["value"] = 30
            self.percent_label.config(text="30%")

            download_format = self.download_format_var.get()

            # 下载 MP3
            if 'MP3' in download_format or '��整' in download_format:
                self.append_status("⬇️ 下载音频文件...")
                if audio_url:
                    mp3_path = os.path.join(output_dir, f"{title}.mp3")
                    self.download_file(audio_url, mp3_path)
                    self.append_status(f"✓ MP3 已保存: {mp3_path}")
                else:
                    raise Exception("无可用音频链接")

            self.progress["value"] = 60
            self.percent_label.config(text="60%")

            # 保存歌词
            if '歌词' in download_format or '完整' in download_format:
                self.append_status("📝 保存歌词...")
                if lyrics:
                    lyrics_path = os.path.join(output_dir, f"{title}_lyrics.txt")
                    with open(lyrics_path, 'w', encoding='utf-8') as f:
                        f.write(f"{title}\n{artist}\n\n{lyrics}")
                    self.append_status(f"✓ 歌词已保存: {lyrics_path}")
                else:
                    self.append_status("ℹ️ 该歌曲无歌词信息")

            self.progress["value"] = 80
            self.percent_label.config(text="80%")

            # 保存元数据
            if 'MP3' in download_format or '完整' in download_format or '元数据' in download_format:
                self.append_status("📋 保存元数据...")
                metadata_path = os.path.join(output_dir, f"{title}_info.txt")
                metadata = f"""Suno AI 歌曲信息
================
标题: {title}
艺术家: {artist}
歌曲 ID: {song_id}
下载时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

歌词:
{lyrics if lyrics else '无歌词信息'}
"""
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    f.write(metadata)
                self.append_status(f"✓ 元数据已保存: {metadata_path}")

            # 保存完整 JSON
            if '完整信息' in download_format:
                self.append_status("💾 保存完整 JSON...")
                json_path = os.path.join(output_dir, f"{title}_full_info.json")
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(song_info, f, ensure_ascii=False, indent=2)
                self.append_status(f"✓ JSON 已保存: {json_path}")

            self.progress["value"] = 100
            self.percent_label.config(text="100%")
            self.append_status("✅ 下载完成！")
            
            messagebox.showinfo(
                "✅ 成功", 
                f"歌曲下载完成！\n\n标题: {title}\n保存位置: {output_dir}"
            )

        except Exception as e:
            error_msg = str(e)
            self.append_status(f"❌ 错误: {error_msg}")
            messagebox.showerror("下载失败", f"错误：\n{error_msg}")
            self.progress["value"] = 0
            self.percent_label.config(text="0%")

        finally:
            self.download_btn.config(state="normal")
            self.cancel_btn.config(state="disabled")
            self.open_folder_btn.config(state="normal")
            self.is_downloading = False

    def get_song_info(self, song_id):
        """获取歌曲信息"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://suno.com/',
                'Accept': 'application/json',
            }
            
            # API 方法：直接调用 Suno API
            self.append_status(f"🔗 尝试通过 API 获取信息...")
            
            api_urls = [
                f"https://api.suno.ai/songs/{song_id}",
                f"https://suno.com/api/v1/songs/{song_id}",
            ]
            
            for api_url in api_urls:
                try:
                    response = requests.get(api_url, headers=headers, timeout=10)
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            self.append_status(f"✓ 成功获取 API 数据")
                            return self.parse_api_response(data, song_id)
                        except:
                            pass
                except:
                    pass
            
            # 网页方法：爬取 HTML 页面
            self.append_status(f"🔗 尝试通过网页爬取...")
            
            urls = [
                f"https://suno.com/s/{song_id}",
                f"https://suno.com/song/{song_id}",
            ]
            
            for url in urls:
                try:
                    self.append_status(f"📄 访问: {url}")
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        self.append_status(f"✓ 页面加载成功，正在解析...")
                        
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # 查找所有脚本标签中的 JSON 数据
                        scripts = soup.find_all('script')
                        for script in scripts:
                            if script.string and 'clip' in script.string.lower():
                                try:
                                    # 提取所有 JSON 块
                                    matches = re.findall(r'\{[^{}]*"audio_url"[^{}]*\}', script.string)
                                    for json_str in matches:
                                        try:
                                            data = json.loads(json_str)
                                            song_info = self.parse_api_response(data, song_id)
                                            if song_info.get('audio_url'):
                                                return song_info
                                        except:
                                            pass
                                except:
                                    pass
                        
                        # 尝试查找 audio 标签
                        audio_tag = soup.find('audio')
                        if audio_tag:
                            source_tag = audio_tag.find('source')
                            if source_tag and source_tag.get('src'):
                                self.append_status(f"✓ 从 HTML 提取音频链接")
                                return {
                                    'id': song_id,
                                    'title': soup.title.string.split('|')[0].strip() if soup.title else 'Unknown',
                                    'artist': 'Suno AI',
                                    'lyrics': '',
                                    'audio_url': source_tag['src'],
                                }
                
                except Exception as e:
                    self.append_status(f"⚠️ 访问失败: {str(e)[:50]}")
            
            return None
                
        except Exception as e:
            self.append_status(f"❌ 获取信息异常: {str(e)[:100]}")
            return None

    def parse_api_response(self, data, song_id):
        """解析 API 响应"""
        if isinstance(data, dict):
            return {
                'id': song_id,
                'title': data.get('title', data.get('name', 'Unknown')).replace('/', '_'),
                'artist': data.get('user', {}).get('name', data.get('display_name', 'Suno AI')),
                'lyrics': data.get('lyrics', data.get('prompt', data.get('metadata', {}).get('gpt_description', ''))),
                'audio_url': data.get('audio_url', data.get('download_url', '')),
            }
        return None

    def get_audio_url_fallback(self, song_id):
        """备用方法获取音频 URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            }
            
            # 尝试直接下载 URL
            fallback_urls = [
                f"https://cdn1.suno.ai/{song_id}.mp3",
                f"https://suno-prod-us-west-2-public.s3.amazonaws.com/{song_id}.mp3",
            ]
            
            for url in fallback_urls:
                try:
                    response = requests.head(url, headers=headers, timeout=5)
                    if response.status_code == 200:
                        self.append_status(f"✓ 找到备用音频链接")
                        return url
                except:
                    pass
        except:
            pass
        
        return ""

    def download_file(self, url, filepath):
        """下载文件"""
        try:
            if not url:
                raise Exception("没有有效的下载链接")
                
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://suno.com/',
            }
            
            self.append_status(f"⬇️ 开始下载音频...")
            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if not self.is_downloading:
                        os.remove(filepath)
                        return
                    
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = min(95, int((downloaded / total_size) * 100))
                            self.progress["value"] = percent
                            self.percent_label.config(text=f"{percent}%")
                            
        except Exception as e:
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
            raise Exception(f"下载失败: {str(e)}")


def main():
    root = tk.Tk()
    app = SunoDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
