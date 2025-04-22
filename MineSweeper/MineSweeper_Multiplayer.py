from tkinter import *
from tkinter import messagebox
import os
from MineSweeper_Difficulty import DifficultyConfig, Difficulty
from MineSweeper_GameBoard import GameBoard

class BoardManager:
    """管理一個遊戲版塊, 初始化會用到的一些變數"""
    def __init__(self, parent_frame, tile_images, name, width, height, mine_count, debug_mode_var, on_win_callback):
        self.parent_frame = parent_frame
        self.tile_images = tile_images
        self.name = name
        self.gameBoard = GameBoard(width, height, mine_count, name)
        self.buttons = []
        
        self.flagged_count = IntVar(value=0)
        self.is_game_over = False
        self.first_click = True
        self.chord_holding = False
        
        self.debug_mode_var = debug_mode_var  # 這是共有的 debug 變數
        self.on_win_callback = on_win_callback  # 勝利時的回調函數
        
        self.create_ui()
        
    def create_ui(self):
        """創建 UI"""
        self.board_frame = Frame(self.parent_frame)
        self.board_frame.pack(side=LEFT, padx=10)
        
        # 遊戲版名字
        Label(self.board_frame, text=self.name, font=("Arial", 12, "bold")).pack(pady=5)
        
        # 遊戲板按鈕
        self.buttons_frame = Frame(self.board_frame)
        self.buttons_frame.pack()
        
        for r in range(self.gameBoard.height):
            row_buttons = []
            for c in range(self.gameBoard.width):
                btn = Button(
                    self.buttons_frame,
                    image=self.tile_images["TileUnknown"],
                    relief="flat",
                    borderwidth=0,
                    highlightthickness=0,
                    command=lambda r=r, c=c: self.on_left_click(r, c)
                )
                btn.bind("<Button-3>", lambda event, r=r, c=c: self.on_right_click(r, c))
                btn.bind("<Button-1>", lambda event, r=r, c=c: self.on_chord_press(r, c))
                btn.bind("<ButtonRelease-1>", lambda event, r=r, c=c: self.on_chord_release(r, c))
                btn.grid(row=r, column=c, padx=0, pady=0)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)
    
    def reset(self):
        """重置遊戲板"""
        self.is_game_over = False
        self.first_click = True
        self.gameBoard.reset()
        self.update_board()
    
    def flood_fill(self, r, c):
        """塌陷"""
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
    
    def on_left_click(self, r, c):
        """你按下了左鍵"""
        if self.is_game_over:
            return
        
        # 第一次按下的時候, 才擺放地雷
        if self.first_click:
            self.first_click = False
            self.gameBoard.place_mines(r, c)
            self.gameBoard.calculate_numbers()

        # 旗標不會被展開
        cell = self.gameBoard.get_cell(r, c)
        if not cell.revealed and cell.flagged:
            return

        # 每次按下, 判斷是否為地雷
        if cell.is_mine():
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
    
    def on_right_click(self, r, c):
        """你按下了右鍵插旗子"""
        if self.is_game_over:
            return
        
        cell = self.gameBoard.get_cell(r, c)
        if cell.revealed:
            return
        
        if self.flagged_count.get() >= self.gameBoard.mine_count: 
            return
        
        cell.flagged = not cell.flagged
        self.update_board()
    
    def on_chord_click(self, r, c):
        """你想要抄近路，玩的快一些"""
        if self.is_game_over:
            return
        
        cell = self.gameBoard.get_cell(r, c)
        if not cell.revealed or not cell.is_number():
            return
        
        flag_count = self.gameBoard.count_flags_around(r, c)
        if flag_count != cell.number:
            return
        
        exploded = False
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr = r + dr
                nc = c + dc
                if self.gameBoard.is_valid_position(nr, nc):
                    neighbor = self.gameBoard.get_cell(nr, nc)
                    if not neighbor.flagged and not neighbor.revealed:
                        if neighbor.is_mine():
                            neighbor.exploded = True
                            neighbor.revealed = True
                            exploded = True
                        elif neighbor.is_number():
                            neighbor.revealed = True
                        else: # empty
                            self.flood_fill(nr, nc)
        if exploded:
            self.is_game_over = True
            self.game_over()
            
        self.update_board()
        self.check_win_condition()
    
    def on_chord_press(self, r, c):
        """想要展開時的「預視」效果"""
        if self.is_game_over:
            return
        
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
    
    def game_over(self):
        """你爆炸了"""
        self.reveal_all_mines()
        messagebox.showinfo("遊戲結束", f"{self.name} 踩到地雷了！")
    
    def check_win_condition(self):
        """勝利唾手可得"""
        for r in range(self.gameBoard.height):
            for c in range(self.gameBoard.width):
                cell = self.gameBoard.get_cell(r, c)
                if not cell.is_mine() and not cell.revealed:
                    return
                    
        self.is_game_over = True
        messagebox.showinfo("恭喜", f"{self.name} 贏了！")
        # 通知主遊戲有板子贏了
        if self.on_win_callback:
            self.on_win_callback(self)
    
    def reveal_all_mines(self):
        """顯示所有地雷"""
        for r in range(self.gameBoard.height):
            for c in range(self.gameBoard.width):
                cell = self.gameBoard.get_cell(r, c)
                if cell.is_mine():
                    cell.revealed = True
        self.update_board()
    
    def update_board(self):
        """更新遊戲板顯示"""
        for r in range(self.gameBoard.height):
            for c in range(self.gameBoard.width):
                cell = self.gameBoard.get_cell(r, c)
                btn = self.buttons[r][c]
                
                if self.debug_mode_var.get() and cell.is_mine() and not cell.revealed:
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
    
    def change_difficulty(self, width, height, mine_count):
        """更改難度"""
        self.gameBoard = GameBoard(width, height, mine_count, self.name)
        self.buttons = []
        self.buttons_frame.destroy()
        self.buttons_frame = Frame(self.board_frame)
        self.buttons_frame.pack()
        
        for r in range(self.gameBoard.height):
            row_buttons = []
            for c in range(self.gameBoard.width):
                btn = Button(
                    self.buttons_frame,
                    image=self.tile_images["TileUnknown"],
                    relief="flat",
                    borderwidth=0,
                    highlightthickness=0,
                    command=lambda r=r, c=c: self.on_left_click(r, c)
                )
                btn.bind("<Button-3>", lambda event, r=r, c=c: self.on_right_click(r, c))
                btn.bind("<Button-1>", lambda event, r=r, c=c: self.on_chord_press(r, c))
                btn.bind("<ButtonRelease-1>", lambda event, r=r, c=c: self.on_chord_release(r, c))
                btn.grid(row=r, column=c, padx=0, pady=0)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)
        
        self.reset()

