import random
from tkinter import *
from tkinter import simpledialog, messagebox
import sqlite3
from PIL import Image, ImageTk 
import os


class Zombie(Frame):
    def __init__(self, parent):
        super().__init__(parent) 
        self.configure(bg="white") 

        self.MAX_ROWS = 5
        self.LANE_COUNT = 3
        self.rows = []
        self.score = 0
        self.can_shoot = True
        self.game_time = 30
        self.time_left = self.game_time
        self.game_running = False
        self.combo = 0 #連擊
        self.after_id = None 
        self.current_zombie_images = [[None]*self.LANE_COUNT for _ in range(self.MAX_ROWS)]



        self.setup_ui()
        self.setup_database()
        self.bind("<KeyPress>", self.key_handler)
        self.focus_set()
        #self.root.after_idle(self.show_db_status)  #顯示資料庫以成功連接，目前不顯示


    def center_window(self, win, width=250, height=150):
        win.update_idletasks()
        x = (win.winfo_screenwidth() - width) // 2
        y = (win.winfo_screenheight() - height) // 2
        win.geometry(f"{width}x{height}+{x}+{y}")

    @staticmethod
    def get_contrasting_color(bg_hex):
        # 確保是 hex 色碼
        if bg_hex.startswith("#") and len(bg_hex) == 7:
            r = int(bg_hex[1:3], 16)
            g = int(bg_hex[3:5], 16)
            b = int(bg_hex[5:7], 16)
            # 計算亮度 (YIQ color space)
            brightness = (r*299 + g*587 + b*114) / 1000
            return "black" if brightness > 128 else "white"
        elif bg_hex.lower() == "black":
            return "white"
        elif bg_hex.lower() == "white":
            return "black"
        else:
            # fallback 預設
            return "white"
        
    def load_img(self):
        # 載入七七
        img_path = os.path.join(os.path.dirname(__file__), "Zombie圖片/七七.png")
        img = Image.open(img_path)
        img = img.resize((180, 180), Image.Resampling.LANCZOS)
        self.qiqi_img = ImageTk.PhotoImage(img)

        self.qiqi_label = Label(self, image=self.qiqi_img, bg=self["bg"], borderwidth=0)

        self.update_idletasks()
        window_width = self.winfo_width()
        x_pos = window_width - 180 - 10  # 右邊邊距
        self.qiqi_label.place(x=x_pos, y=50)

        # 載入雷電將軍
        img_path = os.path.join(os.path.dirname(__file__), "Zombie圖片/雷電將軍.png")
        img = Image.open(img_path)
        img = img.resize((140, 140), Image.Resampling.LANCZOS)
        self.raiden_img = ImageTk.PhotoImage(img)

        self.raiden_label = Label(self, image=self.raiden_img, bg=self["bg"], borderwidth=0)
        self.raiden_label.place(x=30, y=80)  # 左上角


    def setup_ui(self):

        #載入七七跟雷電
        self.load_img()

        # 顯示時間與分數欄
        info_frame = Frame(self, bg=self["bg"])
        info_frame.pack(pady=30)

        self.timer_label = Label(info_frame, text="剩餘時間: 0 秒", font=("Arial", 25),
                                fg=self.get_contrasting_color(self["bg"]),
                                bg=self["bg"])
        self.timer_label.pack(side=LEFT, padx=10)

        self.score_label = Label(info_frame, text="分數: 0", font=("Arial", 25),
                                fg=self.get_contrasting_color(self["bg"]),
                                bg=self["bg"])
        self.score_label.pack(side=LEFT, padx=10)

        self.status_label = Label(self, text="", font=("Arial", 20),
                                fg="red", bg=self["bg"])
        self.status_label.pack()


       # 載入圖片（空格 + 多個殭屍）
        zombie_files = ["Zombie圖片/艾莉.png", "Zombie圖片/爽世.png" , "Zombie圖片/芙莉蓮.png"]
        zombie_paths = [os.path.join(os.path.dirname(__file__), f) for f in zombie_files]
        blank_path = os.path.join(os.path.dirname(__file__), "Zombie圖片/空格.png")

        # 建立 zombie image list
        self.zombie_imgs = []
        for path in zombie_paths:
            img = Image.open(path).resize((100, 100), Image.Resampling.LANCZOS)
            self.zombie_imgs.append(ImageTk.PhotoImage(img))

        # 載入空格圖
        blank_img = Image.open(blank_path).resize((100, 100), Image.Resampling.LANCZOS)
        self.blank_img = ImageTk.PhotoImage(blank_img)

        # 殭屍格框
        frame = Frame(self, bg=self["bg"])
        frame.pack(pady=10)

        self.labels = [[
            Label(
                frame,
                image=self.blank_img,   # 初始都用空格圖
                relief="flat",
                bd=0,
                bg=self["bg"],
                highlightthickness=0
            )
            for _ in range(self.LANE_COUNT)]
            for _ in range(self.MAX_ROWS)
        ]

        for r in range(self.MAX_ROWS):
            for c in range(self.LANE_COUNT):
                self.labels[r][c].grid(row=r, column=c, padx=5, pady=2)

        """
        # 炮臺
        self.turrets = [
            Label(frame, text="💥", width=5, height=1, font=("Arial", 25),
                relief="flat", bd=0, highlightthickness=0, fg="orange", bg=self["bg"])
            for _ in range(self.LANE_COUNT)
        ]
     
        for c in range(self.LANE_COUNT):
            self.turrets[c].grid(row=self.MAX_ROWS, column=c, padx=5, pady=(5, 0))
        """


        # 開始按鈕
        self.start_button = Button(self, text="開始", font=("Arial", 12), width=10, height=2, command=self.ask_game_duration)
        self.start_button.pack(side=RIGHT, padx=20, pady=10)
        self.start_button.focus_set()
        self.bind("<Return>", lambda e: self.ask_game_duration())

        #為了拯救七七
        self.bind("<Configure>", self.on_window_resize)
        




    #為了拯救七七
    def on_window_resize(self, event):
        if hasattr(self, 'qiqi_label'):
            x_pos = self.winfo_width() - 180 - 10  # 固定右邊距離
            self.qiqi_label.place(x=x_pos, y=50)
            
    def setup_database(self):
        try:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zombie_rand.db")
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    time INTEGER NOT NULL,
                    score INTEGER NOT NULL
                )
            ''')
            self.conn.commit()
            self.db_connected = True
        except Exception as e:
            self.db_connected = False

    def show_db_status(self):
        if self.db_connected:
            messagebox.showinfo("資料庫狀態", "✅ 成功連接 zombie_rand.db", parent=self)
        else:
            messagebox.showerror("資料庫錯誤", "❌ 無法連接 zombie_rand.db", parent=self)

    def ask_game_duration(self):
        def set_time(seconds):
            self.game_time = seconds
            self.time_left = self.game_time
            time_select_window.destroy()
            self.countdown_start()

        def custom_time():
            try:
                value = simpledialog.askstring("自訂時間", "請輸入遊戲時間（秒）:")
                seconds = int(value)
                if seconds <= 0:
                    raise ValueError
                set_time(seconds)
            except:
                messagebox.showerror("錯誤", "請輸入有效的正整數", parent=time_select_window)

        def move_focus(direction):
            nonlocal current_focus
            current_focus = (current_focus + direction) % len(button_list)
            button_list[current_focus].focus_set()

        def enter_selected(_=None):
            button_list[current_focus].invoke()

        time_select_window = Toplevel()
        time_select_window.title("選擇遊戲時間")
        self.center_window(time_select_window, 300, 300)
        Label(time_select_window, text="請選擇遊戲時間").pack(pady=10)

        font = ("Arial", 12)

        btn_30 = Button(time_select_window, text="30 秒", width=10, height=2, font=font, command=lambda: set_time(30))
        btn_60 = Button(time_select_window, text="1 分鐘", width=10, height=2, font=font, command=lambda: set_time(60))
        btn_custom = Button(time_select_window, text="自訂時間", width=10, height=2, font=font, command=custom_time)


        button_list = [btn_30, btn_60, btn_custom]
        current_focus = 0

        for btn in button_list:
            btn.pack(pady=5)

        button_list[current_focus].focus_set()
        time_select_window.bind("<Return>", enter_selected)
        time_select_window.bind("<Up>", lambda e: move_focus(-1))
        time_select_window.bind("<Down>", lambda e: move_focus(1))

    def countdown_start(self):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

        self.score = 0
        self.can_shoot = False
        self.game_running = False
        self.rows = [random.randint(0, 2) for _ in range(self.MAX_ROWS)]
        self.timer_label.config(text="剩餘時間: 30 秒" , fg = self.get_contrasting_color(self["bg"]) )
        self.score_label.config(text="分數: 0", fg = self.get_contrasting_color(self["bg"]) )
        self.status_label.config(text="準備中...", fg="orange")
        self.draw_rows()
        self.countdown_number(3)

    def countdown_number(self, n):
        if n > 0:
            self.status_label.config(text=f"{n}", fg="orange")
            self.after(1000, lambda: self.countdown_number(n - 1))
        else:
            self.start_game()

    def start_game(self):
        self.score = 0
        self.combo = 0 
        self.can_shoot = True
        self.time_left = self.game_time
        self.game_running = True
        self.timer_label.config(text="剩餘時間: 30")
        self.score_label.config(text="分數: 0")
        self.status_label.config(text="")
        self.countdown()
        self.draw_rows()
        self.start_button.config(text="重新開始")

    def countdown(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"剩餘時間: {self.time_left} 秒")
            self.after_id = self.after(1000, self.countdown)
        else:
            self.game_running = False
            self.can_shoot = False
            self.status_label.config(text=f"⏰ 時間到！", fg="blue")
            self.prompt_save_score(self.score, self.game_time)

    def draw_rows(self, error_row=-1):
        for r in range(self.MAX_ROWS):
            for c in range(self.LANE_COUNT):
                if self.rows[r] == c:
                    if error_row != r and self.current_zombie_images[r][c] is None:
                        self.current_zombie_images[r][c] = random.choice(self.zombie_imgs)
                    zombie_img = self.current_zombie_images[r][c]
                    self.labels[r][c].config(
                        image=zombie_img,
                        bg="red" if r == error_row else self["bg"]
                    )
                else:
                    self.labels[r][c].config(image=self.blank_img, bg=self["bg"])
                    self.current_zombie_images[r][c] = None

    def shoot(self, column):
        if not self.can_shoot or not self.game_running:
            return

        target = self.rows[-1]
        if column == target:
            self.combo += 1  # Combo +1
            points = int(1.1 ** self.combo)  # 指數加分!!!!!!!!!!!!!!!!
            self.score += points

            self.status_label.config(
                text=f"Combo x {self.combo}", fg="green"
            )

            self.rows.pop()
            self.rows.insert(0, random.randint(0, 2))
            self.score_label.config(text=f"分數: {self.score}")
            self.draw_rows()

        else:
            self.combo = 0  # Combo 歸零
            self.status_label.config(text="MISS! 懲罰 1 秒", fg="red")
            self.can_shoot = False
            self.draw_rows(error_row=self.MAX_ROWS - 1)
            self.after(1000, self.reset_penalty)


    def reset_penalty(self):
        self.can_shoot = True
        self.status_label.config(text="")
        self.draw_rows()

    def key_handler(self, event):
        key_map = {'Left': 0, 'Down': 1, 'Right': 2}
        if event.keysym in key_map:
            self.shoot(key_map[event.keysym])

    def prompt_save_score(self, score, time_mode):
        if time_mode not in [30, 60]:
            return

        def custom_name_dialog():
            dialog = Toplevel(self)
            dialog.title("遊戲結束!!! 是否要新增紀錄")
            self.center_window(dialog, 300, 200)

            Label(dialog, text="遊戲結束!!!", font=("Arial", 12)).pack(pady=(10, 0))
            Label(dialog, text=f"你獲得了 {score} 分", font=("Arial", 12), fg="blue").pack(pady=0)
            Label(dialog, text="請輸入你的名字：", font=("Arial", 12)).pack(pady=(0, 10))            
            entry = Entry(dialog, font=("Arial", 12))
            entry.pack(pady=5)
            entry.focus_set()

            result = {"name": None}
            def on_ok():
                entered = entry.get().strip()
                if not entered:
                    messagebox.showerror("錯誤", "名字不能為空！", parent=dialog)
                    return
                result["name"] = entered
                dialog.destroy()

            def on_cancel():
                dialog.destroy()

            btn_frame = Frame(dialog)
            btn_frame.pack(pady=10)
            Button(btn_frame, text="OK", width=8, command=on_ok).pack(side=LEFT, padx=10)
            Button(btn_frame, text="Cancel", width=8, command=on_cancel).pack(side=LEFT, padx=10)

            dialog.transient(self)
            dialog.grab_set()
            self.wait_window(dialog)

            return result["name"]

        name = custom_name_dialog()
        if name and name.strip():
            msg, max_msg = self.save_score_to_db(name, score, time_mode)
            if msg:
                messagebox.showinfo("紀錄結果", msg)
            if max_msg:
                messagebox.showinfo("最高紀錄", max_msg)

    def save_score_to_db(self, name, score, play_time):
        if play_time not in [30, 60]:
            return None, None

        db_path = os.path.join(os.path.dirname(__file__), "zombie_rand.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT score FROM scores WHERE name = ? AND time = ?", (name, play_time))
        result = cursor.fetchone()

        if result:
            old_score = result[0]
            if score > old_score:
                cursor.execute("UPDATE scores SET score = ? WHERE name = ? AND time = ?", (score, name, play_time))
                msg = f"🎉 {name} 破了自己在 {play_time} 秒局的紀錄！（{old_score} → {score}）"
            else:
                msg = f"😅 {name} 的分數比之前低，未更新紀錄（{score} ≦ {old_score}）"
        else:
            cursor.execute("INSERT INTO scores (name, time, score) VALUES (?, ?, ?)", (name, play_time, score))
            msg = f"✅ {name} 的新紀錄已加入 {play_time} 秒局：{score} 分"

        cursor.execute("SELECT MAX(score) FROM scores WHERE time = ?", (play_time,))
        max_score = cursor.fetchone()[0]
        max_msg = ""
        if score >= max_score:
            max_msg = f"🏆 {name} 是 {play_time} 秒局的最高分紀錄保持者！"

        conn.commit()
        conn.close()
        return msg, max_msg
    

# main
if __name__ == "__main__":
    def center_root(win, w=700, h=800):
        win.update_idletasks()
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

    root = Tk()
    root.title("ShotZombie - 終極鍵盤版")
    root.configure(bg="white")
    center_root(root) 
    app = Zombie(root)
    app.pack(fill="both", expand=True)
    root.mainloop()