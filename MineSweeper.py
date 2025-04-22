from tkinter import *
from tkinter import messagebox
import random
import os
from enum import auto, Enum

class Difficulty(Enum):
    EASY = auto()
    NORMAL = auto() 
    HARD = auto() 
    
class DifficultyConfig(): 
    CONFIGS = {
        Difficulty.EASY:{
            "board_width": 9,
            "board_height": 9,
            "mine_count": 10,
            "name": "簡單"
        },
        Difficulty.NORMAL:{
            "board_width": 16,
            "board_height": 16,
            "mine_count": 40,
            "name": "普通"
        },
        Difficulty.HARD:{
            "board_width": 30,
            "board_height": 16,
            "mine_count": 99,
            "name": "困難"
        }
    }
    def __init__(self, difficulty: Difficulty):
        config = self.CONFIGS[difficulty]
        self.board_width:int = config["board_width"]
        self.board_height:int = config["board_height"]
        self.mine_count:int = config["mine_count"]
        self.name:str = config["name"]
        
class CellType(Enum):
    EMPTY = auto()
    MINE = auto()
    NUMBER = auto()
    
class Cell:
    def __init__(self, row, col):
        self.row:int        = row 
        self.col:int        = col     
        self.type:CellType  = CellType.EMPTY
        self.number:int     = 0
        self.revealed:bool  = False
        self.flagged:bool   = False
        self.exploded:bool  = False
    
    def reset(self):
        self.type = CellType.EMPTY
    
    def is_mine(self):
        return self.type == CellType.MINE

    def is_number(self):
        return self.type == CellType.NUMBER
    
    def is_empty(self):
        return self.type == CellType.EMPTY
    
    def set_mine(self):
        self.type = CellType.MINE
    
    def set_number(self, number:int):
        self.type = CellType.NUMBER
        self.number = number

