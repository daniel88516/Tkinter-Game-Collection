# CanvasZombie - UI 位置調整：統一排版與美化
import tkinter as tk
from tkinter import simpledialog, messagebox, Toplevel
from PIL import Image, ImageTk
import random
import os
import sqlite3


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


    def setup_canvas_elements(self):
        self.update_idletasks()  # 先確保畫面尺寸準確

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        self.bg_id = self.canvas.create_image(canvas_w // 2, canvas_h // 2, anchor="center", image=self.bg_img)

        w = self.winfo_width()
        h = self.winfo_height()
        center_x = w // 2
        center_y = h // 2

        #分數
        self.score_text_id = self.canvas.create_text(center_x - 400, 180, text=" 0 ", anchor="n", font=self.large_font , fill = 'white')
        self.score_icon_id = self.canvas.create_image(center_x - 400, 120, image=self.score_icon, anchor="center")

        # 時間
        self.timer_text_id = self.canvas.create_text(center_x + 400, 180, text=" 0 ", anchor="n", font=self.large_font, fill = 'white')
        self.time_icon_id = self.canvas.create_image(center_x + 400, 120, image=self.time_icon, anchor="center")

        self.status_text_id = self.canvas.create_text(center_x, center_y, text="", font=("微軟正黑體", 70, "bold"), fill="red")


        """
        # 大時間（正中央，紅色）
        self.big_timer_text_id = self.canvas.create_text(
            w // 2, h // 2,
            text="", 
            font=("微軟正黑體", 120, "bold"),
            fill="red",
            anchor="center"
        )
        """
        self.big_timer_img_ids = [] #數字圖片list

        #combo
        self.combo_text_id = self.canvas.create_text(
            center_x + 400, 220,  # 和 timer_text_id 同位置
            text="", 
            font=("微軟正黑體", 60, "bold"),
            fill="green",
            anchor="n"  # 注意！timer_text 是 anchor="n"，所以 combo也要一樣
        )

        #七七
        self.qiqi_id = self.canvas.create_image(w - 390, 200, anchor="nw", image=self.qiqi_img)
        self.qiqi_text_id = self.canvas.create_text(w -200, 550, text="", font=self.large_font, fill="#BB00FF", anchor="center", width=400)

        #雷電將軍
        self.raiden_id = self.canvas.create_image(140, 275, anchor="nw", image=self.raiden_img)
        self.raiden_text_id = self.canvas.create_text(250, 560, text="", font=self.large_font, fill="#0000CC", anchor="center", width=400)

        #開始按鈕
        self.button_rect = self.canvas.create_rectangle(w - 220, h - 100, w - 40, h - 40, fill="purple")
        self.button_text = self.canvas.create_text(w - 130, h - 70, text="開始", font=self.large_font, fill="plum1")

        #預留一個空的圖片物件放在畫面正中央。
        self.countdown_image_id = self.canvas.create_image(
            self.winfo_width() // 2,
            self.winfo_height() // 2,
            anchor="center",
            image=None
        )

    
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
        self.number_imgs = {}
        for i in range(10):
            path = os.path.join(base, f"Zombie圖片/數字/{i}.png")
            img = Image.open(path).resize((80, 120), Image.Resampling.LANCZOS)  # 大小可調
            self.number_imgs[str(i)] = ImageTk.PhotoImage(img)


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

    def ask_game_duration(self):
        def set_time(t):
            self.game_time = t
            self.time_left = self.game_time
            win.destroy()
            self.start_countdown()

        win = Toplevel(self)
        win.title("選擇遊戲時間")
        self.center_window(win, 400, 500)  # ⬅加大寬高

        tk.Label(win, text="請選擇遊戲時間", font=self.large_font).pack(pady=20)

        btn_font = self.large_font
        btn_width = 12
        btn_height = 2

        tk.Button(win, text="30 秒", font=btn_font, width=btn_width, height=btn_height,
                command=lambda: set_time(30)).pack(pady=10)
        tk.Button(win, text="60 秒", font=btn_font, width=btn_width, height=btn_height,
                command=lambda: set_time(60)).pack(pady=10)
        tk.Button(win, text="自訂時間", font=btn_font, width=btn_width, height=btn_height,
                command=lambda: self.ask_custom_time(win)).pack(pady=10)

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
        # 取消之前的倒數動畫
        for job in self.countdown_animation_jobs:
            self.after_cancel(job)
        self.countdown_animation_jobs.clear()

        # 取消之前正在跑的 countdown
        if self.countdown_job:
            self.after_cancel(self.countdown_job)
            self.countdown_job = None


        # 重建 countdown image 物件
        self.countdown_image_id = self.canvas.create_image(
            self.winfo_width() // 2,
            self.winfo_height() // 2,
            anchor="center",
            image=None
        )

        self.rows = [random.randint(0, self.LANE_COUNT - 1) for _ in range(self.MAX_ROWS)]
        for r in range(self.MAX_ROWS):
            for c in range(self.LANE_COUNT):
                self.current_zombie_imgs[r][c] = random.choice(self.zombie_imgs)
        self.combo = 0
        self.score = 0
        self.game_running = False
        self.can_shoot = False
        self.update_texts()
        self.draw_rows()  

        self.canvas.itemconfig(self.status_text_id, text="")  # 清空文字
        self.canvas.itemconfig(self.countdown_image_id, image=self.countdown_imgs[0])  # 3
        self.canvas.tag_raise(self.countdown_image_id) 
        self.countdown_animation_jobs.append(self.after(1000, lambda: self.canvas.itemconfig(self.countdown_image_id, image=self.countdown_imgs[1])))  # 2
        self.countdown_animation_jobs.append(self.after(2000, lambda: self.canvas.itemconfig(self.countdown_image_id, image=self.countdown_imgs[2])))  # 1
        self.countdown_animation_jobs.append(self.after(3000, self.start_game))



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
            self.canvas.itemconfig(self.status_text_id, text="⏰ 時間到！")
            self.canvas.tag_raise(self.status_text_id) #"時間到"浮到上面
            #self.canvas.itemconfig(self.big_timer_text_id, text="")  # 大時間清空！
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
        self.canvas.itemconfig(self.score_text_id, text=f"{self.score}")
        self.canvas.itemconfig(self.timer_text_id, text=f"{self.time_left}")
        #self.canvas.itemconfig(self.big_timer_text_id, text=f"{self.time_left}")
        # 先刪掉舊的圖片
        for img_id in self.big_timer_img_ids:
            self.canvas.delete(img_id)
        self.big_timer_img_ids.clear()

        #---數字圖片---#
        digits = str(self.time_left)
        w = self.winfo_width()
        h = self.winfo_height()
        total_width = len(digits) * 90  # 每張圖的寬度 + 間距
        start_x = (w - total_width) // 2

        for i, d in enumerate(digits):
            if d in self.number_imgs:
                img = self.number_imgs[d]
                x = start_x + i * 90
                y = h // 2 -30
                img_id = self.canvas.create_image(x, y, image=img, anchor="nw")
                self.canvas.tag_raise(img_id, self.bg_id)#要放在最背景之上其餘之下
                self.big_timer_img_ids.append(img_id)
        #---數字圖片---#

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
            self.after(int(1000 / fps), lambda: move_step(step + 1))

        move_step(1)


    
    def show_combo_effect(self):
        self.canvas.itemconfig(self.combo_text_id, text=f"x{self.combo}")

        
        # 殭屍小跳
        target_row = self.MAX_ROWS - 1
        target_col = self.rows[-1]
        if self.current_zombie_ids[target_row][target_col]:
            self.canvas.move(self.current_zombie_ids[target_row][target_col], 0, -10)
            self.after(100, lambda: self.canvas.move(self.current_zombie_ids[target_row][target_col], 0, 10))
        

        # 設定 2秒後自動清空 Combo 字
        if hasattr(self, "combo_after_id") and self.combo_after_id:
            self.after_cancel(self.combo_after_id)
        self.combo_after_id = self.after(1000, self.clear_combo_text)
    
    def clear_combo_text(self):
        self.canvas.itemconfig(self.combo_text_id, text="")
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

    def prompt_save_score(self, score, time_mode):
        if time_mode not in [30, 60]:
            return

        def show_custom_dialog():
            dialog = Toplevel(self)
            dialog.title("遊戲結束")
            self.center_window(dialog, 400, 250)  

            tk.Label(dialog, text=f"你獲得了 {score} 分！", font=self.default_font).pack(pady=10)
            tk.Label(dialog, text="請輸入你的名字：", font=self.default_font).pack()

            entry = tk.Entry(dialog, font=self.default_font, width=20)  
            entry.pack(pady=10)
            entry.focus_set()

            result = {"name": None}

            def on_ok():
                val = entry.get().strip()
                if not val:
                    messagebox.showerror("錯誤", "名字不能為空！", parent=dialog)
                    return
                result["name"] = val
                dialog.destroy()

            def on_cancel():
                dialog.destroy()

            btn_frame = tk.Frame(dialog)
            btn_frame.pack(pady=10)
            tk.Button(btn_frame, text="OK", width=10, command=on_ok).pack(side="left", padx=10)
            tk.Button(btn_frame, text="取消", width=10, command=on_cancel).pack(side="left", padx=10)

            dialog.transient(self)
            dialog.grab_set()
            self.wait_window(dialog)
            return result["name"]

        name = show_custom_dialog()
        if name:
            self.save_score_to_db(name, score, time_mode)

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
        self.canvas.delete("all")  # 把 canvas 上所有東西清乾淨
        self.current_zombie_ids = [[None]*self.LANE_COUNT for _ in range(self.MAX_ROWS)]  # 重設 zombie id
        self.setup_canvas_elements()  # 重建分數、時間、角色圖、按鈕
        if self.game_running:  # 如果遊戲正在跑，才重畫 rows
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

        def easing(t):
            # 使用簡單的拋物線公式，t ∈ [0,1]
            return -4 * height * (t - 0.5) ** 2 + height

        for i in range(steps + 1):
            t = i / steps
            delta = -easing(t)  # 產生一個「跳」的曲線位移
            self.after(int(i * (1000 / fps)), lambda d=delta: self.canvas.coords(
                zombie_id,
                self.canvas.coords(zombie_id)[0],
                120 + row * self.row_height + d
            ))

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