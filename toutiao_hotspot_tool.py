import os
import re
import json
import random
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path

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


class ToutiaoHotspotWriterPro:
    def __init__(self, root):
        self.root = root
        self.root.title("今日头条爆款写作助手 Pro")
        self.root.geometry("1320x900")
        self.root.resizable(False, False)

        self.topic_var = tk.StringVar(value="娱乐热点")
        self.keywords_var = tk.StringVar(value="明星,综艺,热搜,娱乐圈,情绪")
        self.audience_var = tk.StringVar(value="年轻用户")
        self.tone_var = tk.StringVar(value="观点型")
        self.style_var = tk.StringVar(value="热点分析")
        self.length_var = tk.StringVar(value="800-1200字")
        self.output_dir_var = tk.StringVar(value=str(Path.home() / "Downloads" / "头条爆款文案"))

        self.build_ui()

    def build_ui(self):
        main = ttk.Frame(self.root, padding=16)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="🎯 今日头条爆款写作助手 Pro", font=("Microsoft YaHei", 22, "bold")).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 12)
        )
        ttk.Label(
            main,
            text="用途：热点分析、爆款标题、原创正文、封面图生成；适合娱乐、人物、热点、观点型文章的写作。",
            foreground="darkorange",
            font=("Microsoft YaHei", 10)
        ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 8))

        # 主题/关键词/受众/语气
        ttk.Label(main, text="主题：", font=("Microsoft YaHei", 11, "bold")).grid(row=2, column=0, sticky="w", padx=(0, 8), pady=(8, 4))
        ttk.Entry(main, textvariable=self.topic_var, width=38, font=("Microsoft YaHei", 10)).grid(row=2, column=1, sticky="ew", pady=(8, 4))

        ttk.Label(main, text="关键词：", font=("Microsoft YaHei", 11, "bold")).grid(row=2, column=2, sticky="w", padx=(18, 8), pady=(8, 4))
        ttk.Entry(main, textvariable=self.keywords_var, width=42, font=("Microsoft YaHei", 10)).grid(row=2, column=3, sticky="ew", pady=(8, 4))

        ttk.Label(main, text="受众：", font=("Microsoft YaHei", 11, "bold")).grid(row=3, column=0, sticky="w", padx=(0, 8), pady=(8, 4))
        ttk.Combobox(main, textvariable=self.audience_var, values=["年轻用户", "职场人", "学生群体", "女性用户", "泛大众"], width=36, state="readonly").grid(row=3, column=1, sticky="ew", pady=(8, 4))

        ttk.Label(main, text="语气：", font=("Microsoft YaHei", 11, "bold")).grid(row=3, column=2, sticky="w", padx=(18, 8), pady=(8, 4))
        ttk.Combobox(main, textvariable=self.tone_var, values=["观点型", "亲和型", "悬疑型", "解读型", "情绪型"], width=36, state="readonly").grid(row=3, column=3, sticky="ew", pady=(8, 4))

        ttk.Label(main, text="风格：", font=("Microsoft YaHei", 11, "bold")).grid(row=4, column=0, sticky="w", padx=(0, 8), pady=(8, 4))
        ttk.Combobox(main, textvariable=self.style_var, values=["热点分析", "观点评论", "人物故事", "行业观察", "情绪共鸣"], width=36, state="readonly").grid(row=4, column=1, sticky="ew", pady=(8, 4))

        ttk.Label(main, text="长度：", font=("Microsoft YaHei", 11, "bold")).grid(row=4, column=2, sticky="w", padx=(18, 8), pady=(8, 4))
        ttk.Combobox(main, textvariable=self.length_var, values=["500-800字", "800-1200字", "1200-1800字", "1800-2500字"], width=36, state="readonly").grid(row=4, column=3, sticky="ew", pady=(8, 4))

        # 热搜获取与输出目录
        ttk.Label(main, text="热搜词：", font=("Microsoft YaHei", 11, "bold")).grid(row=5, column=0, sticky="w", padx=(0, 8), pady=(12, 6))
        hot_frame = ttk.Frame(main)
        hot_frame.grid(row=5, column=1, columnspan=3, sticky="ew", pady=(12, 6))
        ttk.Button(hot_frame, text="抓取热搜词", command=self.fetch_hot_searches, width=18).pack(side="left", padx=(0, 8))
        ttk.Button(hot_frame, text="填充示例词", command=self.fill_example_keywords, width=18).pack(side="left", padx=(0, 8))
        ttk.Button(hot_frame, text="清空词库", command=self.clear_keywords, width=18).pack(side="left")

        ttk.Label(main, text="输出目录：", font=("Microsoft YaHei", 11, "bold")).grid(row=6, column=0, sticky="w", padx=(0, 8), pady=(10, 8))
        dir_frame = ttk.Frame(main)
        dir_frame.grid(row=6, column=1, columnspan=3, sticky="ew", pady=(10, 8))
        ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=90, font=("Microsoft YaHei", 10)).pack(side="left", fill="x", expand=True)
        ttk.Button(dir_frame, text="浏览", command=self.choose_directory).pack(side="left", padx=(8, 0))

        # 功能按钮
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=7, column=0, columnspan=4, sticky="ew", pady=(8, 10))
        ttk.Button(btn_frame, text="1. 热点方向", command=self.generate_hotspot_direction, width=18).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="2. 爆款标题", command=self.generate_titles, width=18).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="3. A/B标题", command=self.generate_ab_titles, width=18).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="4. 原创正文", command=self.generate_article, width=18).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="5. 封面图", command=self.generate_cover, width=18).pack(side="left")

        # 结果区
        ttk.Label(main, text="生成结果：", font=("Microsoft YaHei", 11, "bold")).grid(row=8, column=0, sticky="nw", pady=(6, 6))
        self.result_box = scrolledtext.ScrolledText(main, width=130, height=20, font=("Microsoft YaHei", 10))
        self.result_box.grid(row=8, column=1, columnspan=3, sticky="nsew", pady=(6, 0))

        main.columnconfigure(1, weight=1)
        main.columnconfigure(3, weight=1)
        main.rowconfigure(8, weight=1)

    def choose_directory(self):
        folder = filedialog.askdirectory(title="选择输出目录")
        if folder:
            self.output_dir_var.set(folder)

    def append_result(self, text):
        self.result_box.insert("end", text + "\n")
        self.result_box.see("end")
        self.root.update_idletasks()

    def safe_title(self, text):
        return re.sub(r'[<>:"/\\|?*]', '_', text).strip()[:80] or "头条爆款文案"

    def clear_keywords(self):
        self.keywords_var.set("")
        self.append_result("已清空关键词。")

    def fill_example_keywords(self):
        self.keywords_var.set("明星,综艺,热搜,娱乐圈,情绪,流量,传闻,情感")
        self.append_result("已填充示例关键词。")

    def fetch_hot_searches(self):
        # 仅抓取公开热搜词，避免直接搬运侵权内容；用于选题灵感和关键词扩充
        urls = [
            "https://weibo.com/ajax/side/hotSearch",
            "https://s.weibo.com/top/summary?cate=realtimehot",
            "https://www.baidu.com/s?wd=热搜",
        ]
        words = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        for url in urls:
            try:
                r = requests.get(url, headers=headers, timeout=8)
                if r.status_code != 200:
                    continue
                text = r.text
                # 抽取可能的热搜词
                matches = re.findall(r'"word":"([^"]+)"', text)
                if matches:
                    words.extend(matches)
                if len(words) >= 12:
                    break
            except Exception:
                continue

        if not words:
            words = ["明星", "综艺", "热搜", "娱乐圈", "行业观察", "情绪共鸣", "话题传播", "流量密码", "争议", "爆料", "合作"]

        unique = []
        seen = set()
        for w in words:
            w = re.sub(r'\\u[0-9a-fA-F]{4}', '', w).strip()
            if w and w not in seen and len(w) < 18:
                unique.append(w)
                seen.add(w)
            if len(unique) >= 12:
                break

        self.keywords_var.set(", ".join(unique))
        self.append_result("已更新热搜词：" + ", ".join(unique))

    def generate_hotspot_direction(self):
        topic = self.topic_var.get().strip() or "娱乐热点"
        keywords = [k.strip() for k in self.keywords_var.get().split(',') if k.strip()]
        audience = self.audience_var.get()
        tone = self.tone_var.get()

        direction_list = [
            f"{topic}为什么持续走热？真正的关键不是热闹，而是是否切中了读者的情绪与认知。",
            f"对{audience}来说，{topic}能否爆发，不取决于信息量，而在于是否让人产生‘我也有同感’的冲动。",
            f"在{topic}的传播中，真正让人停留的，并不是事件本身，而是它背后的情绪逻辑和讨论空间。",
            f"如果做{topic}内容，重点不要堆砌事实，而是把热点转成‘可讨论、可评论、可转发’的观点。",
            f"从传播心理看，{topic}能爆火，本质上都是因为它扎中了用户的情绪、表达欲和认同欲。",
        ]

        result = "热点方向建议\n" + "=" * 60 + "\n"
        result += "\n".join([f"{i+1}. {d}" for i, d in enumerate(direction_list)]) + "\n\n"
        result += "写作建议：\n"
        result += f"- 关键词：{', '.join(keywords[:5]) if keywords else topic}\n"
        result += f"- 受众：{audience}\n"
        result += f"- 语气：{tone}\n"
        result += "- 结构：问题导入 -> 现象观察 -> 原因分析 -> 观点总结 -> 情绪收束\n"

        self.result_box.delete("1.0", "end")
        self.append_result(result)

    def generate_titles(self):
        topic = self.topic_var.get().strip() or "娱乐热点"
        keywords = [k.strip() for k in self.keywords_var.get().split(',') if k.strip()]
        tone = self.tone_var.get()
        style = self.style_var.get()
        keyword_text = " | ".join(keywords[:4]) if keywords else topic

        title_templates = [
            f"{topic}为什么突然火了？真正的关键，不只是热闹，而是它触碰了什么情绪",
            f"{topic}持续热议的背后：不在于信息本身，而在于它让人想继续讨论",
            f"一条{topic}热点，为什么总让人停留？因为它击中了人们想表达的那种情绪",
            f"{topic}不是简单的事件，而是一场关于情绪与认同感的传播事件",
            f"{keyword_text}：为什么这类内容总能形成强讨论？",
            f"{topic}火了的根本原因：它解决了用户什么心理和情绪需求",
            f"{topic}为什么总能引发讨论？真正决定传播的，不是‘见过’，而是‘有共鸣’",
            f"在{topic}的热度背后，真正让人愿意转发的，是内容里的情绪和观点",
            f"{topic}为什么容易被记住？因为它告诉人们一个想被表达的答案",
            f"{topic}不只是热点，它更像一场情绪共鸣的传播",
        ]

        if tone == "观点型":
            title_templates = [
                f"{topic}为什么总能引发讨论？真正的核心，不是热闹，而是情绪连接",
                f"{topic}真正的传播力，来自于它有没有让人产生‘我也有同感’的冲动",
                f"{topic}为什么持续热议？不是因为信息多，而是因为它精准击中了人们的情绪",
            ] + title_templates

        random.shuffle(title_templates)
        result = "爆款标题候选\n" + "=" * 60 + "\n"
        result += "\n".join([f"{i+1}. {t}" for i, t in enumerate(title_templates[:12])]) + "\n\n"
        result += f"风格：{style}\n"
        result += f"语气：{tone}\n"
        result += "建议：标题尽量做到‘情绪 + 观点 + 讨论欲’。"
        self.result_box.delete("1.0", "end")
        self.append_result(result)

    def generate_ab_titles(self):
        topic = self.topic_var.get().strip() or "娱乐热点"
        keyword_block = ", ".join([k.strip() for k in self.keywords_var.get().split(',') if k.strip()][:4])

        title_a = f"{topic}为什么突然火了？真正的关键，不只是热闹，而是它触碰了什么情绪"
        title_b = f"{topic}背后真正的传播逻辑：不是‘看到’，而是‘感同身受’"
        title_c = f"一条{topic}热点，为什么总让人停留？因为它在讲一个大家都愿意谈的话题"
        title_d = f"{keyword_block}：这类内容为什么总能形成强讨论？"

        result = "A/B标题测试版\n" + "=" * 60 + "\n"
        result += f"A：{title_a}\n\nB：{title_b}\n\nC：{title_c}\n\nD：{title_d}\n\n"
        result += "推荐策略：优先测试 A/B，A更适合强冲突型，B更适合观点型。"
        self.result_box.delete("1.0", "end")
        self.append_result(result)

    def generate_article(self):
        topic = self.topic_var.get().strip() or "娱乐热点"
        keywords = [k.strip() for k in self.keywords_var.get().split(',') if k.strip()]
        audience = self.audience_var.get()
        tone = self.tone_var.get()
        length = self.length_var.get()
        style = self.style_var.get()

        keyword_block = ", ".join(keywords[:5]) if keywords else topic

        article = []
        article.append(f"在今天的{topic}讨论里，很多人只看到了表面的热闹，却忽略了真正推动传播的核心。")
        article.append(
            "真正决定传播力的，不是事件本身，而是它能否触发用户的情绪共鸣、表达欲和讨论欲。"
            "当一个话题能够让不同人群产生‘我也有同感’的感觉，它就已经具备了传播的基础。"
        )
        article.append("一、为什么很多热点容易被看见，却不容易被讨论")
        article.append(
            "很多内容停留在表层信息，关注的是‘发生了什么’，却忽略了‘为什么大家愿意继续谈论它’。"
            "真正有传播力的内容，往往不是单纯的信息堆砌，而是通过一个切口，把看似普通的现象，变成了大家愿意表达看法的话题。"
        )
        article.append("二、用户为什么愿意参与热度")
        article.append(
            f"对{audience}来说，内容的价值不只在于信息，更在于是否能够给他们提供一个表达的出口。"
            "当内容能触发关注、情绪回应和情感认同时，用户才会愿意停留、评论和转发。"
        )
        article.append("三、做原创内容时，不能只讲事实")
        article.append(
            f"如果围绕{keyword_block}展开写作，最关键的是不要只复制事实，而是把‘发生了什么’升级成‘为什么它值得被讨论’。"
            "也就是说，要从更高的层面解释：这件事为什么会被关注，它反映了什么现实问题，为什么值得更多人看到。"
        )
        article.append("四、写作结构：让内容更容易传播")
        article.append(
            "一个有传播力的热点文章，通常遵循‘引发好奇—解释现象—分析原因—给出观点—情绪收束’的结构。"
            "这样能让读者在阅读过程中持续保持注意力，并在结束时留下‘我也有同感’的效果。"
        )
        article.append("五、结语")
        article.append(
            f"真正有传播力的{topic}内容，不是为了堆砌事实，而是为了让读者在看完之后产生一种‘我也想说一句’的冲动。"
            "当内容既有信息价值，又有情绪价值，它就更容易被记住，被讨论，被转发。"
        )

        result = f"原创爆款正文（{style} / {tone} / {length}）\n" + "=" * 72 + "\n\n" + "\n\n".join(article)
        self.result_box.delete("1.0", "end")
        self.append_result(result)

        output_dir = self.output_dir_var.get().strip()
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{self.safe_title(topic)}_正文.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result)
        self.append_result(f"\n正文已保存：{file_path}")

    def generate_cover(self):
        topic = self.topic_var.get().strip() or "热点观察"
        output_dir = self.output_dir_var.get().strip()
        os.makedirs(output_dir, exist_ok=True)

        width, height = 1080, 1920
        img = Image.new("RGB", (width, height), color=(248, 250, 255))
        draw = ImageDraw.Draw(img)

        for x in range(0, width, 150):
            draw.rectangle((x, 0, x + 60, height), fill=(234, 240, 255))

        title = topic[:18]
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 82)
        except Exception:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), title, font=font)
        text_w = bbox[2] - bbox[0]
        text_x = (width - text_w) / 2
        draw.text((text_x, 430), title, font=font, fill=(18, 18, 18))

        try:
            sub_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 38)
        except Exception:
            sub_font = ImageFont.load_default()

        draw.text((255, 620), "热点观察 × 原创表达", fill=(118, 124, 137), font=sub_font)
        draw.rounded_rectangle((150, 760, 930, 900), radius=30, fill=(255, 146, 100))
        draw.text((260, 790), "原创内容 × 传播更有力量", fill=(255, 255, 255), font=sub_font)

        cover_path = os.path.join(output_dir, f"{self.safe_title(topic)}_封面图.png")
        img.save(cover_path)

        self.append_result(f"封面图已生成：{cover_path}")
        messagebox.showinfo("成功", f"封面图已保存到：\n{cover_path}")


def main():
    root = tk.Tk()
    app = ToutiaoHotspotWriterPro(root)
    root.mainloop()


if __name__ == "__main__":
    main()
