from tkinter import *
from tkinter import messagebox
import os
from MineSweeper_Difficulty import DifficultyConfig, Difficulty
from MineSweeper_GameBoard import GameBoard
from MineSweeper_Event import Event 
class BoardManager:
    """管理一個遊戲版塊, 初始化會用到的一些變數"""
    def __init__(self, parent_frame, tile_images, name, config:DifficultyConfig, debug_mode_var, is_opponent:bool):
        self.parent_frame = parent_frame
        self.tile_images = tile_images
        self.name = name
        self.gameBoard = GameBoard(config, name)
        self.buttons = []
        
        self.flagged_count = IntVar(value=0)
        self.is_game_over = False
        self.first_click = True
        self.chord_holding = False
        self.is_opponent = is_opponent
        
        self.debug_mode_var = debug_mode_var  # 這是共有的 debug 變數
        
        self.create_events()
        self.create_ui()
    
    def create_events(self):
        self.on_reveal_cell:Event = Event()
        self.on_toggle_flag_cell:Event = Event()
        self.on_chord_click_cell:Event = Event()
        self.on_chord_press_cell:Event = Event()
        self.on_chord_release_cell:Event = Event()
        self.on_game_over:Event = Event()
        self.on_complete:Event = Event()
    
    def create_ui(self):
        """創建 UI"""
        self.board_frame = Frame(self.parent_frame)
        self.board_frame.pack(side=LEFT, padx=10)        
        # 遊戲板按鈕
        self.buttons_frame = LabelFrame(self.board_frame, text=self.name)
        self.buttons_frame.pack()
        
        self.change_difficulty(DifficultyConfig(Difficulty.EASY))
    
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
    
    def on_reveal(self, r:int, c:int, seed=None):
        """你按下了左鍵"""
        if self.is_game_over:
            return
        if seed is None: 
            seed = int.from_bytes(os.urandom(4), byteorder='big')
            
        # 第一次按下的時候, 才擺放地雷
        self.on_reveal_cell.emit(r, c, seed)
        if self.first_click:
            self.first_click = False
            self.gameBoard.place_mines(r, c, seed)
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
    
    def on_toggle_flag(self, r:int, c:int):
        """你按下了右鍵插旗子"""
        if self.is_game_over:
            return
        
        self.on_toggle_flag_cell.emit(r, c)
        cell = self.gameBoard.get_cell(r, c)
        if cell.revealed:
            return
        
        if self.flagged_count.get() >= self.gameBoard.mine_count: 
            return
        
        cell.flagged = not cell.flagged
        self.update_board()
    
    def on_chord_click(self, r:int, c:int):
        """你想要抄近路，玩的快一些"""
        if self.is_game_over:
            return
         
        self.on_chord_click_cell.emit(r, c)
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
    
    def on_chord_press(self, r:int, c:int):
        """想要展開時的「預視」效果"""
        if self.is_game_over:
            return
        
        self.on_chord_press_cell.emit(r, c)
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
    
    def on_chord_release(self, r:int, c:int):
        """放開按鍵, 觸發 chord_click 的效果"""
        if not self.chord_holding:
            return
        self.on_chord_release_cell.emit(r, c)
        self.chord_holding = False
        self.update_board()
        self.on_chord_click(r, c)
    
    def game_over(self):
        """你爆炸了"""
        self.on_game_over.emit()
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
        self.on_complete.emit()
    
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
    
    def change_difficulty(self, config: DifficultyConfig):
        """更改難度"""
        self.gameBoard = GameBoard(config, self.name)
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
                    command=lambda r=r, c=c: self.on_reveal(r, c)
                )
                btn.bind("<Button-3>", lambda event, r=r, c=c: self.on_toggle_flag(r, c))
                btn.bind("<Button-1>", lambda event, r=r, c=c: self.on_chord_press(r, c))
                btn.bind("<ButtonRelease-1>", lambda event, r=r, c=c: self.on_chord_release(r, c))
                btn.grid(row=r, column=c, padx=0, pady=0)
                if self.is_opponent:
                    btn.config(state="disabled")
                row_buttons.append(btn)
            self.buttons.append(row_buttons)
        
        self.reset()
