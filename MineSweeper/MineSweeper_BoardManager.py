from tkinter import *
import os
from MineSweeper_Difficulty import DifficultyConfig, Difficulty
from MineSweeper_GameBoard import GameBoard
from MineSweeper_Event import MyEvent
from MineSweeper_Timer import CountUpTimer
from functools import wraps


def operation_check(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if getattr(self, "is_game_over", True):
            return
        if not getattr(self, "is_ready", False):
            return
        if not getattr(self, "is_game_started", False):
            return
        return method(self, *args, **kwargs)
    return wrapper


class BoardManager:
    """管理一個遊戲版塊, 初始化會用到的一些變數"""
    def __init__(self, parent_frame, tile_images, name, config:DifficultyConfig, debug_mode_var, is_opponent:bool):

        self.parent_frame = parent_frame
        self.board_frame = Frame(self.parent_frame)
        self.board_frame.pack(side=LEFT, padx=10)
        
        self.tile_images = tile_images
        self.name = name
        self.gameBoard = GameBoard(config, name)
        self.buttons = []
        
        self.is_opponent = is_opponent        
        self.debug_mode_var = debug_mode_var  # 這是共有的 debug 變數
        self.create_events()
        self.create_variable()
        self.create_ui()
    
    def create_variable(self):
        self.is_ready = False
        self.is_game_over = False
        self.is_game_started = False
        self.first_click = True
        self.safe_reveal_var = False
        self.chord_holding = False
        self.flagged_count:int = 0
        self.countup_timer = CountUpTimer(self.board_frame)

    def create_events(self):
        self.event_first_reveal_cell:MyEvent = MyEvent()
        self.event_reveal_cell:MyEvent = MyEvent()
        self.event_toggle_flag_cell:MyEvent = MyEvent()
        self.event_chord_click_cell:MyEvent = MyEvent()
        self.event_chord_press_cell:MyEvent = MyEvent()
        self.event_chord_release_cell:MyEvent = MyEvent()
        self.event_game_over:MyEvent = MyEvent()
        self.event_complete:MyEvent = MyEvent()
        self.event_toggle_safe_reveal_var:MyEvent = MyEvent()
        
        # 當第一次揭開格子時, 啟動計時器
        self.event_first_reveal_cell.subscribe(lambda r,c,seed: self.start_timer())
        # 遊戲結束或重置時, 停止並重置計時器
        self.event_game_over.subscribe(lambda *args, **kwargs: self.stop_timer())
        self.event_complete.subscribe(lambda *args, **kwargs: self.stop_timer())

    def create_ui(self):
        """創建 UI"""
        
        # 顯示計時 Label
        self.info_frame = Frame(self.board_frame)
        self.info_frame.pack(fill=X,pady=(0,5))
        
        self.timer_label = Label(self.info_frame, textvariable=self.countup_timer.countdown_var, font=(None, 12))
        self.timer_label.pack(side=LEFT, anchor=W)
        
        # 技能施放按鈕區塊
        self.skill_frame = Frame(self.info_frame)
        self.skill_frame.pack(side=RIGHT, anchor=E)
        
        self.safe_reveal_button = Button(self.skill_frame, text="安全展開", command=self.on_toggle_safe_reveal_var)
        self.safe_reveal_button.pack()
 
        # 遊戲板按鈕
        self.buttons_frame = Frame(self.board_frame)
        # self.buttons_frame = LabelFrame(self.board_frame, text=self.name)
        self.buttons_frame.pack()
        
        # change_difficulty 會呼叫 reset
        self.change_difficulty(DifficultyConfig(Difficulty.EASY))
        

    def start_timer(self):
        self.is_game_started = True
        self.countup_timer.reset()
        self.countup_timer.start_countdown()

    def stop_timer(self):
        self.countup_timer.stop_countdown()

    def get_timer_value(self):
        return self.countup_timer.countdown_var.get()

    def reset(self, remember_ready_state:bool=False):
        """重置遊戲板"""
        if not remember_ready_state: 
            self.is_ready = False
        self.is_game_started = False
        self.is_game_over = False
        self.first_click = True
        self.safe_reveal_var = False
        
        self.safe_reveal_button.config(text="安全展開")
        self.safe_reveal_button.config(state=DISABLED)
        
        self.gameBoard.reset()
        self.countup_timer.reset()
        self.update_board()
        # 重置計時器顯示
        self.countup_timer.reset()
    
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
    
    @operation_check
    def on_reveal(self, r:int, c:int, seed=None):
        """你按下了左鍵"""
        if seed is None: 
            seed = int.from_bytes(os.urandom(4), byteorder='big')
            
        # 旗標不會被展開
        cell = self.gameBoard.get_cell(r, c)
        
        if cell.revealed or cell.flagged:
            return 
        
        # 第一次按下的時候, 才擺放地雷
        if self.first_click:
            if self.is_opponent == False:
                self.safe_reveal_button.config(state=ACTIVE)
            self.first_click = False
            self.event_first_reveal_cell.emit(r, c, seed)
            self.gameBoard.place_mines(r, c, seed)
            self.gameBoard.calculate_numbers()

        # 每次按下, 判斷是否為地雷
        self.event_reveal_cell.emit(r, c)
        if cell.is_mine():
            if self.safe_reveal_var == True:
                cell.flagged = True
                cell.revealed = True 
                self.safe_reveal_var = False
                self.safe_reveal_button.config(text="安全展開")
                self.safe_reveal_button.config(state=DISABLED)
            else: 
                cell.exploded = True
                cell.revealed = True
                self.game_over()
        elif cell.is_number():
            cell.revealed = True
        elif cell.is_empty():
            self.flood_fill(r, c)

        self.update_board()
        self.check_win_condition()
        
    def on_toggle_safe_reveal_var(self):
        self.event_toggle_safe_reveal_var.emit()
        self.safe_reveal_var = not self.safe_reveal_var
        self.safe_reveal_button.config(foreground="green" if self.safe_reveal_var == True else "red")
        
    def on_toggle_flag(self, r:int, c:int):
        """你按下了右鍵插旗子"""        
        self.event_toggle_flag_cell.emit(r, c)
        cell = self.gameBoard.get_cell(r, c)
        if cell.revealed:
            return
        
        if self.flagged_count >= self.gameBoard.mine_count: 
            return
        
        cell.flagged = not cell.flagged
        self.update_board()
    
    @operation_check
    def on_chord_click(self, r:int, c:int):
        """你想要抄近路，玩的快一些"""         
        cell = self.gameBoard.get_cell(r, c)
        if not cell.revealed or not cell.is_number():
            return
        
        flag_count = self.gameBoard.count_flags_around(r, c)
        if flag_count != cell.number:
            return
        
        self.event_chord_click_cell.emit(r, c)
        exploded = False
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr = r + dr
                nc = c + dc
                if self.gameBoard.is_valid_position(nr, nc):
                    self.on_reveal(nr, nc)
    
    @operation_check
    def on_chord_press(self, r:int, c:int):
        """想要展開時的「預視」效果"""
        cell = self.gameBoard.get_cell(r, c)
        if not cell.revealed or not cell.is_number():
            return
            
        flag_count = self.gameBoard.count_flags_around(r, c)
        if flag_count != cell.number:
            return
            
        self.event_chord_press_cell.emit(r, c)
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
        self.event_chord_release_cell.emit(r, c)
        self.chord_holding = False
        self.update_board()
        self.on_chord_click(r, c)
        
    def check_win_condition(self):
        """勝利唾手可得"""
        for r in range(self.gameBoard.height):
            for c in range(self.gameBoard.width):
                cell = self.gameBoard.get_cell(r, c)
                if not cell.is_mine() and not cell.revealed:
                    return                    
        self.complete()
    
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

    def game_over(self):
        """你爆炸了"""
        self.is_game_over = True
        msg = f"遊戲結束{self.name} 踩到地雷了！"
        self.reveal_all_mines()
        self.event_game_over.emit(msg)
        
    def complete(self):
        self.is_game_over = True
        msg = f"{self.name}完成了!"
        self.event_complete.emit(msg)
        
    def change_difficulty(self, config: DifficultyConfig):
        """更改難度"""
        self.gameBoard = GameBoard(config, self.name)
        self.buttons = []
        self.buttons_frame.destroy()
        self.buttons_frame = Frame(self.board_frame)
        # self.buttons_frame = LabelFrame(self.board_frame, text=self.name)
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
        self.reset(remember_ready_state=True)