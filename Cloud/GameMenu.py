import os
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from ThreeHall import ThreeHall
from TicTacToe import TicTacToe
from MineSweeper import MineSweeper
from MineSweeper_SinglePlayer import MineSweeper as SingleMine
from Z_main import ZMain
import importlib
from MineSweeper_RankingPage import RankingPage 

class GameMenu:
    def __init__(self):
        
        # 建立主視窗
        self.window = Tk()
        self.window.title("Game Menu")
        self.window.configure(bg="black")
        self.window.resizable(True, True)

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        w, h = 1080, 800
        x, y = (screen_width - w) // 2, (screen_height - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")

        # 載入圖片當標題
        base_path = os.path.dirname(__file__)
        img_path = os.path.join(base_path, "GameMenu圖片", "GTA6.webp")
        original_img = Image.open(img_path).resize((600, 345))
        self.banner_img = ImageTk.PhotoImage(original_img)
        banner_label = Label(self.window, image=self.banner_img, bg="black")
        banner_label.pack(pady=10)

        # 中央內容容器（限制 TreeView 尺寸）
        content_frame = Frame(self.window, bg="black", width=700, height=300)
        content_frame.pack(pady=20)
        content_frame.pack_propagate(False)  # 禁止根據內容自動壓縮尺寸

        # 控制 Treeview 的最大寬度
        max_width = 800  
        content_frame.configure(width=max_width)
        content_frame.pack_propagate(False)

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
        self.tree = ttk.Treeview(content_frame, show="headings", columns=("game",), height=10)
        self.tree.heading("game", text="遊戲清單")
        self.tree.column("game", anchor="center")
        self.tree.pack(fill="both", expand=False, padx=40, pady=20)
        self.tree.tag_configure('hover', background="#555555")  

        # 遊戲清單
        self.games = {
            "🧟 殭屍射擊": ("Z_main", "ZMain"),
            "💣 踩地雷（雙人）": ("MineSweeper", "MineSweeper"),
            "💣 踩地雷（單人）": ("MineSweeper_SinglePlayer", "MineSweeper"),
        }

        # TreeView條紋列
        self.tree.tag_configure('evenrow', background="#2a2a2a")  # 偶數行
        self.tree.tag_configure('oddrow', background="#1a1a1a")   # 奇數行

        self.row_tags = {}
        for idx, name in enumerate(self.games):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            item_id = self.tree.insert("", "end", values=(name,), tags=(tag,))
            self.row_tags[item_id] = tag  # <== 記錄每一行原本的 tag

        # 右鍵選單
        self.menu = Menu(self.window, tearoff=0)
        self.menu.add_command(label="🚀     執行", command=self.run_selected_game)
        self.menu.add_command(label="🛡️以系統管理員執行", command=self.run_selected_game)
        self.menu.add_command(label="📘    遊戲教學", command=self.show_game_tutorial)

        #事件
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", lambda e: self.run_selected_game())
        self.tree.bind("<Return>", lambda e: self.run_selected_game())
        self.tree.bind("<Motion>", self.on_mouse_move)

        # 退出按鈕
        exit_btn = Button(self.window, text="退出", font=("微軟正黑體", 14, "bold"),
                        bg="red", fg="white", activebackground="darkred", command=self.window.quit)
        exit_btn.pack(pady=10)

        #紀錄正再跑的程式
        self.running_processes = {} 

        self.window.mainloop()
    def run_selected_game(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        game_name = self.tree.item(selected_item[0])["values"][0]
        module_name, class_name = self.games.get(game_name)

        if game_name == "💣 踩地雷（單人）":
            self.create_minesweeper_with_ranking()
            return

        module = importlib.import_module(module_name)
        game_class = getattr(module, class_name)

        top = Toplevel(self.window)
        game_instance = game_class(top)

        if isinstance(game_instance, Frame):
            game_instance.pack(fill="both", expand=True)
        if hasattr(game_instance, "start"):
            game_instance.start()

    def create_minesweeper_with_ranking(self):
        from MineSweeper_RankingPage import RankingPage
        from MineSweeper_SinglePlayer import MineSweeper as SingleMine
        from tkinter.ttk import Notebook

        def on_tab_change(event):
            selected_tab = event.widget.select()
            selected_tab_text = event.widget.tab(selected_tab, "text")
            if selected_tab_text == "排行榜":
                screen_width = minesweeper_window.winfo_screenwidth()
                screen_height = minesweeper_window.winfo_screenheight()
                w, h = 1920, 1080
                x = (screen_width - w) // 2
                y = (screen_height - h) // 2
                minesweeper_window.geometry(f"{w}x{h}+{x}+{y}")
                minesweeper_window.state('zoomed')
            else:
                minesweeper_window.geometry('')
                minesweeper_window.state('normal')

        minesweeper_window = Toplevel(self.window)
        minesweeper_window.title("踩地雷")

        notebook = Notebook(minesweeper_window)
        notebook.pack(expand=True, fill=BOTH)

        style = ttk.Style()
        style.configure("TNotebook.Tab", focuscolor="none")

        minesweeper_game = SingleMine(minesweeper_window)
        minesweeper_window.wm_iconphoto(False, minesweeper_game.tile_images["TileMine"])
        notebook.add(minesweeper_game, text="遊戲頁面")

        rank_page = RankingPage(minesweeper_window)
        notebook.add(rank_page, text="排行榜")

        notebook.bind("<<NotebookTabChanged>>", on_tab_change)
    def show_game_tutorial(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        game_name = self.tree.item(selected_item[0])["values"][0]
        base_path = os.path.dirname(__file__)
        img_dir = os.path.join(base_path, "GameMenu圖片")

        extensions = [".png", ".jpg", ".webp"]
        img_path = None

        for ext in extensions:
            candidate = os.path.join(img_dir, f"{game_name}教學{ext}")
            if os.path.exists(candidate):
                img_path = candidate
                break

        if img_path:
            tutorial_window = Toplevel(self.window)
            tutorial_window.title(f"{game_name} 教學")
            tutorial_window.configure(bg="black")

            w, h = 640, 640
            screen_w = tutorial_window.winfo_screenwidth()
            screen_h = tutorial_window.winfo_screenheight()
            x = (screen_w - w) // 2
            y = (screen_h - h) // 2
            tutorial_window.geometry(f"{w}x{h}+{x}+{y}")

            tutorial_img = Image.open(img_path).resize((600, 600))
            photo = ImageTk.PhotoImage(tutorial_img)

            label = Label(tutorial_window, image=photo, bg="black")
            label.image = photo  # keep reference
            label.pack(padx=20, pady=20)
        else:
            messagebox.showinfo("提示", "目前沒有教學")

    def on_mouse_move(self, event):
        region = self.tree.identify('region', event.x, event.y)
        if region == 'cell':
            row_id = self.tree.identify_row(event.y)
            if hasattr(self, 'hover_row') and self.hover_row == row_id:
                return
            if hasattr(self, 'hover_row') and self.hover_row:
                self.tree.item(self.hover_row, tags=(self.row_tags[self.hover_row],))
            self.hover_row = row_id
            if row_id:
                self.tree.item(row_id, tags=('hover',))
        else:
            if hasattr(self, 'hover_row') and self.hover_row:
                self.tree.item(self.hover_row, tags=(self.row_tags[self.hover_row],))
                self.hover_row = None
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)

if __name__ == "__main__":
    GameMenu()