class MineSweeper:
    # ===初始化===
    def __init__(self, window:Tk, difficulty: Difficulty=Difficulty.NORMAL):
        self.window:Tk              = window
        self.config = DifficultyConfig(difficulty)
        self.board_width:int        = self.config.board_width
        self.board_height:int       = self.config.board_height
        self.mine_count:int         = self.config.mine_count
        self.cells:list[Cell]       = []
        self.buttons:list[Button]   = []    
            
        self.load_images()
        self.create_variable()
        self.create_widget()
        self.new_game()
    
    def start(self):
        self.window.mainloop()
        
    def load_images(self):
        base_path = os.path.join(os.path.dirname(__file__), "Images")
        self.tile_images = {}
        for i in range(1, 9):
            self.tile_images[f"Tile{i}"] = PhotoImage(file=os.path.join(base_path, f"Tile{i}.png"))
        self.tile_images["TileEmpty"]    = PhotoImage(file=os.path.join(base_path, "TileEmpty.png"))
        self.tile_images["TileExploded"] = PhotoImage(file=os.path.join(base_path, "TileExploded.png"))
        self.tile_images["TileFlag"]     = PhotoImage(file=os.path.join(base_path, "TileFlag.png"))
        self.tile_images["TileUnknown"]  = PhotoImage(file=os.path.join(base_path, "TileUnknown.png"))
        self.tile_images["TileMine"]     = PhotoImage(file=os.path.join(base_path, "TileMine.png"))

    def create_variable(self):
        self.is_game_over  = False
        self.debug_mode = False
        self.first_click = True
        
    def create_widget(self):
        self.frame = Frame(self.window)
        self.frame.pack()
        self.board = Frame(self.frame)
        self.board.pack()
        for r in range(self.board_height):
            row_buttons = []
            for c in range(self.board_width):
                btn = Button(
                    self.board,
                    image=self.tile_images["TileUnknown"],
                    relief="flat",
                    borderwidth=0,
                    highlightthickness=0,
                    command=lambda r=r, c=c: self.on_left_click(r, c)  # 左鍵點擊
                )
                btn.bind("<Button-3>", lambda event, r=r, c=c: self.on_right_click(r, c))  # 右鍵點擊
                btn.bind("<Button-2>", lambda event, r=r, c=c: self.on_chord_click(r, c)) # 中鍵點擊
                btn.grid(row=r, column=c, padx=0, pady=0)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)
        self.create_control_panel()
        self.center_window()
   
    def center_window(self):
        """讓視窗自適應大小並置中"""
        self.window.update_idletasks()
        
        # 計算所需的視窗大小
        # 假設每個格子是 32x32 像素，再加上邊距和控制面板的空間
        width = self.board_width * 32 + 40  # 左右各加 20 像素邊距
        height = self.board_height * 32 + 100  # 上下邊距加控制面板高度
        
        # 獲取螢幕尺寸
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # 計算視窗位置使其置中
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # 設定視窗大小和位置
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_control_panel(self):
        # 建立控制面板
        control_frame = Frame(self.frame)
        control_frame.pack(pady=5)
        
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

    def toggle_debug_mode(self):
        self.debug_mode = not self.debug_mode
        self.debug_button.config(text=f"Debug 模式：{'開啟' if self.debug_mode else '關閉'}")
        self.update_board()
        
    # ===遊戲邏輯===
    def place_mines(self, first_r, first_c):
        # 安全開局
        safe_cells = set()
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr = first_r + dr
                nc = first_c + dc
                if 0 <= nr < self.board_height and 0 <= nc < self.board_width:
                    safe_cells.add((nr, nc))
        count = 0
        while count < self.mine_count:
            r = random.randrange(self.board_height)
            c = random.randrange(self.board_width)
            cell = self.cells[r][c]
            if (r, c) not in safe_cells and not cell.is_mine():
                self.cells[r][c].set_mine()
                count += 1

    def calculate_numbers(self):
        for r in range(self.board_height):
            for c in range(self.board_width):
                cell = self.cells[r][c]
                if cell.is_mine():
                    continue
                mine_count = sum(1
                    for dr in [-1, 0, 1]
                    for dc in [-1, 0, 1]
                    if 0 <= r + dr < self.board_height
                    and 0 <= c + dc < self.board_width
                    and self.cells[r + dr][c + dc].is_mine()
                )
                if mine_count > 0:
                    cell.set_number(mine_count)

    def flood_fill(self, r, c):
        if not (0 <= r < self.board_height and 0 <= c < self.board_width):
            return
        cell = self.cells[r][c]
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
                    if 0 <= nr < self.board_height and 0 <= nc < self.board_width:
                        neighbor = self.cells[nr][nc]
                        if not neighbor.revealed and not neighbor.is_mine():
                            self.flood_fill(nr, nc)

    # ===遊戲狀態相關===
    def new_game(self):
        self.is_game_over = False
        self.first_click = True
        self.cells = [[Cell(r, c) for c in range(self.board_width)] for r in range(self.board_height)]
        self.update_board()

    def game_over(self):
        self.reveal_all_mines()
        messagebox.showinfo("遊戲結束", "你踩到地雷了！")
        
    def check_win_condition(self):
        for r in range(self.board_height):
            for c in range(self.board_width):
                cell = self.cells[r][c]
                if not cell.is_mine() and not cell.revealed:
                    return
        self.is_game_over = True
        messagebox.showinfo("恭喜", "你贏了！")
    
    # ===滑鼠事件處理===
    def on_left_click(self, r, c):
        if self.is_game_over:
            return
        
        # 第一次按下的時候, 才擺放地雷
        if self.first_click:
            self.first_click = False
            self.place_mines(r, c)
            self.calculate_numbers()
            self.first_click = False

        # 旗標不會被展開
        cell = self.cells[r][c]
        if cell.revealed and cell.flagged:
            return

        # 每次按下, 判斷是否為地雷
        if cell.is_mine():
            cell.exploded = True
            cell.revealed = True
            self.is_game_over = True
            self.game_over()
        elif cell.is_number():
            if cell.revealed:
                self.on_chord_click(r, c)
            else: 
                cell.revealed = True
        elif cell.is_empty():
            self.flood_fill(r, c)
        self.update_board()
        self.check_win_condition()

    def on_right_click(self, r, c):
        if self.is_game_over:
            return
        cell = self.cells[r][c]
        if cell.revealed:
            return
        cell.flagged = not cell.flagged
        self.update_board()

    def on_chord_click(self, r, c):
        if self.is_game_over:
            return
        
        # 只能在 revealed, 數字觸發
        cell = self.cells[r][c]
        if not cell.revealed or not cell.is_number():
            return
        
        flag_count = self.count_flags_around(r, c)
        if flag_count != cell.number:
            return
        
        exploded = False
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr = r + dr
                nc = c + dc
                if 0 <= nr < self.board_height and 0 <= nc < self.board_width:
                    neighbor = self.cells[nr][nc]
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
    
    # ===輔助方法===
    def count_flags_around(self, r, c):
        flag_count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr = r + dr
                nc = c + dc
                if 0 <= nr < self.board_height and 0 <= nc < self.board_width:
                    if self.cells[nr][nc].flagged:
                        flag_count += 1
        return flag_count

    def reveal_all_mines(self):
        for r in range(self.board_height):
            for c in range(self.board_width):
                cell = self.cells[r][c]
                if cell.is_mine():
                    cell.revealed = True
        self.update_board()

    def update_board(self):
        for r in range(self.board_height):
            for c in range(self.board_width):
                cell = self.cells[r][c]
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

    def change_difficulty(self, difficulty):
        self.config = DifficultyConfig(difficulty)
        self.board_width = self.config.board_width
        self.board_height = self.config.board_height
        self.mine_count = self.config.mine_count
        self.frame.destroy()
        self.create_widget()
        self.new_game()
        
# main
if __name__ == "__main__":
    window = Tk()
    window.title("踩地雷")
    game = MineSweeper(window)
    game.start()