class MineSweeper:
    """主遊戲類"""
    def __init__(self, window:Tk, difficulty: Difficulty=Difficulty.NORMAL, board_count=2):
        self.window = window
        self.config = DifficultyConfig(difficulty)
        self.debug_mode = BooleanVar(value=False)
        self.board_managers = []
        
        self.load_images()
        self.create_widget(board_count)
        self.center_window()
        self.new_game()
    
    def start(self):
        """啟動遊戲"""
        self.window.mainloop()
        
    def load_images(self):
        """加載圖片"""
        base_path = os.path.join(os.path.dirname(__file__), f"Images")
        self.tile_images = {}
        for i in range(1, 9):
            self.tile_images[f"Tile{i}"] = PhotoImage(file=os.path.join(base_path, f"Tile{i}.png"))
        self.tile_images["TileEmpty"]    = PhotoImage(file=os.path.join(base_path, "TileEmpty.png"))
        self.tile_images["TileExploded"] = PhotoImage(file=os.path.join(base_path, "TileExploded.png"))
        self.tile_images["TileFlag"]     = PhotoImage(file=os.path.join(base_path, "TileFlag.png"))
        self.tile_images["TileUnknown"]  = PhotoImage(file=os.path.join(base_path, "TileUnknown.png"))
        self.tile_images["TileMine"]     = PhotoImage(file=os.path.join(base_path, "TileMine.png"))
        
    def create_widget(self, board_count):
        """創建UI元素"""
        self.frame = Frame(self.window)
        self.frame.pack(padx=20, pady=20)
        
        # 創建遊戲板容器
        self.boards_container = Frame(self.frame)
        self.boards_container.pack()
        
        # 創建多個遊戲板
        for i in range(board_count):
            board_manager = BoardManager(
                self.boards_container,
                self.tile_images,
                f"遊戲板 {i+1}",
                self.config.board_width,
                self.config.board_height,
                self.config.mine_count,
                self.debug_mode,
                self.on_board_win
            )
            self.board_managers.append(board_manager)
            
        # 控制面板
        self.create_control_panel()
   
    def create_control_panel(self):
        """創建控制面板"""
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
        
        self.reset_button = Button(control_frame, text="重置遊戲", command=self.new_game)
        self.reset_button.pack(side=LEFT, padx=5)
        
        self.debug_button = Button(control_frame, text="Debug 模式：關閉", command=self.toggle_debug_mode)
        self.debug_button.pack(side=LEFT, padx=5)

    def center_window(self):
        """調整視窗大小和位置"""
        self.window.update_idletasks()

        # 計算視窗大小
        board_width = self.config.board_width * 32
        total_width = board_width * len(self.board_managers) + 80 + (20 * (len(self.board_managers) - 1))
        height = self.config.board_height * 32 + 150
        
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - total_width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{total_width}x{height}+{x}+{y}")
        
    def toggle_debug_mode(self):
        """切換Debug模式"""
        self.debug_mode.set(not self.debug_mode.get())
        self.debug_button.config(text=f"Debug 模式：{'開啟' if self.debug_mode.get() else '關閉'}")
        self.update_all_boards()
    
    def update_all_boards(self):
        """更新所有遊戲板"""
        for board_manager in self.board_managers:
            board_manager.update_board()
    
    def new_game(self):
        """開始新遊戲"""
        for board_manager in self.board_managers:
            board_manager.reset()
    
    def on_board_win(self, board_manager):
        """處理遊戲板勝利事件"""
        # 檢查是否所有遊戲板都贏了
        all_won = all(bm.is_game_over for bm in self.board_managers)
        if all_won:
            messagebox.showinfo("恭喜", "你完成了所有遊戲板！")
    
    def change_difficulty(self, difficulty):
        """更改難度"""
        self.config = DifficultyConfig(difficulty)
        for board_manager in self.board_managers:
            board_manager.change_difficulty(
                self.config.board_width,
                self.config.board_height,
                self.config.mine_count
            )
        self.center_window()
        
# main
if __name__ == "__main__":
    window = Tk()
    window.title("多人踩地雷")
    game = MineSweeper(window, Difficulty.EASY, 5)  # 預設創建2個遊戲板
    game.start()
