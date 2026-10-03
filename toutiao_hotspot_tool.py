import os
import re
import json
import random
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime

# 自动安装依赖
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

try:
    from bs4 import BeautifulSoup
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4", "-q"])
    from bs4 import BeautifulSoup

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
    from PIL import Image, ImageDraw, ImageFont


class ToutiaoViralWriter:
    def __init__(self, root):
        self.root = root
        self.root.title("今日头条爆款写作助手 - 安全原创版")
        self.root.geometry("1200x800")
        self.root.resizable(False, False)

        self.topic_var = tk.StringVar(value="娱乐热点")
        self.keywords_var = tk.StringVar(value="明星,综艺,爆料,热搜,娱乐圈")
        self.reference_var = tk.StringVar(value="手动输入参考信息或复制公开新闻标题")
        self.output_dir_var = tk.StringVar(value=str(Path.home() / "Downloads" / "头条爆款文案"))

        self.build_ui()

    def build_ui(self):
        main = ttk.Frame(self.root, padding=16)
        main.pack(fill="both", expand=True)

        # 标题
        ttk.Label(main, text="🎯 今日头条爆款写作助手", font=("Microsoft YaHei", 18, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 12)
        )
        ttk.Label(
            main,
            text="说明：本工具只用于热点分析、原创选题、标题优化和文案生成，不直接抓取侵权内容或未经授权发布。",
            font=("Microsoft YaHei", 10),
            foreground="darkorange"
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 10))

        # 主题
        ttk.Label(main, text="写作主题：", font=("Microsoft YaHei", 11, "bold")).grid(row=2, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(main, textvariable=self.topic_var, width=50, font=("Microsoft YaHei", 10)).grid(row=2, column=1, sticky="ew")

        # 关键词
        ttk.Label(main, text="关键词：", font=("Microsoft YaHei", 11, "bold")).grid(row=3, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        ttk.Entry(main, textvariable=self.keywords_var, width=50, font=("Microsoft YaHei", 10)).grid(row=3, column=1, sticky="ew", pady=(10, 0))

        # 参考素材
        ttk.Label(main, text="参考素材：", font=("Microsoft YaHei", 11, "bold")).grid(row=4, column=0, sticky="nw", padx=(0, 10), pady=(10, 0))
        self.reference_box = scrolledtext.ScrolledText(main, height=8, width=65, font=("Microsoft YaHei", 9))
        self.reference_box.grid(row=4, column=1, sticky="nsew", pady=(10, 0))
        self.reference_box.insert("1.0", "例如：\n- 公开新闻标题\n- 你自己的观察\n- 用户评论热点\n- 你看到的行业趋势\n- 你自己整理的素材\n")

        # 输出目录
        ttk.Label(main, text="输出目录：", font=("Microsoft YaHei", 11, "bold")).grid(row=5, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        dir_frame = ttk.Frame(main)
        dir_frame.grid(row=5, column=1, sticky="ew", pady=(10, 0))
        ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=38, font=("Microsoft YaHei", 10)).pack(side="left", fill="x", expand=True)
        ttk.Button(dir_frame, text="浏览", command=self.choose_directory).pack(side="left", padx=(8, 0))

        # 操作按钮
        action_frame = ttk.Frame(main)
        action_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(18, 10))
        ttk.Button(action_frame, text="1. 生成热点方向", command=self.generate_hotspot_direction, width=18).pack(side="left", padx=(0, 10))
        ttk.Button(action_frame, text="2. 生成标题", command=self.generate_titles, width=18).pack(side="left", padx=(0, 10))
        ttk.Button(action_frame, text="3. 生成正文", command=self.generate_article, width=18).pack(side="left", padx=(0, 10))
        ttk.Button(action_frame, text="4. 生成封面图", command=self.generate_cover, width=18).pack(side="left")

        # 结果区
        ttk.Label(main, text="生成结果：", font=("Microsoft YaHei", 11, "bold")).grid(row=7, column=0, sticky="nw", pady=(10, 0))
        self.result_box = scrolledtext.ScrolledText(main, height=18, width=110, font=("Microsoft YaHei", 10))
        self.result_box.grid(row=7, column=1, sticky="nsew", pady=(10, 0))

        main.columnconfigure(1, weight=1)
        main.rowconfigure(7, weight=1)

    def choose_directory(self):
        folder = filedialog.askdirectory(title="选择输出目录")
        if folder:
            self.output_dir_var.set(folder)

    def append_result(self, text):
        self.result_box.insert("end", text + "\n")
        self.result_box.see("end")
        self.root.update_idletasks()

    def generate_hotspot_direction(self):
        topic = self.topic_var.get().strip()
        keywords = [k.strip() for k in self.keywords_var.get().split(',') if k.strip()]
        if not topic and not keywords:
            messagebox.showerror("错误", "请填写主题或关键词")
            return

        # 设计热点方向模板（原创选题逻辑）
        templates = [
            f"{topic}为何持续走热：从传播逻辑到用户情绪，这类内容为什么能让人停留更久",
            f"{topic}的真实热度，不是‘事件本身’，而是人们为什么愿意讨论、转发与评论",
            f"{topic}爆款内容的共性：从标题点击、观点切入到情绪设计，这三件事决定了传播幅度",
            f"{topic}为什么容易形成二次传播：用户不是在看事实，而是在看参与感和情绪价值",
            f"从{topic}的趋势看，内容要想爆款，必须解决‘看了就想转发’和‘看了就想评论’这两个点",
        ]

        result = "\n".join([
            "热点方向建议：",
            *[f"{i + 1}. {t}" for i, t in enumerate(templates[:5])],
            "",
            "选题建议：",
            f"- 结构：问题导入 -> 现象分析 -> 表层原因 -> 用户感受 -> 观点总结",
            f"- 关键词重点：{', '.join(keywords[:5]) if keywords else topic}",
            "- 传播角度：让读者产生‘我也有同感’的认同感",
        ])
        self.result_box.delete("1.0", "end")
        self.append_result(result)

    def generate_titles(self):
        topic = self.topic_var.get().strip() or "娱乐热点"
        keywords = [k.strip() for k in self.keywords_var.get().split(',') if k.strip()]
        if not keywords:
            keywords = [topic]

        # 爆款标题结构：二次传播 + 情绪 + 观点 + 冲突感
        title_patterns = [
            f"{topic}为什么突然火了？这背后藏着哪些真实原因",
            f"{topic}的真实热度，不在于话题本身，而在于它撬动了什么情绪",
            f"{topic}不能只看表面：这类内容为什么总能引发大量讨论",
            f"{topic}爆款文案的秘密：看完后，人们为什么愿意转发和评论",
            f"{topic}不是单纯的热点，它更像一场情绪共鸣的传播事件",
            f"{topic}为什么会持续占据热搜？真正的关键不是‘信息’，而是‘情绪’",
            f"{topic}背后真正的“爆点”，其实是你看到了什么却没意识到的东西",
            f"{topic}火起来的真正原因：它解决了用户什么心理和情绪需求",
        ]

        # 根据关键词生成更贴近的标题
        keyword_block = " | ".join(keywords[:4])
        extra = [
            f"{keyword_block}：从用户情绪切入，为什么这类内容总能引发讨论",
            f"{topic}为什么容易“引爆”？核心不是内容，而是它触碰了什么情绪",
            f"一条{topic}的内容，为什么能让人看完后忍不住转发？",
        ]

        title_list = title_patterns + extra
        random.shuffle(title_list)
        result = "推荐标题：\n" + "\n".join([f"{i + 1}. {t}" for i, t in enumerate(title_list[:10])])
        self.result_box.delete("1.0", "end")
        self.append_result(result)

    def generate_article(self):
        topic = self.topic_var.get().strip() or "娱乐热点"
        keywords = [k.strip() for k in self.keywords_var.get().split(',') if k.strip()]
        reference = self.reference_box.get("1.0", "end").strip()

        # 简单的原创文本生成逻辑
        intro = (
            f"在今天的{topic}热议中，很多人把注意力放在“事件本身”，却忽略了真正推动传播的原因。"
            f"实际上，真正让内容爆发的，不只是信息量，而是它是否触发了用户的情绪共鸣、参与欲和讨论欲。"
        )

        body = []
        body.append("一、先说结论")
        body.append(
            "热点内容之所以容易被大量传播，核心不在于它是否“有料”，而在于它是否让人产生一种‘我也想说一句’的冲动。"
            "当内容既有信息价值，又有情绪价值时，它才更容易被阅读、评论和转发。"
        )
        body.append("二、为什么很多内容容易失去传播力")
        body.append(
            "很多内容停留在表层信息，缺乏“观点”和“情绪层次”，因此很难形成持续传播。用户并不会只看事实，"
            "他们更关注的是：这件事是否和我的感受相符、是否有值得讨论的角度、是否能站在这个事件里找到自己的情绪出口。"
        )
        body.append("三、爆款内容的共性")
        body.append(
            "真正有传播力的内容，通常具备三点：第一，清晰的问题导入；第二，强烈的情绪连接；第三，能让读者看完后产生‘我也想聊聊’的冲动。"
            "而不是简单地堆砌事实和热词。"
        )
        body.append("四、从写作角度如何做原创")
        if reference and reference != "例如：":
            body.append(f"结合你整理的素材：{reference[:300]}。从这些信息出发，我们不需要复制事实，而是重构观点。")
        else:
            body.append(f"结合{', '.join(keywords[:3]) if keywords else topic}等关键词，写作时不要只罗列信息，而要用‘现象—分析—观点—建议’的结构，把读者带进讨论中。")
        body.append(
            "这样做的好处是：一方面提升可读性，另一方面能让内容更有个人判断和传播价值。"
            "读者不是在看信息，而是在看你如何理解事件。"
        )
        body.append("五、结语")
        body.append(
            f"一篇真正有传播力的{topic}文章，不是追求“铺天盖地的字数”，而是追求“一句话让人停留，几段判断让人继续看下去”。"
            "只要抓住用户的情绪和讨论欲，内容自然会更容易形成传播。"
        )

        article = "\n\n".join([intro, *body])

        result = "爆款正文（原创写作版）\n" + "=" * 60 + "\n\n" + article
        self.result_box.delete("1.0", "end")
        self.append_result(result)

        # 保存到文件
        output_dir = self.output_dir_var.get().strip()
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{self.topic_var.get().strip() or '爆款文案'}_正文.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result)
        self.append_result(f"\n已保存正文到：{file_path}")

    def generate_cover(self):
        topic = self.topic_var.get().strip() or "爆款内容"
        output_dir = self.output_dir_var.get().strip()
        os.makedirs(output_dir, exist_ok=True)

        width, height = 1080, 1920
        img = Image.new("RGB", (width, height), color=(245, 248, 255))
        draw = ImageDraw.Draw(img)

        # 背景装饰
        for i in range(0, width, 150):
            draw.rectangle((i, 0, i + 40, height), fill=(230, 236, 255))

        # 标题文本
        title = topic[:20]
        title = re.sub(r"[\\/:*?\"<>|]", "", title)
        font_path = None
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 80)
        except Exception:
            font = ImageFont.load_default()

        # 标题区：大字
        bbox = draw.textbbox((0, 0), title, font=font)
        text_w = bbox[2] - bbox[0]
        text_x = (width - text_w) / 2
        draw.text((text_x, 450), title, fill=(18, 18, 18), font=font)

        # 辅助文案
        sub = "热点观察 × 原创表达"
        try:
            sub_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 38)
        except Exception:
            sub_font = ImageFont.load_default()
        draw.text((250, 620), sub, fill=(110, 118, 140), font=sub_font)

        # 底部装饰条
        draw.rounded_rectangle((140, 760, 940, 900), radius=30, fill=(255, 142, 100))
        draw.text((260, 790), "原创内容 · 传播更有力量", fill=(255, 255, 255), font=sub_font)

        cover_path = os.path.join(output_dir, f"{topic}_封面图.png")
        img.save(cover_path)

        self.append_result(f"封面图已生成：{cover_path}")
        messagebox.showinfo("成功", f"封面图已生成：\n{cover_path}")


def main():
    root = tk.Tk()
    app = ToutiaoViralWriter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
