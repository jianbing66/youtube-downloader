import os
import re
import json
import random
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

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
        self.root.title("今日头条爆款写作助手 - 原创安全版 Pro")
        self.root.geometry("1280x860")
        self.root.resizable(False, False)

        self.topic_var = tk.StringVar(value="娱乐热点")
        self.keywords_var = tk.StringVar(value="明星,综艺,热搜,娱乐圈,情绪")
        self.audience_var = tk.StringVar(value="年轻用户")
        self.tone_var = tk.StringVar(value="观点型")
        self.style_var = tk.StringVar(value="热点分析")
        self.length_var = tk.StringVar(value="800-1200字")
        self.reference_var = tk.StringVar(value="手动输入参考素材：公开新闻、用户评论、行业趋势、自己的观察")

        self.output_dir_var = tk.StringVar(value=str(Path.home() / "Downloads" / "头条爆款文案"))

        self.build_ui()

    def build_ui(self):
        main = ttk.Frame(self.root, padding=16)
        main.pack(fill="both", expand=True)

        headline = ttk.Label(main, text="🎯 今日头条爆款写作助手 Pro", font=("Microsoft YaHei", 20, "bold"))
        headline.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 12))

        info = ttk.Label(
            main,
            text="说明：本工具用于热点分析、标题优化、原创文案结构设计和封面图生成，不直接搬运侵权内容，不直接伪造平台发布。",
            foreground="darkorange",
            font=("Microsoft YaHei", 10)
        )
        info.grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 8))

        # 输入字段
        ttk.Label(main, text="主题：", font=("Microsoft YaHei", 11, "bold")).grid(row=2, column=0, sticky="w", padx=(0, 8), pady=(8, 4))
        ttk.Entry(main, textvariable=self.topic_var, width=40, font=("Microsoft YaHei", 10)).grid(row=2, column=1, sticky="ew", pady=(8, 4))

        ttk.Label(main, text="关键词：", font=("Microsoft YaHei", 11, "bold")).grid(row=2, column=2, sticky="w", padx=(20, 8), pady=(8, 4))
        ttk.Entry(main, textvariable=self.keywords_var, width=40, font=("Microsoft YaHei", 10)).grid(row=2, column=3, sticky="ew", pady=(8, 4))

        ttk.Label(main, text="受众：", font=("Microsoft YaHei", 11, "bold")).grid(row=3, column=0, sticky="w", padx=(0, 8), pady=(8, 4))
        ttk.Combobox(main, textvariable=self.audience_var, values=["年轻用户", "职场人", "学生群体", "女性用户", "泛大众"], width=38, state="readonly").grid(row=3, column=1, sticky="ew", pady=(8, 4))

        ttk.Label(main, text="语气：", font=("Microsoft YaHei", 11, "bold")).grid(row=3, column=2, sticky="w", padx=(20, 8), pady=(8, 4))
        ttk.Combobox(main, textvariable=self.tone_var, values=["观点型", "亲和型", "悬疑型", "解读型", "情绪型"], width=38, state="readonly").grid(row=3, column=3, sticky="ew", pady=(8, 4))

        ttk.Label(main, text="写作风格：", font=("Microsoft YaHei", 11, "bold")).grid(row=4, column=0, sticky="w", padx=(0, 8), pady=(8, 4))
        ttk.Combobox(main, textvariable=self.style_var, values=["热点分析", "观点评论", "人物故事", "行业观察", "情绪共鸣"], width=38, state="readonly").grid(row=4, column=1, sticky="ew", pady=(8, 4))

        ttk.Label(main, text="长度：", font=("Microsoft YaHei", 11, "bold")).grid(row=4, column=2, sticky="w", padx=(20, 8), pady=(8, 4))
        ttk.Combobox(main, textvariable=self.length_var, values=["500-800字", "800-1200字", "1200-1800字", "1800-2500字"], width=38, state="readonly").grid(row=4, column=3, sticky="ew", pady=(8, 4))

        # 参考素材
        ttk.Label(main, text="参考素材：", font=("Microsoft YaHei", 11, "bold")).grid(row=5, column=0, sticky="nw", padx=(0, 8), pady=(12, 4))
        self.reference_box = scrolledtext.ScrolledText(main, width=90, height=7, font=("Microsoft YaHei", 9))
        self.reference_box.grid(row=5, column=1, columnspan=3, sticky="nsew", pady=(12, 4))
        self.reference_box.insert("1.0", "例如：\n- 公开新闻标题\n- 用户围绕事件的讨论\n- 你自己的观察和经验\n- 热点关键词\n- 你在平台看到的内容方向\n")

        # 输出目录
        ttk.Label(main, text="输出目录：", font=("Microsoft YaHei", 11, "bold")).grid(row=6, column=0, sticky="w", padx=(0, 8), pady=(12, 8))
        dir_frame = ttk.Frame(main)
        dir_frame.grid(row=6, column=1, columnspan=3, sticky="ew", pady=(12, 8))
        ttk.Entry(dir_frame, textvariable=self.output_dir_var, width=60, font=("Microsoft YaHei", 10)).pack(side="left", fill="x", expand=True)
        ttk.Button(dir_frame, text="浏览", command=self.choose_directory).pack(side="left", padx=(8, 0))

        # 按钮
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=7, column=0, columnspan=4, sticky="ew", pady=(8, 10))
        ttk.Button(btn_frame, text="1. 热点方向", command=self.generate_hotspot_direction, width=18).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="2. 爆款标题", command=self.generate_titles, width=18).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="3. 原创正文", command=self.generate_article, width=18).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="4. 封面图", command=self.generate_cover, width=18).pack(side="left")

        # 结果框
        ttk.Label(main, text="生成结果：", font=("Microsoft YaHei", 11, "bold")).grid(row=8, column=0, sticky="nw", pady=(4, 6))
        self.result_box = scrolledtext.ScrolledText(main, width=130, height=18, font=("Microsoft YaHei", 10))
        self.result_box.grid(row=8, column=1, columnspan=3, sticky="nsew", pady=(4, 0))

        main.columnconfigure(1, weight=1)
        main.columnconfigure(3, weight=1)
        main.rowconfigure(8, weight=1)

    def choose_directory(self):
        folder = filedialog.askdirectory(title="选择保存目录")
        if folder:
            self.output_dir_var.set(folder)

    def append_result(self, text):
        self.result_box.insert("end", text + "\n")
        self.result_box.see("end")
        self.root.update_idletasks()

    def safe_title(self, text):
        return re.sub(r'[<>:"/\\|?*]', '_', text).strip()[:80] or "头条爆款文案"

    def generate_hotspot_direction(self):
        topic = self.topic_var.get().strip() or "娱乐热点"
        keywords = [k.strip() for k in self.keywords_var.get().split(',') if k.strip()]
        audience = self.audience_var.get()
        tone = self.tone_var.get()

        direction_list = [
            f"{topic}为什么能持续走热？关键不在‘热闹’，而在于它触碰了什么情绪和认知。",
            f"对{audience}来说，{topic}真正的爆点，不是信息量，而是‘我有什么共鸣’的感觉。",
            f"在{topic}的传播中，真正让人停下来的不是事实，而是话题背后的情绪逻辑和解释空间。",
            f"从传播心理看，{topic}能迅速爆发，往往因为它满足了用户的表达欲、讨论欲和认同欲。",
            f"如果要做{topic}内容，重点不是堆砌信息，而是把热点转化为‘可以讨论、可以评论、可以转发’的观点。",
        ]

        result = "热点方向建议\n" + "=" * 60 + "\n"
        result += "\n".join([f"{i+1}. {d}" for i, d in enumerate(direction_list)]) + "\n\n"
        result += "写作建议：\n"
        result += f"- 重点关键词：{', '.join(keywords[:5]) if keywords else topic}\n"
        result += f"- 受众画像：{audience}\n"
        result += f"- 语气策略：{tone}\n"
        result += "- 内容结构：现象 -> 讨论 -> 观点 -> 情绪 -> 结论\n"

        self.result_box.delete("1.0", "end")
        self.append_result(result)

    def generate_titles(self):
        topic = self.topic_var.get().strip() or "娱乐热点"
        keywords = [k.strip() for k in self.keywords_var.get().split(',') if k.strip()]
        tone = self.tone_var.get()
        style = self.style_var.get()

        keyword_text = " | ".join(keywords[:4]) if keywords else topic
        title_templates = [
            f"{topic}为什么突然火了？真正的关键不只是热闹，而是它触碰了什么情绪",
            f"{topic}背后真正的传播逻辑：为什么它能让人停留、评论、转发",
            f"一条{topic}热点为什么能走红？不在于信息，而在于它满足了什么心理需求",
            f"{topic}不是单纯的话题，而是一场围绕情绪和认同感的传播事件",
            f"{keyword_text}：为什么这类内容总能形成强讨论？",
            f"{topic}的爆点不在“事件”，而在“人们为什么愿意谈论它”",
            f"{topic}为何总能引发讨论？关键不是‘看到’，而是‘感同身受’",
            f"别再只看{topic}的表面：真正决定传播的，是你是否看到了情绪共鸣",
            f"{topic}火起来的秘密：它抓住的不是热点，而是人们的“想表达”",
            f"{topic}为什么能形成持续传播？因为它把一个普通事件，变成了大家愿意讨论的话题",
        ]

        if tone == "观点型":
            title_templates = [
                f"{topic}为什么总能引发讨论？真正的核心，不是热闹，而是情绪连接",
                f"{topic}真正的传播力，来自于它有没有让人产生‘我也有同感’的冲动",
                f"{topic}为什么能持续热议？不是因为信息多，而是因为它精准击中了人们的情绪",
            ] + title_templates
        elif tone == "情绪型":
            title_templates = [
                f"看完{topic}，为什么很多人会忍不住评论？因为它触发的，不只是热闹，而是情绪共鸣",
                f"{topic}火起来的真正原因：它让人看到了别人也在经历的那个瞬间",
            ] + title_templates

        random.shuffle(title_templates)
        result = "爆款标题候选\n" + "=" * 60 + "\n"
        result += "\n".join([f"{i+1}. {t}" for i, t in enumerate(title_templates[:12])]) + "\n\n"
        result += f"风格：{style}\n"
        result += f"语气：{tone}\n"
        result += "建议：标题尽量做到‘情绪 + 观点 + 讨论欲’。"
        self.result_box.delete("1.0", "end")
        self.append_result(result)

    def generate_article(self):
        topic = self.topic_var.get().strip() or "娱乐热点"
        keywords = [k.strip() for k in self.keywords_var.get().split(',') if k.strip()]
        audience = self.audience_var.get()
        tone = self.tone_var.get()
        style = self.style_var.get()
        length = self.length_var.get()
        reference = self.reference_box.get("1.0", "end").strip()

        if reference and "例如：" in reference:
            reference = reference.split("例如：", 1)[1].strip()

        keyword_block = ", ".join(keywords[:5]) if keywords else topic

        article = []
        article.append(f"在今天的{topic}讨论里，很多人只看到了表面的热闹，却忽略了真正让内容持续扩散的核心。")
        article.append(
            "真正决定传播力的，不是事件本身，而是它是否触发了用户的情绪共鸣、表达欲和讨论欲。"
            "当一个话题能够让不同人群产生‘我也有同感’的感觉，它就已经具备了传播的基础。"
        )
        article.append("一、为什么很多热点容易被看见，却很难被讨论起来")
        article.append(
            "很多内容停留在表层信息，重点看的是‘发生了什么’，但忽略了‘为什么大家愿意继续谈论它’。"
            "真正有传播力的内容，往往不是单纯的信息堆砌，而是通过一个角度，把看似普通的现象，变成了大家愿意表达看法的话题。"
        )
        article.append("二、用户为什么愿意参与热度")
        article.append(
            f"对{audience}来说，内容的价值不只在于信息，更在于是否能给他们提供一个表达的出口。"
            "当内容能够触发关注、情绪回应和共鸣时，用户才会愿意停留下来，甚至在评论区参与讨论。"
        )
        article.append("三、做原创内容时，不能只讲事实")
        article.append(
            f"如果我们围绕{keyword_block}展开写作，最重要的是不要只复制事实，而是把‘发生了什么’升级成‘为什么它值得被讨论’。"
            "也就是说，要从一个更高的层面解释：这件事为什么是现在被讨论的，它反映了什么现实问题，为什么值得被更多人看到。"
        )
        if reference:
            article.append(f"结合你整理的参考素材：{reference[:500]}。这类信息可以作为叙事切入点，但真正形成爆款的关键，不是信息堆叠，而是观点和情绪的切入。")
        article.append("四、写作结构：让内容更容易传播")
        article.append(
            "一个好的热点文章，通常要遵循‘引发好奇—解释现象—分析原因—给出观点—落到情绪共鸣’的结构。"
            "这样能让读者在阅读过程中持续保持注意力，并在结束时留下‘我也有同感’的效果。"
        )
        article.append("五、结语")
        article.append(
            f"真正有传播力的{topic}内容，不是为了“塞满事实”，而是为了让读者在看完之后，产生一种‘我也想说一句’的冲动。"
            "当内容既有信息价值，又有情绪价值，就更容易被转发、被评论、被记住。"
        )

        article_text = "\n\n".join(article)
        header = "原创爆款正文（头条风格）\n" + "=" * 70 + "\n\n"
        result = header + article_text

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

        # 背景装饰
        for x in range(0, width, 140):
            draw.rectangle((x, 0, x + 60, height), fill=(234, 240, 255))

        # 标题
        title = topic[:18]
        try:
            title_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 85)
        except Exception:
            title_font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
        tx = (width - tw) / 2
        draw.text((tx, 440), title, font=title_font, fill=(18, 18, 18))

        subtitle = "热点观察 × 原创表达"
        try:
            sub_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 40)
        except Exception:
            sub_font = ImageFont.load_default()
        draw.text((260, 615), subtitle, fill=(118, 124, 137), font=sub_font)

        draw.rounded_rectangle((150, 760, 930, 900), radius=32, fill=(255, 146, 100))
        draw.text((270, 790), "原创内容 × 传播更有力量", fill=(255, 255, 255), font=sub_font)

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
