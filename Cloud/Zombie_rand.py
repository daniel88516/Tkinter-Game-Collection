import tkinter as tk
from PIL import Image, ImageTk
import requests
import os

API_BASE_URL = 'https://gamesuper.fly.dev'  # 你的 Fly.io API 網址

def get_ranking_from_api(play_time=30):
    try:
        res = requests.get(f"{API_BASE_URL}/get_ranking", params={'time': play_time}, timeout=5)
        return res.json()
    except Exception as e:
        print("連線失敗：", e)
        return None 

class RankingPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="white")

        self.results = [] #資料容器

        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.selected_time = tk.IntVar(value=30)
        self.current_page = 0

        self.load_images()
        self.create_controls()
        self.display_ranking()

        self.canvas.bind("<Configure>", self.on_frame_configure)


    def load_images(self):
        base = os.path.dirname(__file__)
        bg_path = os.path.join(base, "Zombie圖片/排行榜背景.png")
        self.bg_img = Image.open(bg_path) if os.path.exists(bg_path) else None

        self.score_number_imgs = {}
        for i in range(10):
            path = os.path.join(base, f"Zombie圖片/分數數字/{i}.png")
            if os.path.exists(path):
                img = Image.open(path).resize((40, 40), Image.Resampling.LANCZOS)
                self.score_number_imgs[str(i)] = ImageTk.PhotoImage(img)

    def create_controls(self):
        rb_style = {
            "font": ("微軟正黑體", 16, "bold"),
            "bg": "#000000",
            "activebackground": "#000000",
            "highlightthickness": 0,
            "bd": 0,
            "indicatoron": 1,
            "selectcolor": "#000000"
        }

        rb_30 = tk.Radiobutton(self.canvas, text="30 秒", variable=self.selected_time, value=30,
                               command=self.reset_page, fg="#FF00FF", **rb_style)
        self.canvas.create_window(700, 50, window=rb_30, anchor="nw")

        rb_60 = tk.Radiobutton(self.canvas, text="60 秒", variable=self.selected_time, value=60,
                               command=self.reset_page, fg="#666666", **rb_style)
        self.canvas.create_window(800, 50, window=rb_60, anchor="nw")

        base = os.path.dirname(__file__)
        arrow_path = os.path.join(base, "Zombie圖片/箭頭.png")
        left_img = Image.open(arrow_path).resize((180, 180), Image.Resampling.LANCZOS)
        right_img = left_img.transpose(Image.FLIP_LEFT_RIGHT)

        self.left_tk_img = ImageTk.PhotoImage(left_img)
        self.right_tk_img = ImageTk.PhotoImage(right_img)

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        button_y = canvas_height - 260
        left_x = canvas_width / 2 - 280
        right_x = canvas_width / 2 + 240

        self.canvas.create_image(left_x, button_y, image=self.left_tk_img, anchor="nw", tags="left_arrow")
        self.canvas.create_image(right_x, button_y, image=self.right_tk_img, anchor="nw", tags="right_arrow")

        self.canvas.tag_bind("left_arrow", "<Button-1>", lambda e: self.prev_page())
        self.canvas.tag_bind("right_arrow", "<Button-1>", lambda e: self.next_page())

    def reset_page(self):
        self.current_page = 0
        self.results = get_ranking_from_api(self.selected_time.get())  # 一次性抓資料
        self.display_ranking()

    def next_page(self):
        total_records = len(self.results)  # 不再重抓 API
        per_page = 10
        max_page = max((total_records - 1) // per_page, 0)
        if self.current_page < max_page:
            self.current_page += 1
            self.display_ranking()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_ranking()

    def on_frame_configure(self, event):
        self.canvas.update_idletasks()
        self.display_ranking()

    def display_ranking(self):
        self.canvas.delete("all")

        if self.bg_img:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            bg_resized = self.bg_img.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            self.bg_tk_img = ImageTk.PhotoImage(bg_resized)
            self.canvas.create_image(0, 0, image=self.bg_tk_img, anchor="nw")

        self.create_controls()

        # 只在資料還沒抓回來時顯示「連線中」
        if self.results is None:
            self.canvas.create_text(
                self.canvas.winfo_width() / 2,
                self.canvas.winfo_height() / 2,
                text="排行榜連線中...\n請稍候。",
                font=("微軟正黑體", 24, "bold"),
                fill="#666666"
            )
            return

        # 沒有資料就直接空白，不顯示任何提示
        if not self.results:
            return

        # 正常顯示排行榜資料
        results = self.results
        per_page = 10
        start_idx = self.current_page * per_page
        end_idx = start_idx + per_page

        y_offset = 140
        row_height = 50
        canvas_width = self.canvas.winfo_width()

        page_data = results[start_idx:end_idx]
        for idx, (name, score) in enumerate(page_data, start=start_idx + 1):
            self.draw_ranking_row(idx, name, score, y_offset, canvas_width)
            y_offset += row_height

        self.canvas.configure(scrollregion=(0, 0, canvas_width, y_offset))


    def draw_ranking_row(self, rank, name, score, y_pos, canvas_width):
        rank_x = canvas_width * 0.2
        name_x = canvas_width * 0.45
        score_x = canvas_width * 0.8

        rank_str = str(rank)
        num_width = 40
        spacing = -10
        total_rank_width = len(rank_str) * num_width + (len(rank_str) - 1) * spacing
        start_rank_x = rank_x - total_rank_width // 2

        for char in rank_str:
            if char in self.score_number_imgs:
                img = self.score_number_imgs[char]
                self.canvas.create_image(start_rank_x, y_pos + 10, image=img, anchor="nw")
                start_rank_x += num_width + spacing

        self.canvas.create_text(name_x, y_pos + 20, text=name, font=("微軟正黑體", 16, "bold"), anchor="n")

        score_str = str(score)
        total_score_width = len(score_str) * num_width + (len(score_str) - 1) * spacing
        start_score_x = score_x - total_score_width // 2

        for char in score_str:
            if char in self.score_number_imgs:
                img = self.score_number_imgs[char]
                self.canvas.create_image(start_score_x, y_pos + 10, image=img, anchor="nw")
                start_score_x += num_width + spacing

if __name__ == "__main__":
    root = tk.Tk()
    root.state("zoomed")
    app = RankingPage(root)
    app.pack(fill="both", expand=True)
    root.mainloop()
