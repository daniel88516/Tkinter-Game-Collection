import tkinter as tk
from tkinter import simpledialog, messagebox, Toplevel
from PIL import Image, ImageTk
import random
import os
import sqlite3
import requests  


class CanvasZombie(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="white")

        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.LANE_COUNT = 3
        self.MAX_ROWS = 5
        self.lane_width = 200
        self.row_height = 140
        self.score = 0
        self.combo = 0
        self.game_time = 30
        self.time_left = self.game_time
        self.rows = []
        self.game_running = False
        self.can_shoot = True
        self.current_zombie_ids = [[None]*self.LANE_COUNT for _ in range(self.MAX_ROWS)]
        self.current_zombie_imgs = [[None]*self.LANE_COUNT for _ in range(self.MAX_ROWS)]
        self.combo_text_id = None 
        self.countdown_job = None
        self.countdown_animation_jobs = []

        self.score_img_ids = []  #紫色數字圖片list
        self.big_timer_img_ids = [] #紅色數字圖片list
        self.combo_img_digits = []



        #字體設定
        self.default_font = ("微軟正黑體", 20 , "bold")
        self.small_font = ("微軟正黑體", 16 , "bold")
        self.large_font = ("微軟正黑體", 24 , "bold")

        #傷人的話
        self.qiqi_quotes = [
            "連這也打不到……？",
            "你好遜喔……我要睡覺了。",
            "是不是該換人玩了？",
            "我失望了。",
            "我以為你會比較厲害……結果也不過如此。",
            "這麼簡單，也失敗了嗎？",
            "……我沒什麼好說的了。",
            "你在浪費我的復活時間。",
            "我要記錄下來，提醒自己不要再相信你了。",
            "……你真的有在看嗎？"
        ]
        self.raiden_quotes = [
            "就這？",
            "垃圾。",
            "弱得讓人想睡覺。",
            "真是浪費我的時間。",
            "你的無能讓我感到羞恥。",
            "你也配稱作戰士？",
            "蠢貨。",
            "這樣也敢站在我面前？",
            "倒不如自己了解自己的極限吧。",
            "離開吧，在你更丟人之前。"
        ]

        self.load_images()
        self.setup_canvas_elements()
        self.setup_db()

        self.bind("<KeyPress>", self.key_handler)
        self.bind("<Configure>", self.on_window_resize)
        self.canvas.bind("<Button-1>", self.mouse_click_handler)

        self.focus_set()  # 很重要！讓 Frame 接收鍵盤輸入

  

    def center_window(self, win, width=300, height=200):
        win.update_idletasks()
        x = (win.winfo_screenwidth() - width) // 2
        y = (win.winfo_screenheight() - height) // 2
        win.geometry(f"{width}x{height}+{x}+{y}")


    def setup_canvas_elements(self, mode="title"):
        self.update_idletasks()  # 確保畫面尺寸正確

        # 背景圖片
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        self.bg_id = self.canvas.create_image(canvas_w // 2, canvas_h // 2, anchor="center", image=self.bg_img)

        # 分數、時間、Combo 顯示元件
        self.timer_text_id = self.canvas.create_text(0, 0, text="", font=self.large_font, fill="white")
        self.status_text_id = self.canvas.create_text(0, 0, text="", font=("微軟正黑體", 70, "bold"), fill="red")
        self.combo_img_id = self.canvas.create_image(0, 0, anchor="n", image=None)
        self.combo_text_id = self.canvas.create_text(0, 0, text="", font=self.large_font, fill="yellow", anchor="n")

        # 七七 & 雷電將軍
        w = self.winfo_width()
        self.qiqi_id = self.canvas.create_image(w - 390, 200, anchor="nw", image=self.qiqi_img)
        self.qiqi_text_id = self.canvas.create_text(w - 200, 550, text="", font=self.large_font, fill="#BB00FF", anchor="center", width=400)
        self.raiden_id = self.canvas.create_image(140, 275, anchor="nw", image=self.raiden_img)
        self.raiden_text_id = self.canvas.create_text(250, 560, text="", font=self.large_font, fill="#0000CC", anchor="center", width=400)

        # 按鈕
        self.return_rect = self.canvas.create_rectangle(0, 0, 0, 0, fill="purple")
        self.return_text = self.canvas.create_text(0, 0, text="返回主選單", font=self.large_font, fill="plum1")
        self.button_rect = self.canvas.create_rectangle(0, 0, 0, 0, fill="purple")
        self.button_text = self.canvas.create_text(0, 0, text="開始", font=self.large_font, fill="plum1")

        self.countdown_image_id = self.canvas.create_image(self.winfo_width() // 2, self.winfo_height() // 2, anchor="center", image=None)

        # 遊戲標題只在 title 模式下顯示
        if mode == "title":
            base = os.path.dirname(__file__)
            title_img_path = os.path.join(base, "Zombie圖片/遊戲標題.png")
            raw_img = Image.open(title_img_path).resize((700, 500), Image.Resampling.LANCZOS)
            self.title_img = ImageTk.PhotoImage(raw_img)
            self.title_img_id = self.canvas.create_image(
                self.winfo_width() // 2,
                self.winfo_height() // 2 - 100,
                image=self.title_img,
                anchor="center"
            )

        self.update_button_positions(mode=mode)


    def quit_game(self):
        # 往上找到 root 視窗並正確關閉
        self.winfo_toplevel().destroy()

    def load_images(self):
        base = os.path.dirname(__file__)

        def load(path, size):
            img = Image.open(os.path.join(base, path)).resize(size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)

        # 背景
        bg_path = os.path.join(base, "Zombie圖片/背景.png")  
        bg_raw = Image.open(bg_path)
        screen_w = self.master.winfo_screenwidth()
        screen_h = self.master.winfo_screenheight()
        bg_raw = bg_raw.resize((screen_w, screen_h), Image.Resampling.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(bg_raw)

        #數字素材
        #倒數用的數字圖(紅色)
        self.number_imgs = {}
        for i in range(10):
            path = os.path.join(base, f"Zombie圖片/數字/{i}.png")
            img = Image.open(path).resize((120, 120), Image.Resampling.LANCZOS)  # 大小可調
            self.number_imgs[str(i)] = ImageTk.PhotoImage(img)
        # 分數用的數字圖(紫色)
        self.score_number_imgs = {}
        for i in range(10):
            path = os.path.join(base, f"Zombie圖片/分數數字/{i}.png")
            img = Image.open(path).resize((75, 75), Image.Resampling.LANCZOS)
            self.score_number_imgs[str(i)] = ImageTk.PhotoImage(img)
        yi_path = os.path.join(base, "Zombie圖片/分數數字/b.png")
        yi_img = Image.open(yi_path).resize((80, 80), Image.Resampling.LANCZOS)
        self.score_number_imgs["b"] = ImageTk.PhotoImage(yi_img)

        #start exit
        self.start_button_img = load("Zombie圖片/start.png", (180, 60))
        self.exit_button_img = load("Zombie圖片/exit.png", (180, 60))


        zombie_aize = 150

        self.zombie_imgs = [
            load("Zombie圖片/艾莉.png", (zombie_aize, zombie_aize)),
            load("Zombie圖片/爽世.png", (zombie_aize, zombie_aize)),
            load("Zombie圖片/芙莉蓮.png", (zombie_aize, zombie_aize))
        ]
        self.blank_img = load("Zombie圖片/空格.png", (120, 120))
        self.qiqi_img = load("Zombie圖片/七七.png", (350, 350))
        self.raiden_img = load("Zombie圖片/雷電將軍.png", (240, 240))
        self.time_icon = load("Zombie圖片/時間.png", (80, 80))
        self.score_icon = load("Zombie圖片/分數.png", (80, 80))

        self.countdown_imgs = [
            load("Zombie圖片/3.png", (400, 400)),
            load("Zombie圖片/2.png", (400, 400)),
            load("Zombie圖片/1.png", (400, 400)),
        ]

        self.times_up_img = load("Zombie圖片/times_up.png", (600, 600)) 
        self.combo_img = load("Zombie圖片/combo.png", (200, 150))
        self.x_img = load("Zombie圖片/x.png", (80, 80))

        
    def setup_db(self):
        db_path = os.path.join(os.path.dirname(__file__), "zombie_rand.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY,
                name TEXT,
                time INT,
                score INT
            )
        ''')
        self.conn.commit()

    def mouse_click_handler(self, event):
        x, y = event.x, event.y
        coords = self.canvas.coords(self.button_rect)
        if coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]:
            self.ask_game_duration()

        if hasattr(self, "return_rect"):
            return_coords = self.canvas.coords(self.return_rect)
            if return_coords[0] <= x <= return_coords[2] and return_coords[1] <= y <= return_coords[3]:
                current_text = self.canvas.itemcget(self.button_text, "text")
                if current_text == "重新開始":
                    self.reset_game_state()  # 在倒數中 or 遊戲中 → 回標題
                else:
                    self.quit_game()  # 標題畫面 → 直接退出
                return

    def ask_game_duration(self):
        def set_time(t):
            self.game_time = t
            self.time_left = self.game_time
            win.destroy()
            #消掉標題
            if hasattr(self, 'title_img_id'):
                self.canvas.delete(self.title_img_id)
            self.start_countdown()

        win = Toplevel(self)
        win.title("選擇遊戲時間")
        self.center_window(win, 400, 500)

        tk.Label(win, text="請選擇遊戲時間", font=self.large_font).pack(pady=20)

        btn_font = self.large_font
        btn_width = 12
        btn_height = 2

        # 第一個按鈕：focus_set + Enter 綁定觸發
        btn_30 = tk.Button(win, text="30 秒", font=btn_font, width=btn_width, height=btn_height,
                        command=lambda: set_time(30))
        btn_30.pack(pady=10)
        btn_30.focus_set()

        tk.Button(win, text="60 秒", font=btn_font, width=btn_width, height=btn_height,
                command=lambda: set_time(60)).pack(pady=10)
        tk.Button(win, text="自訂時間", font=btn_font, width=btn_width, height=btn_height,
                command=lambda: self.ask_custom_time(win)).pack(pady=10)
        win.bind("<Return>", lambda e: win.focus_get().invoke())

        win.grab_set()

    def ask_custom_time(self, parent):
        def submit():
            try:
                seconds = int(entry.get())
                if seconds <= 0:
                    raise ValueError
                self.game_time = seconds
                self.time_left = self.game_time
                top.destroy()
                parent.destroy()
                self.start_countdown()
            except:
                messagebox.showerror("錯誤", "請輸入有效的正整數", parent=top)

        top = tk.Toplevel(parent)
        top.withdraw()  # 先隱藏
        top.title("自訂時間")
        self.center_window(top, 400, 200)  # 置中+指定大小
        top.deiconify()  # 再顯示

        label = tk.Label(top, text="請輸入遊戲時間（秒）:", font=("微軟正黑體", 20))
        label.pack(pady=20)

        entry = tk.Entry(top, font=("微軟正黑體", 24))  # 字大一點
        entry.pack(pady=10)

        submit_button = tk.Button(top, text="確認", command=submit, font=("微軟正黑體", 18))
        submit_button.pack(pady=10)

        top.transient(parent)
        top.grab_set()
        parent.wait_window(top)

    def start_countdown(self):
        # 先清除舊東西
        if self.countdown_job:
            self.after_cancel(self.countdown_job)
            self.countdown_job = None

        for job in self.countdown_animation_jobs:
            self.after_cancel(job)
        self.countdown_animation_jobs.clear()

        if self.countdown_image_id:
            self.canvas.delete(self.countdown_image_id)
            self.countdown_image_id = None

        # 建立新圖層
        self.countdown_image_id = self.canvas.create_image(
            self.winfo_width() // 2,
            self.winfo_height() // 2,
            anchor="center",
            image=None
        )

        # data ready
        self.rows = [random.randint(0, self.LANE_COUNT - 1) for _ in range(self.MAX_ROWS)]
        for r in range(self.MAX_ROWS):
            for c in range(self.LANE_COUNT):
                self.current_zombie_imgs[r][c] = random.choice(self.zombie_imgs)

        self.combo = 0
        self.score = 0
        self.game_running = True
        self.can_shoot = False
        self.update_texts()
        self.draw_rows()

        # 倒數動畫
        self.canvas.itemconfig(self.status_text_id, text="")
        self.canvas.itemconfig(self.countdown_image_id, image=self.countdown_imgs[0])  # 顯示 "3"
        self.canvas.tag_raise(self.countdown_image_id)

        self.countdown_animation_jobs.append(
            self.after(1000, lambda: self.canvas.itemconfig(self.countdown_image_id, image=self.countdown_imgs[1]))  # 2
        )
        self.countdown_animation_jobs.append(
            self.after(2000, lambda: self.canvas.itemconfig(self.countdown_image_id, image=self.countdown_imgs[2]))  # 1
        )
        self.countdown_animation_jobs.append(
            self.after(3000, self.start_game)  # 倒數結束，開始遊戲
        )

        # 更新按鈕位置
        self.canvas.itemconfig(self.button_text, text="重新開始")
        self.update_button_positions(mode="game")



    def start_game(self):
    
         # 清除倒數圖片並刷新畫面
        def clear_countdown_image():
            self.canvas.delete(self.countdown_image_id)
            self.canvas.update_idletasks()

        self.after(1,clear_countdown_image)

        if self.countdown_job:
            self.after_cancel(self.countdown_job)
            self.countdown_job = None

        self.game_running = True
        self.can_shoot = True
        self.time_left = self.game_time
        self.canvas.itemconfig(self.status_text_id, text="")
        self.update_texts()

        self.draw_rows()
        self.countdown()
        self.canvas.itemconfig(self.button_text, text="重新開始")



    def countdown(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.update_texts()
            self.countdown_job = self.after(1000, self.countdown)
        else:
            self.game_running = False
            self.can_shoot = False
            self.canvas.itemconfig(self.status_text_id, text="")
            self.canvas.tag_raise(self.status_text_id)
            #self.canvas.itemconfig(self.big_timer_text_id, text="")  
            self.prompt_save_score(self.score, self.game_time)
    

    def draw_rows(self):
        # 一開始就清除所有圖片
        for r in range(self.MAX_ROWS):
            for c in range(self.LANE_COUNT):
                if self.current_zombie_ids[r][c]:
                    self.canvas.delete(self.current_zombie_ids[r][c])
                    self.current_zombie_ids[r][c] = None

        # 重新畫出畫面
        canvas_w = self.winfo_width()
        lane_total_width = self.LANE_COUNT * self.lane_width
        start_x = (canvas_w - lane_total_width) // 2 + (self.lane_width - 120) // 2

        for r in range(self.MAX_ROWS):
            for c in range(self.LANE_COUNT):
                x = start_x + c * self.lane_width
                y = 120 + r * self.row_height
                if self.rows[r] == c:
                    img = self.current_zombie_imgs[r][c]
                    self.current_zombie_ids[r][c] = self.canvas.create_image(x, y, anchor="nw", image=img)

    def update_texts(self):
        self.canvas.itemconfig(self.timer_text_id, text="")

        # 清除舊的倒數圖像
        for img_id in self.big_timer_img_ids:
            self.canvas.delete(img_id)
        self.big_timer_img_ids.clear()

        # ---紅色數字圖片（倒數）--- #
        digits = str(self.time_left)
        w = self.winfo_width()
        h = self.winfo_height()
        total_width = len(digits) * 90
        start_x = (w - total_width) // 2

        for i, d in enumerate(digits):
            if d in self.number_imgs:
                img = self.number_imgs[d]
                x = start_x + i * 90
                y = h // 2 - 30
                img_id = self.canvas.create_image(x, y, image=img, anchor="nw")
                self.canvas.tag_raise(img_id, self.bg_id)
                self.big_timer_img_ids.append(img_id)
        # ---紅色數字圖片--- #

        # ---紫色數字圖片（分數）--- #
        for img_id in self.score_img_ids:
            self.canvas.delete(img_id)
        self.score_img_ids.clear()

        # 判斷是否顯示為 billion
        if self.score >= 10**9:
            display_digits = str(self.score // 10**9)  # billion 
            use_b = True
        else:
            display_digits = str(self.score)
            use_b = False

        digit_width = 48
        total_width = len(display_digits) * digit_width
        if use_b:
            total_width += digit_width  # 為 b 圖留空間

        icon_x = 240  
        start_y = 140 

        total_width = len(display_digits) * digit_width
        if use_b:
            total_width += digit_width

        start_x = icon_x - total_width // 2  # 自動置中

        for i, d in enumerate(display_digits):
            if d in self.score_number_imgs:
                img = self.score_number_imgs[d]
                x = start_x + i * digit_width
                img_id = self.canvas.create_image(x, start_y, image=img, anchor="nw")
                self.score_img_ids.append(img_id)

        if use_b and "b" in self.score_number_imgs:
            b_img = self.score_number_imgs["b"]
            x = start_x + len(display_digits) * digit_width + 8  # 稍微偏右一點
            img_id = self.canvas.create_image(x, start_y, image=b_img, anchor="nw")
            self.score_img_ids.append(img_id)
        # ---紫色數字圖片--- #

    def shoot(self, column):
        if not self.can_shoot or not self.game_running:
            return
        target = self.rows[-1]
        if column == target:
            self.combo += 1
            self.score += int(1.1 ** self.combo)

            #  更新 rows 
            self.rows.pop()
            self.rows.insert(0, random.randint(0, self.LANE_COUNT - 1))

            #  同步更新 imgs
            self.current_zombie_imgs.pop()
            self.current_zombie_imgs.insert(0, [random.choice(self.zombie_imgs) for _ in range(self.LANE_COUNT)])

            # 畫面更新
            self.show_combo_effect()
            self.update_texts()

            self.animate_rows_fall(callback=self.draw_rows)
        else:
            # MISS 處理不變
            self.combo = 0
            self.miss_zombie_jump()
            self.canvas.itemconfig(self.qiqi_text_id, text=random.choice(self.qiqi_quotes))
            self.canvas.itemconfig(self.raiden_text_id, text=random.choice(self.raiden_quotes))
            self.can_shoot = False
            self.after(1000, self.reset_penalty_and_clear)
            
    def animate_rows_fall(self, callback=None, duration=500):
        fps = 120
        frame_interval = 10000 / fps  
        steps = int(duration / frame_interval)
        delta_y = self.row_height / steps

        # 先刪除最後一排殭屍（直接擊殺消失）
        for c in range(self.LANE_COUNT):
            zombie_id = self.current_zombie_ids[self.MAX_ROWS - 1][c]
            if zombie_id:
                self.canvas.delete(zombie_id)
                self.current_zombie_ids[self.MAX_ROWS - 1][c] = None

        def move_step(step):
            if step > steps:
                if callback:
                    callback()
                return
            # 除了最後一行，全部往下滑
            for r in range(self.MAX_ROWS - 1):  # 只跑到 MAX_ROWS - 2
                for c in range(self.LANE_COUNT):
                    zombie_id = self.current_zombie_ids[r][c]
                    if zombie_id:
                        self.canvas.move(zombie_id, 0, delta_y)
            self.after(int(1000 / fps), 
                       lambda: move_step(step + 1))

        move_step(1)


    
    def show_combo_effect(self):
        # 清除舊的
        for img_id in self.combo_img_digits:
            self.canvas.delete(img_id)
        self.combo_img_digits.clear()

        if hasattr(self, "combo_combo_img_id"):
            self.canvas.delete(self.combo_combo_img_id)
        if hasattr(self, "combo_x_img_id"):
            self.canvas.delete(self.combo_x_img_id)

        # combo
        x = self.winfo_width() // 2 + 400
        combo_y = 220
        self.combo_combo_img_id = self.canvas.create_image(x, combo_y, image=self.combo_img, anchor="n")
        self.canvas.tag_raise(self.combo_combo_img_id)

        # x
        combo_str = str(self.combo)
        digit_width = 48
        digit_total_width = len(combo_str) * digit_width
        x_img_x = x - digit_total_width // 2 - 10
        self.combo_x_img_id = self.canvas.create_image(x_img_x, combo_y + 90, image=self.x_img, anchor="n")
        self.canvas.tag_raise(self.combo_x_img_id)

        # 數字圖片
        combo_str = str(self.combo)
        y = 310
        digit_width = 48
        start_x = x - len(combo_str) * digit_width // 2

        for i, char in enumerate(combo_str):
            if char in self.score_number_imgs:
                img = self.score_number_imgs[char]
                img_id = self.canvas.create_image(start_x + i * digit_width, y, image=img, anchor="nw")
                self.combo_img_digits.append(img_id)

        # 小跳動畫
        row = self.MAX_ROWS - 1
        col = self.rows[-1]
        if self.current_zombie_ids[row][col]:
            self.canvas.move(self.current_zombie_ids[row][col], 0, -10)
            self.after(100, lambda: self.canvas.move(self.current_zombie_ids[row][col], 0, 10))

        # 一秒後清除
        if hasattr(self, "combo_after_id") and self.combo_after_id:
            self.after_cancel(self.combo_after_id)
        self.combo_after_id = self.after(1000, self.clear_combo_text)

            
    def clear_combo_text(self):
        for img_id in self.combo_img_digits:
            self.canvas.delete(img_id)
        self.combo_img_digits.clear()

        if hasattr(self, "combo_combo_img_id"):
            self.canvas.delete(self.combo_combo_img_id)
            self.combo_combo_img_id = None

        if hasattr(self, "combo_x_img_id"):
            self.canvas.delete(self.combo_x_img_id)
            self.combo_x_img_id = None

        self.combo_after_id = None


    def reset_penalty_and_clear(self):
        self.can_shoot = True
        self.canvas.itemconfig(self.status_text_id, text="")
        self.canvas.itemconfig(self.qiqi_text_id, text="")
        self.canvas.itemconfig(self.raiden_text_id, text="")
        self.draw_rows()

    def key_handler(self, event):
        key_map = {"Left": 0, "Down": 1, "Right": 2}
        key = event.keysym
        if key in key_map:
            self.shoot(key_map[key])
        elif key == "Return":
            # 模擬點擊開始按鈕
            coords = self.canvas.coords(self.button_rect)
            fake_event = type("Event", (), {"x": (coords[0] + coords[2]) // 2, "y": (coords[1] + coords[3]) // 2})()
            self.mouse_click_handler(fake_event)
            
    def prompt_save_score(self, score, time_mode):
        if time_mode not in [30, 60]:
            return

        def show_custom_dialog():
            result = {"name": None}

            def on_submit():
                result["name"] = name_entry.get()
                dialog.destroy()

            dialog = tk.Toplevel(self)
            dialog.title("請輸入名字")
            width, height = 400, 200
            screen_width = dialog.winfo_screenwidth()
            screen_height = dialog.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            dialog.geometry(f"{width}x{height}+{x}+{y}")

            tk.Label(dialog, text=f"恭喜您獲得 {score} 分，請輸入名字：", font=("微軟正黑體", 14)).pack(pady=20)
            name_entry = tk.Entry(dialog, font=("微軟正黑體", 16))
            name_entry.pack(pady=10, padx=20, fill="x")
            name_entry.focus_set()

            submit_btn = tk.Button(dialog, text="確定", font=("微軟正黑體", 14), command=on_submit)
            submit_btn.pack(pady=10)

            dialog.grab_set()
            self.wait_window(dialog)
            return result["name"]

        name = show_custom_dialog()
        if name:
            self.save_score_to_db(name, score, time_mode)
            self.upload_score(name, score, time_mode)  # 這裡加上

        self.reset_game_state()


    def save_score_to_db(self, name, score, play_time):
        self.cursor.execute("SELECT score FROM scores WHERE name = ? AND time = ?", (name, play_time))
        result = self.cursor.fetchone()
        if result:
            old_score = result[0]
            if score > old_score:
                self.cursor.execute("UPDATE scores SET score = ? WHERE name = ? AND time = ?", (score, name, play_time))
                msg = f"🎉 {name} 破紀錄了！（{old_score} → {score}）"
            else:
                msg = f"😅 {name} 分數比之前低，未更新紀錄（{score} ≦ {old_score}）"
        else:
            self.cursor.execute("INSERT INTO scores (name, time, score) VALUES (?, ?, ?)", (name, play_time, score))
            msg = f"✅ {name} 的新紀錄已儲存：{score} 分"

        self.cursor.execute("SELECT MAX(score) FROM scores WHERE time = ?", (play_time,))
        max_score = self.cursor.fetchone()[0]
        max_msg = f"🏆 {name} 是 {play_time} 秒模式的最高紀錄保持者！" if score >= max_score else ""

        self.conn.commit()
        messagebox.showinfo("紀錄結果", f"{msg}\n{max_msg}")
    
    def on_window_resize(self, event=None):
        self.canvas.delete("all")
        self.current_zombie_ids = [[None] * self.LANE_COUNT for _ in range(self.MAX_ROWS)]
        
        mode = "game" if self.game_running else "title"
        self.setup_canvas_elements(mode=mode)

        if self.game_running:
            self.draw_rows()
    
    def miss_zombie_jump(self):
        row = self.MAX_ROWS - 1
        col = self.rows[-1]
        zombie_id = self.current_zombie_ids[row][col]

        if not zombie_id:
            return

        total_duration = 1000  # ms
        fps = 60
        steps = int(total_duration / (1000 / fps))  # 約 60 幀
        height = 50


        # 拋物線公式[0,1]
        def easing(t):
            return -4 * height * (t - 0.5) ** 2 + height

        for i in range(steps + 1):
            t = i / steps
            delta = -easing(t)  # 產生一個「跳」的曲線位移
            self.after(int(i * (1000 / fps)), lambda d=delta: self.canvas.coords(
                zombie_id,
                self.canvas.coords(zombie_id)[0],
                120 + row * self.row_height + d
            ))

    def show_title_screen(self):
        base = os.path.dirname(__file__)
        title_img_path = os.path.join(base, "Zombie圖片/遊戲標題.png")
        raw_img = Image.open(title_img_path).resize((700,500), Image.Resampling.LANCZOS)
        self.title_img = ImageTk.PhotoImage(raw_img)
        self.title_img_id = self.canvas.create_image(
            self.winfo_width() // 2,
            self.winfo_height() // 2 -100,
            image=self.title_img,
            anchor="center"
        )
        self.canvas.itemconfig(self.button_text, text="開始")
        self.update_button_positions(mode="title")


    def reset_game_state(self):
        # 清除殭屍
        for r in range(self.MAX_ROWS):
            for c in range(self.LANE_COUNT):
                if self.current_zombie_ids[r][c]:
                    self.canvas.delete(self.current_zombie_ids[r][c])
                    self.current_zombie_ids[r][c] = None

        # 清除 分數 Combo 
        for img_id in self.score_img_ids + self.big_timer_img_ids + self.combo_img_digits:
            self.canvas.delete(img_id)
        self.score_img_ids.clear()
        self.big_timer_img_ids.clear()
        self.combo_img_digits.clear()

        # 清除 Combo 圖層
        if hasattr(self, "combo_combo_img_id") and self.combo_combo_img_id:
            self.canvas.delete(self.combo_combo_img_id)
            self.combo_combo_img_id = None
        if hasattr(self, "combo_x_img_id") and self.combo_x_img_id:
            self.canvas.delete(self.combo_x_img_id)
            self.combo_x_img_id = None

        # 清除倒數動畫  圖片 
        # 清除倒數排程
        if self.countdown_job:
            self.after_cancel(self.countdown_job)
            self.countdown_job = None

        for job in self.countdown_animation_jobs:
            self.after_cancel(job)
        self.countdown_animation_jobs.clear()

        # 刪除倒數
        if self.countdown_image_id:
            self.canvas.delete(self.countdown_image_id)
            self.countdown_image_id = None

        if hasattr(self, "times_up_image_id") and self.times_up_image_id:
            self.canvas.delete(self.times_up_image_id)
            self.times_up_image_id = None

        # 清除七七和雷電將軍的對話
        self.canvas.itemconfig(self.qiqi_text_id, text="")
        self.canvas.itemconfig(self.raiden_text_id, text="")

        # 重置
        self.rows.clear()
        self.game_running = False
        self.can_shoot = False
        self.combo = 0
        self.score = 0

        # 回主選單
        self.show_title_screen()





    def update_button_positions(self, mode="title"):
        w = self.winfo_width()
        h = self.winfo_height()

        if mode == "title":
            start_x = w // 2 - 100
            start_y = h // 2 + 150
            return_x = w // 2 - 100
            return_y = start_y + 80
        else:  
            start_x = w - 220
            start_y = h - 180
            return_x = w - 220
            return_y = h - 100

        # 更新「開始 / 重新開始」按鈕位置
        self.canvas.coords(self.button_rect, start_x, start_y, start_x + 180, start_y + 60)
        self.canvas.coords(self.button_text, start_x + 90, start_y + 30)
        self.canvas.coords(self.return_rect, return_x, return_y, return_x + 180, return_y + 60)
        self.canvas.coords(self.return_text, return_x + 90, return_y + 30)

        # 確保「返回主選單」顯示在最上層，不被任何東西遮住
        self.canvas.tag_raise(self.return_rect)
        self.canvas.tag_raise(self.return_text)

    def upload_score(self, name, score, play_time):
        url = "https://gamesuper.fly.dev/submit_score"
        data = {"name": name, "score": score, "time": play_time}
        try:
            response = requests.post(url, json=data, timeout=5)
            if response.status_code == 200:
                print("分數上傳成功")
            else:
                print("上傳失敗", response.text)
        except Exception as e:
            print("連線錯誤", e)




if __name__ == "__main__":
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    w, h = 1080, 900
    x = (screen_width - w) // 2
    y = (screen_height - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.state("zoomed")

    app = CanvasZombie(root)
    app.pack(fill="both", expand=True)
    root.mainloop()