import tkinter as tk
from tkinter import messagebox
import random
import os

class Cell:
    def __init__(self, row, col):
        self.row      = row 
        self.col      = col     
        self.type     = "empty" # "empty", "mine", "number"
        self.number   = 0
        self.revealed = False
        self.flagged  = False
        self.exploded = False

class MineSweeper:
    def __init__(self, window, board_width=16, board_height=16, mine_count=32):
        self.window     = window
        self.board_width  = board_width
        self.board_height = board_height
        self.mine_count = mine_count
        self.cells      = []
        self.buttons    = []    
            
        self.center_window(800, 600)
        self.load_images()
        self.create_variable()
        self.create_widget()
        self.create_control_panel()
        self.new_game()
    
    def start(self):
        self.window.mainloop()
        
    def center_window(self, width=800, height=900):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - width) // 2
        y = (self.window.winfo_screenheight() - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
    def load_images(self):
        base_path = os.path.join(os.path.dirname(__file__), "Images")
        self.tile_images = {}
        for i in range(1, 9):
            self.tile_images[f"Tile{i}"] = tk.PhotoImage(file=os.path.join(base_path, f"Tile{i}.png"))
        self.tile_images["TileEmpty"]    = tk.PhotoImage(file=os.path.join(base_path, "TileEmpty.png"))
        self.tile_images["TileExploded"] = tk.PhotoImage(file=os.path.join(base_path, "TileExploded.png"))
        self.tile_images["TileFlag"]     = tk.PhotoImage(file=os.path.join(base_path, "TileFlag.png"))
        self.tile_images["TileUnknown"]  = tk.PhotoImage(file=os.path.join(base_path, "TileUnknown.png"))
        self.tile_images["TileMine"]     = tk.PhotoImage(file=os.path.join(base_path, "TileMine.png"))

    def create_variable(self):
        self.is_game_over  = False
        self.debug_mode = False
        self.first_click = True
        
    def create_widget(self):
        self.frame      = tk.Frame(self.window)
        self.frame.pack()
        for r in range(self.board_height):
            row_buttons = []
            for c in range(self.board_width):
                btn = tk.Button(
                    self.frame,
                    image=self.tile_images["TileUnknown"],
                    relief="flat",
                    borderwidth=0,
                    highlightthickness=0,
                    command=lambda r=r, c=c: self.on_left_click(r, c)  # 左鍵點擊
                )
                btn.bind("<Button-3>", lambda event, r=r, c=c: self.on_right_click(r, c))  # 右鍵點擊
                btn.bind("<Button-2>", lambda event, r=r, c=c: self.on_chord_click(r, c)) # 中鍵雙擊
                btn.grid(row=r, column=c, padx=0, pady=0)
                row_buttons.append(btn)
            self.buttons.append(row_buttons)
        self.reset_button = tk.Button(self.window, text="重置遊戲", command=self.new_game)
        self.reset_button.pack(pady=10)
        
    def create_control_panel(self):
        # 建立控制面板
        control_frame = tk.Frame(self.window)
        control_frame.pack(pady=5)
        
        self.reset_button = tk.Button(control_frame, text="重置遊戲", command=self.new_game)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.debug_button = tk.Button(control_frame, text="Debug 模式：關閉",  command=self.toggle_debug_mode)
        self.debug_button.pack(side=tk.LEFT, padx=5)

    def toggle_debug_mode(self):
        self.debug_mode = not self.debug_mode
        self.debug_button.config(text=f"Debug 模式：{'開啟' if self.debug_mode else '關閉'}")
        self.update_board()
        
    def new_game(self):
        self.is_game_over = False
        self.first_click = True
        self.cells = [[Cell(r, c) for c in range(self.board_width)] for r in range(self.board_height)]
        # self.place_mines()
        # self.calculate_numbers()
        self.update_board()

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
            if (r, c) not in safe_cells and self.cells[r][c].type != "mine":
                self.cells[r][c].type = "mine"
                count += 1

    def calculate_numbers(self):
        for r in range(self.board_height):
            for c in range(self.board_width):
                cell = self.cells[r][c]
                if cell.type == "mine":
                    continue
                mine_count = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr = r + dr
                        nc = c + dc
                        if 0 <= nr < self.board_height and 0 <= nc < self.board_width:
                            if self.cells[nr][nc].type == "mine":
                                mine_count += 1
                if mine_count > 0:
                    cell.type   = "number"
                    cell.number = mine_count

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
        if cell.type == "mine":
            cell.exploded = True
            cell.revealed = True
            self.is_game_over = True
            self.game_over()
        elif cell.type == "number":
            if cell.revealed:
                self.on_chord_click(r, c)
            else: 
                cell.revealed = True
        elif cell.type == "empty":
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
        print(f"chord click: row{r}, col{c}")
        if self.is_game_over:
            return
        
        # 只能在 revealed, 數字觸發
        cell = self.cells[r][c]
        if not cell.revealed or cell.type != "number":
            return
        
        flag_count = self.count_flags_around(r, c)
        if flag_count != cell.number:
            print(f"flag_count{flag_count} not equal to cellnumber: {cell.number}")
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
                        if neighbor.type=="mine":
                            neighbor.exploded = True
                            neighbor.revealed = True
                            exploded = True
                        elif neighbor.type == "number":
                            neighbor.revealed = True
                        else: # empty
                            self.flood_fill(nr, nc)
        if exploded:
            self.is_game_over = True
            self.game_over()
            
        self.update_board()
        if not exploded:
            self.check_win_condition()

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

    def flood_fill(self, r, c):
        if not (0 <= r < self.board_height and 0 <= c < self.board_width):
            return
        cell = self.cells[r][c]
        if cell.revealed or cell.flagged:
            return
        cell.revealed = True
        if cell.type == "empty":
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr = r + dr
                    nc = c + dc
                    if 0 <= nr < self.board_height and 0 <= nc < self.board_width:
                        neighbor = self.cells[nr][nc]
                        if not neighbor.revealed and neighbor.type != "mine":
                            self.flood_fill(nr, nc)

    def game_over(self):
        self.reveal_all_mines()
        messagebox.showinfo("遊戲結束", "你踩到地雷了！")
        
    def reveal_all_mines(self):
        for r in range(self.board_height):
            for c in range(self.board_width):
                cell = self.cells[r][c]
                if cell.type == "mine":
                    cell.revealed = True
        self.update_board()

    def check_win_condition(self):
        for r in range(self.board_height):
            for c in range(self.board_width):
                cell = self.cells[r][c]
                if cell.type != "mine" and not cell.revealed:
                    return
        self.is_game_over = True
        messagebox.showinfo("恭喜", "你贏了！")

    def update_board(self):
        for r in range(self.board_height):
            for c in range(self.board_width):
                cell = self.cells[r][c]
                btn = self.buttons[r][c]
                
                if self.debug_mode and cell.type == "mine" and not cell.revealed:
                    img = self.tile_images["TileMine"]
                elif cell.revealed:
                    if cell.type == "mine":
                        if cell.exploded:
                            img = self.tile_images["TileExploded"]
                        else:
                            img = self.tile_images["TileMine"]
                    elif cell.type == "number":
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

# main
if __name__ == "__main__":
    window = tk.Tk()
    window.title("踩地雷")
    game = MineSweeper(window)
    game.start()