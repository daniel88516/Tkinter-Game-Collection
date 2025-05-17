from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Notebook
from PIL import Image, ImageTk
import os, random
from functools import wraps
from MineSweeper_Difficulty import DifficultyConfig, Difficulty
from MineSweeper_GameBoard import GameBoard
from MineSweeper_Timer import HighPrecisionCountUpTimer
from MineSweeper_RankingPage import RankingPage
from MineSweeper_Database import Database

def operation_check(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if getattr(self, "is_game_over", True):
            return
        return method(self, *args, **kwargs)
    return wrapper
class MineSweeper(Frame):
    """初始化"""
    def __init__(self, parent:Tk, difficulty: Difficulty=Difficulty.NORMAL):
        super().__init__(parent)
        # 根據難度初始化遊戲場地
        self.gameBoard:GameBoard = GameBoard(DifficultyConfig(difficulty))
        self.buttons: list[list[Button]] = []
                    
        self.window:Tk = parent
        
        self.create_variable()
        self.load_images()
        self.create_gameboard()
        self.center_window()
        self.new_game()
    
    def start(self):
        """用 start 封裝 mainloop, 問就是這樣比較直觀"""
        self.window.mainloop()
        
    def load_images(self):
        """把圖片加載進來, 之後可透過環境變數簡化"""
        base_path = os.path.join(os.path.dirname(__file__), f"Images/UI/32x32")
        self.tile_images = {}
        for i in range(1, 9):
            self.tile_images[f"Tile{i}"] = PhotoImage(file=os.path.join(base_path, f"Tile{i}.png"))
        self.tile_images["TileEmpty"]    = PhotoImage(file=os.path.join(base_path, "TileEmpty.png"))
        self.tile_images["TileExploded"] = PhotoImage(file=os.path.join(base_path, "TileExploded.png"))
        self.tile_images["TileFlag"]     = PhotoImage(file=os.path.join(base_path, "TileFlag.png"))
        self.tile_images["TileUnknown"]  = PhotoImage(file=os.path.join(base_path, "TileUnknown.png"))
        self.tile_images["TileMine"]     = PhotoImage(file=os.path.join(base_path, "TileMine.png"))
        self.tile_images["LightOn"]      = PhotoImage(file=os.path.join(base_path, "LightOn.png"))
        self.tile_images["LightOff"]     = PhotoImage(file=os.path.join(base_path, "LightOff.png"))
        
    def create_variable(self):
        """會用到的一些遊戲變數"""
        self.flagged_count:IntVar = IntVar(value=0)
        self.is_game_over:bool = False
        self.first_click:bool = True
        self.chord_holding:bool = False
        self.debug_mode:bool = False
        self.safe_reveal_var:bool = True
        
        self.final_message: list[str] = [
            "你試圖在地雷中優雅地跳芭蕾", 
            "你被逐出了人界",
            "你想證明地雷很安全，失敗得很徹底",
            "你被地雷排除了",
            "你被炸得血肉模糊",
            "你忘了金屬探測器怎麼用", 
            "你被絆倒了",
            "你發出了一聲巨響，隨後消散在天地間",
            "你的四肢在空中飛舞，劃出一道優美的血線",
            "轟!"
        ]
                
    def create_gameboard(self):
        """創建遊戲版相關的所有元件"""
        self.frame = Frame(self)
        self.frame.pack(padx=20, pady=20)
        
        self.info_frame = Frame(self.frame)
        self.info_frame.pack(pady=5, fill=X)
        
        self.countup_timer = HighPrecisionCountUpTimer(self.frame)
        self.timer_label = Label(self.info_frame, textvariable=self.countup_timer.countdown_var, font=("Arial", 12))
        self.timer_label.pack(side=LEFT, anchor=W)
        
        self.safe_reveal_var = True
        self.safe_reveal_btn = Button(self.info_frame,
                                      image = self.tile_images["LightOn"],
                                      relief=FLAT,
                                      command=self.on_toggle_safe_reveal_var)
        self.safe_reveal_btn.pack(side=RIGHT, anchor=E)
        
        self.board_frame = Frame(self.frame)
        self.board_frame.pack()
        for r in range(self.gameBoard.height):
            row_buttons = []
            for c in range(self.gameBoard.width):
                btn = Button(
                    self.board_frame,
                    image=self.tile_images["TileUnknown"],
                    relief="flat",
                    borderwidth=0,
                    highlightthickness=0,
                    command=lambda r=r, c=c: self.on_left_click(r, c)  # 左鍵點擊
                )
                btn.bind("<Button-3>", lambda event, r=r, c=c: self.on_right_click(r, c))  # 右鍵點擊
                btn.bind("<Button-1>", lambda event, r=r, c=c: self.on_chord_press(r, c)) # 左鍵點擊
                btn.bind("<ButtonRelease-1>", lambda event, r=r, c=c: self.on_chord_release(r, c)) # 左鍵放開
                btn.grid(row=r, column=c, padx=0, pady=0)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)
        # 控制面板
        self.create_control_panel()
   
    def create_control_panel(self):
        """建立控制面板"""
        control_frame = Frame(self.frame)
        control_frame.pack(pady=5)
        
        # 難度按鈕
        difficulty_frame = Frame(control_frame)
        difficulty_frame.pack(side=TOP, pady=5)
        
        for diff in Difficulty: 
            Button(
                difficulty_frame,
                text=DifficultyConfig.CONFIGS[diff]["name"],
                command=lambda d=diff: self.change_difficulty(d)
            ).pack(side=LEFT, padx=5)
        
        # 按下 r, reset 
        self.window.bind("<space>", lambda event: self.new_game())
        self.window.bind("<Return>", lambda event:  self.new_game())
        self.reset_button = Button(control_frame, text="重置遊戲", command=self.new_game)
        self.reset_button.pack()
        
        # self.debug_button = Button(control_frame, text="Debug 模式：關閉", command=self.toggle_debug_mode)
        # self.debug_button.pack(side=LEFT, padx=5)

    def center_window(self):
        """讓視窗自適應大小, 然後置中"""
        # self.window.update_idletasks()

        # 每個方塊的大小是 32 
        # width = self.gameBoard.width * 32 + 40  # 左右各加 20 像素邊距
        # height = self.gameBoard.height * 32 + 120  # 加入控制面板高度
        
        # screen_width = self.window.winfo_screenwidth()
        # screen_height = self.window.winfo_screenheight()
        # x = (screen_width - width) // 2
        # y = (screen_height - height) // 2
        # self.window.geometry(f"{width}x{height}+{x}+{y}")
        
    def toggle_debug_mode(self):
        """作弊是一定要有的, 開發者很累的"""
        self.debug_mode = not self.debug_mode
        self.debug_button.config(text=f"Debug 模式：{'開啟' if self.debug_mode else '關閉'}")
        self.update_board()
        
    """計時器相關函數"""
    def start_timer(self):
        self.countup_timer.reset()
        self.countup_timer.start_countup()

    def stop_timer(self):
        self.countup_timer.stop_countup()

    def get_timer_value(self) -> str:
        return self.countup_timer.countdown_var.get()
    
    """遊戲邏輯"""
    def flood_fill(self, r, c):
        if not self.gameBoard.is_valid_position(r, c):
            return 
        cell = self.gameBoard.get_cell(r, c)
        if cell.revealed or cell.flagged:
            return
        cell.revealed = True
        if cell.is_empty():
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr = r + dr
                    nc = c + dc
                    if self.gameBoard.is_valid_position(nr, nc):
                        neighbor = self.gameBoard.get_cell(nr, nc)
                        if not neighbor.revealed and not neighbor.is_mine():
                            self.flood_fill(nr, nc)

    """遊戲狀態相關"""
    def new_game(self):
        """開始一場新遊戲"""
        self.is_game_over = False
        self.first_click = True
        self.countup_timer.reset()
        self.safe_reveal_btn.config(state=DISABLED)
        self.safe_reveal_var = True
        self.gameBoard.reset()
        self.update_board()
        
    def game_over(self):
        """你爆炸了"""
        self.reveal_all_mines()
        self.is_game_over = True
        self.stop_timer()
        messagebox.showerror("遊戲結束", f"{self.get_random_final_message()}, 成功在{self.get_timer_value()}內失敗了!")
        
    def check_win_condition(self):
        """勝利唾手可得"""
        for r in range(self.gameBoard.height):
            for c in range(self.gameBoard.width):
                cell = self.gameBoard.get_cell(r, c)
                if not cell.is_mine() and not cell.revealed:
                    return
        self.is_game_over = True
        self.stop_timer()
        self.show_victory_popup()
        # messagebox.showinfo("恭喜", f"你在{self.get_timer_value()}內贏得了遊戲！")
        
    """滑鼠事件處理"""
    @operation_check
    def on_left_click(self, r, c):
        """你按下了左鍵"""
        # 第一次按下的時候, 才擺放地雷
        if self.first_click:
            self.safe_reveal_btn.config(state=ACTIVE)
            self.gameBoard.place_mines(r, c, int.from_bytes(os.urandom(4), byteorder='big'))
            self.gameBoard.calculate_numbers()
            self.start_timer()
            self.first_click = False

        # 旗標不會被展開
        cell = self.gameBoard.get_cell(r, c)
        if cell.revealed or cell.flagged:
            return

        # 每次按下, 判斷是否為地雷
        if cell.is_mine():
            if self.safe_reveal_var == True:
                cell.flagged = True
                cell.revealed = True  
                self.safe_reveal_var = False               
                self.safe_reveal_btn.config(image=self.tile_images["LightOff"], state=DISABLED)
            else: 
                cell.exploded = True
                cell.revealed = True
                self.is_game_over = True
                self.game_over()
        elif cell.is_number():
            cell.revealed = True
        elif cell.is_empty():
            self.flood_fill(r, c)
        self.update_board()
        self.check_win_condition()

    @operation_check
    def on_right_click(self, r, c):
        """你按下了右鍵插旗子"""
        # 你不能將旗子插在奇怪的位置
        cell = self.gameBoard.get_cell(r, c)
        if cell.revealed:
            return
        
        # 你插太多旗子了
        if self.flagged_count.get() >= self.gameBoard.mine_count: 
            return
        
        cell.flagged = not cell.flagged
        self.update_board()

    @operation_check
    def on_chord_click(self, r, c):
        """你想要抄近路，玩的快一些"""        
        # 只能在 revealed, 且為數字的時候觸發
        cell = self.gameBoard.get_cell(r, c)
        if not cell.revealed or not cell.is_number():
            return
        
        flag_count = self.gameBoard.count_flags_around(r, c)
        if flag_count != cell.number:
            return
        
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr = r + dr
                nc = c + dc
                if self.gameBoard.is_valid_position(nr, nc):
                    self.on_left_click(nr, nc)
    
    @operation_check
    def on_chord_press(self, r, c):
        """想要展開時的「預視」效果"""
        
        cell = self.gameBoard.get_cell(r, c)
        if not cell.revealed or not cell.is_number():
            return
            
        flag_count = self.gameBoard.count_flags_around(r, c)
        if flag_count != cell.number:
            return
            
        self.chord_holding = True
        # 臨時顯示周圍未標記格子的內容
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr = r + dr
                nc = c + dc
                if self.gameBoard.is_valid_position(nr, nc):
                    neighbor = self.gameBoard.get_cell(nr, nc)
                    if not neighbor.flagged and not neighbor.revealed:
                        btn = self.buttons[nr][nc]
                        btn.config(image=self.tile_images["TileEmpty"])

    def on_chord_release(self, r, c):
        """放開按鍵, 觸發 chord_click 的效果"""
        if not self.chord_holding:
            return
        self.chord_holding = False
        self.update_board()
        self.on_chord_click(r, c)
    
    def on_toggle_safe_reveal_var(self):
        self.safe_reveal_var = not self.safe_reveal_var
        self.safe_reveal_btn.config(image=self.tile_images["LightOn"] if self.safe_reveal_var == True else self.tile_images["LightOff"])
    
    """輔助方法"""
    def reveal_all_mines(self):
        for r in range(self.gameBoard.height):
            for c in range(self.gameBoard.width):
                cell = self.gameBoard.get_cell(r, c)
                if cell.is_mine():
                    cell.revealed = True
        self.update_board()

    def update_board(self):
        for r in range(self.gameBoard.height):
            for c in range(self.gameBoard.width):
                cell = self.gameBoard.get_cell(r, c)
                btn = self.buttons[r][c]
                
                if self.debug_mode and cell.is_mine() and not cell.revealed:
                    img = self.tile_images["TileMine"]
                elif cell.revealed:
                    if cell.is_mine():
                        if cell.exploded:
                            img = self.tile_images["TileExploded"]
                        else:
                            img = self.tile_images["TileMine"]
                    elif cell.is_number():
                        key = "Tile" + str(cell.number)
                        img = self.tile_images.get(key, self.tile_images["TileEmpty"])
                    else:
                        img = self.tile_images["TileEmpty"]
                else:
                    if cell.flagged:
                        img = self.tile_images["TileFlag"]
                    else:
                        img = self.tile_images["TileUnknown"]
                btn.config(image=img)

    def change_difficulty(self, difficulty: Difficulty):
        """切換難度"""
        self.gameBoard = GameBoard(DifficultyConfig(difficulty))
        self.buttons:list[list[Button]] = []
        self.frame.destroy()
        self.create_gameboard()
        self.center_window()
        self.new_game()
    
    def get_random_final_message(self) -> str:
        """隨機選擇一個訊息"""
        return random.choice(self.final_message)
       
    def show_victory_popup(self):
        config = self.gameBoard.config
        
        messagebox.showinfo("恭喜", f"你在 {self.get_timer_value()} 內贏得了遊戲！")
        # 建立輸入名字的 Toplevel 視窗
        name_popup = Toplevel()
        name_popup.title("輸入名字")
        name_popup.geometry("300x150")
        name_popup.resizable(False, False)
        name_popup.grab_set()

        Label(name_popup, text="請輸入你的名字：", font=("微軟正黑體", 14)).pack(pady=10)

        entry = Entry(name_popup, font=("微軟正黑體", 14))
        entry.pack(pady=5)
        entry.focus()

        def on_confirm():
            name = entry.get().strip()
            if not name: 
                messagebox.showerror("錯誤", "名字不能為空！")
                return
            minutes, seconds, millis = map(int, self.get_timer_value().replace(":", " ").replace(".", " ").split())
            db = Database()
            success = db.insert_score(name, minutes, seconds, millis, config)
            
            if success:
                messagebox.showinfo("紀錄結果", f"🎉 {name} 的新紀錄已成功加入排行榜！")
            else:
                messagebox.showinfo("紀錄結果", f"😅 {name} 的成績未超過舊有紀錄，未更新。")
            
            db.close()
            name_popup.destroy()
            
        button_frame = Frame(name_popup)
        button_frame.pack(pady=5)
        confirm_btn = Button(button_frame, text="確定", font=("微軟正黑體", 12), command=on_confirm)
        confirm_btn.pack(side=LEFT)
        
        cancel_btn = Button(button_frame, text="取消", font=("微軟正黑體", 12), command=name_popup.destroy)
        cancel_btn.pack(padx=10, side=RIGHT)

        # 綁定 Enter 鍵
        name_popup.bind("<Return>", lambda event: on_confirm())

if __name__ == "__main__":
    def on_tab_change(event):
        """處理 Notebook 分頁切換事件"""
        selected_tab = event.widget.select()
        selected_tab_text = event.widget.tab(selected_tab, "text")
        if selected_tab_text == "排行榜":
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            w, h = 1920, 1080
            x = (screen_width - w) // 2
            y = (screen_height - h) // 2
            window.geometry(f"{w}x{h}+{x}+{y}")
        else:
            window.geometry('')
            pass
        
    window = Tk()
    window.title("踩地雷")

    notebook = Notebook(window)
    notebook.pack(expand=True, fill=BOTH)

    minesweeper_game = MineSweeper(window)
    window.wm_iconphoto(False, minesweeper_game.tile_images["TileMine"])
    notebook.add(minesweeper_game, text="遊戲頁面")

    rank_page = RankingPage(window)
    notebook.add(rank_page, text="排行榜")

    # 綁定分頁切換事件
    notebook.bind("<<NotebookTabChanged>>", on_tab_change)

    minesweeper_game.start()