import os
import subprocess
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

class GameMenu:
    def __init__(self):
        # 建立主視窗
        self.window = Tk()
        self.window.title("Game Menu")
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        w, h = 600, 800
        x, y = (screen_width - w) // 2, (screen_height - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")
        self.window.configure(bg="black")
        self.window.resizable(False, False)

        # 載入圖片當標題
        base_path = os.path.dirname(__file__)
        img_path = os.path.join(base_path, "GameMenu圖片", "GTA6.webp")
        original_img = Image.open(img_path).resize((400, 200))
        self.banner_img = ImageTk.PhotoImage(original_img)
        banner_label = Label(self.window, image=self.banner_img, bg="black")
        banner_label.pack(pady=10)

        # TreeView 樣式設定
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Treeview",
            font=("微軟正黑體", 18, "bold"),
            rowheight=50,
            background="black",
            foreground="white",
            fieldbackground="black",
            bordercolor="white",
            borderwidth=1,
            relief="solid"
        )

        style.configure("Treeview.Heading",
            font=("微軟正黑體", 20, "bold"),
            background="#00BFFF",
            foreground="white",
            padding=(5, 10)
        )

        style.map('Treeview', 
            background=[('selected', '#FF69B4'), ('active', '#404040')],
            foreground=[('selected', 'white')]
        )

        # 建立 TreeView
        self.tree = ttk.Treeview(self.window, show="headings", columns=("game",), height=6)
        self.tree.heading("game", text="遊戲清單")
        self.tree.column("game", anchor="center")
        self.tree.pack(fill="both", expand=True, padx=40, pady=20)

        # 遊戲清單
        self.games = {
            "Zombie": os.path.join(base_path, "Z_main.py"),
            "Monty Hall": os.path.join(base_path, "ThreeHall.py"),
            "井字遊戲": os.path.join(base_path, "TicTacToe.py"),
            "踩地雷(單人版)": os.path.join(base_path, "MineSweeper_SinglePlayer.py"),
            "踩地雷(多人版)": os.path.join(base_path, "MineSweeper", "MineSweeper.py")
        }

        # TreeView條紋列
        self.tree.tag_configure('evenrow', background="#2a2a2a")  # 偶數行
        self.tree.tag_configure('oddrow', background="#1a1a1a")   # 奇數行

        for idx, name in enumerate(self.games):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=(name,), tags=(tag,))

        # 右鍵選單
        self.menu = Menu(self.window, tearoff=0)
        self.menu.add_command(label="🚀     執行", command=self.run_selected_game)
        self.menu.add_command(label="🛡️以系統管理員執行", command=self.run_selected_game)
        self.menu.add_command(label="📘    遊戲教學", command=self.show_game_tutorial)

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", lambda e: self.run_selected_game())
        self.tree.bind("<Return>", lambda e: self.run_selected_game())

        # 退出按鈕
        exit_btn = Button(self.window, text="退出", font=("微軟正黑體", 14, "bold"),
                        bg="red", fg="white", activebackground="darkred", command=self.window.quit)
        exit_btn.pack(pady=10)

        self.window.mainloop()



    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)

    def run_selected_game(self):
        selected_item = self.tree.selection()
        if selected_item:
            game_name = self.tree.item(selected_item[0])["values"][0]
            py_file = self.games.get(game_name)
            if py_file:
                full_path = os.path.join(os.path.dirname(__file__), py_file)
                subprocess.Popen(["python", full_path], shell=True)
                
    def show_game_tutorial(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        game_name = self.tree.item(selected_item[0])["values"][0]
        base_path = os.path.dirname(__file__)
        img_dir = os.path.join(base_path, "GameMenu圖片")

        # 支援的圖檔副檔名
        extensions = [".png", ".jpg", ".webp"]
        img_path = None

        for ext in extensions:
            candidate = os.path.join(img_dir, f"{game_name}教學{ext}")
            if os.path.exists(candidate):
                img_path = candidate
                break

        if img_path:
            # 建立 Toplevel 視窗
            tutorial_window = Toplevel(self.window)
            tutorial_window.title(f"{game_name} 教學")
            tutorial_window.configure(bg="black")

            # 視窗大小
            w, h = 640, 640
            screen_w = tutorial_window.winfo_screenwidth()
            screen_h = tutorial_window.winfo_screenheight()
            x = (screen_w - w) // 2
            y = (screen_h - h) // 2
            tutorial_window.geometry(f"{w}x{h}+{x}+{y}")

            # 載入圖片
            tutorial_img = Image.open(img_path).resize((600, 600))
            photo = ImageTk.PhotoImage(tutorial_img)

            label = Label(tutorial_window, image=photo, bg="black")
            label.image = photo  # keep reference
            label.pack(padx=20, pady=20)
        else:
            messagebox.showinfo("提示", "目前沒有教學")


if __name__ == "__main__":
    GameMenu()
