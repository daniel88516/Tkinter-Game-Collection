from tkinter import * 
import os
from MineSweeper_Difficulty import DifficultyConfig, Difficulty
from MineSweeper_BoardManager import BoardManager
from MineSweeper_NetworkManager import NetworkManager
from MineSweeper_GameMessage import GameMessage, GameMessageType
from MineSweeper_ChatManager import ChatManager
from MineSweeper_Timer import CountDownTimer
class MineSweeper:
    """主遊戲類"""
    def __init__(self, window:Tk):
        self.window = window
        self.container = Frame(self.window)
        self.container.pack(fill="both", expand=True)
        
        self.load_images()
        self.create_variable()
        self.create_counter_eventHandler() # timer 在 create_variable 當中
        
        self.create_gameBoard()
        self.create_gameBoard_eventHandler()
        
        self.create_network_panel()
        self.create_network_eventHandler()
        
        self.create_control_panel()
        
        self.create_chat_panel()
        self.create_chat_eventHandler()
        
        
        self.center_window()
        
        # 處理網路傳訊
        self.container.after(100, self._poll_incoming_message)

    def start(self):
        """啟動遊戲"""
        self.container.mainloop()
        
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
        
    def create_variable(self):
        self.debug_mode = BooleanVar(value=False)
        self.board_managers:list[BoardManager] = []
        self.config = DifficultyConfig(Difficulty.EASY)
        self.network_manager:NetworkManager = NetworkManager()
        self.chat_manager:ChatManager = ChatManager()
        
        self.message_var:StringVar = StringVar(value="")
        self.game_started:bool = False
        self.countdown_timer = CountDownTimer(self.container)
         
    def create_gameBoard(self):
        """創建UI元素"""
        self.gameBoard_frame = Frame(self.container)
        self.gameBoard_frame.pack(padx=20, pady=10)
        
        self.boards_container = Frame(self.gameBoard_frame)
        self.boards_container.pack()
        
        self.player_board = BoardManager(
            self.boards_container,
            self.tile_images,
            "你",
            self.config,
            self.debug_mode,
            False
        )
        
        self.opponent_board = BoardManager(
            self.boards_container,
            self.tile_images,
            "你的對手",
            self.config,
            self.debug_mode,
            True
        )
        self.board_managers.append(self.player_board)
        self.board_managers.append(self.opponent_board)
    
    def create_gameBoard_eventHandler(self):
        self.player_board.on_first_reveal_cell.subscribe(self.on_player_first_reveal_cell)
        self.player_board.on_reveal_cell.subscribe(self.on_player_reveal_cell)
        self.player_board.on_toggle_flag_cell.subscribe(self.on_player_toggle_flag_cell)
        self.player_board.on_chord_click_cell.subscribe(self.on_player_chord_click_cell)
        self.player_board.on_chord_press_cell.subscribe(self.on_player_chord_press_cell)
        self.player_board.on_chord_release_cell.subscribe(self.on_player_chord_release_cell)
        self.player_board.on_game_over.subscribe(self.on_player_game_over)
        self.player_board.on_complete.subscribe(self.on_player_complete)
   
    def create_network_eventHandler(self):
        # server events, 開關, 連線, 斷線
        self.network_manager.on_server_connect_success.subscribe(self.on_networkManager_server_connect_success)
        self.network_manager.on_server_disconnect_success.subscribe(self.on_networkManager_server_disconnect_success)
        self.network_manager.on_client_connect_success.subscribe(self.on_networkManager_client_connect_success)
        self.network_manager.on_client_disconnect_success.subscribe(self.on_networkManager_client_disconnect_success)
        
        # 接收訊息
        self.network_manager.on_receive_message_failed.subscribe(self.on_networkManager_receive_message_failed) 
        
        self.message_handlers = {    
            GameMessageType.READY_STATE: lambda self, msg: self.opponent_toggle_ready_state(msg.data["state"]),
            GameMessageType.FIRST_CELL_REVEAL: lambda self, msg: self.opponent_board.on_reveal(msg.data["row"], msg.data["col"], msg.data["seed"]),                            
            GameMessageType.CELL_REVEAL: lambda self, msg: self.opponent_board.on_reveal(msg.data["row"], msg.data["col"]),
            GameMessageType.TOGGLE_FLAG: lambda self, msg: self.opponent_board.on_toggle_flag(msg.data["row"], msg.data["col"]),
            GameMessageType.CHORD_CLICK: lambda self, msg: self.opponent_board.on_chord_click(msg.data["row"], msg.data["col"]),
            GameMessageType.CHORD_PRESS: lambda self, msg: self.opponent_board.on_chord_press(msg.data["row"], msg.data["col"]),
            GameMessageType.CHORD_RELEASE: lambda self, msg: self.opponent_board.on_chord_release(msg.data["row"], msg.data["col"]),
            GameMessageType.GAME_OVER: lambda self, msg: self.opponent_board.game_over(),
            GameMessageType.GAME_COMPLETE: lambda self, msg: self.opponent_board.complete(),
            GameMessageType.RESET: lambda self, msg: self.new_game(),
            GameMessageType.CHANGE_DIFFICULTY: lambda self,msg :self.change_difficulty(msg.data["difficulty"]),
        }
   
    def create_counter_eventHandler(self):
        self.countdown_timer.on_counter_change.subscribe(self.on_timer_count_change)
        self.countdown_timer.on_count_end.subscribe(self.on_timer_count_end)
        
    def create_control_panel(self):
        """控制面板"""
        control_frame = Frame(self.gameBoard_frame)
        control_frame.pack(pady=5)
        
        # 難度按鈕
        difficulty_frame = Frame(control_frame)
        difficulty_frame.pack(side=TOP, pady=5)
        
        self.difficulty_buttons:list[Button] = []
        for diff in Difficulty: 
            btn = Button(
                difficulty_frame,
                text=DifficultyConfig.CONFIGS[diff]["name"],
                command=lambda d=diff: [self.change_difficulty(d), self.send_change_difficulty_message(d)],
                state=DISABLED
            )
            btn.pack(side=LEFT, padx=5)
            self.difficulty_buttons.append(btn)
        
        self.ready_button = Button(control_frame, fg="red", text="未準備", command=self.toggle_ready_state, state=DISABLED)
        self.ready_button.pack(side=LEFT, padx=5)
        
        self.reset_button = Button(control_frame, text="重置遊戲", command= lambda: [self.new_game(), self.send_reset_message()], state=DISABLED)
        self.reset_button.pack(side=LEFT, padx=5)
        
        self.debug_button = Button(control_frame, text="Debug 模式：關閉", command=self.toggle_debug_mode)
        self.debug_button.pack(side=LEFT, padx=5)

    def create_network_panel(self):
        self.network_frame = Frame(self.container)
        self.network_frame.pack()
        self.network_manager.create_widget(self.network_frame)
                
    def create_chat_panel(self):
        """聊天區域"""
        self.chat_manager.create_widget(self.network_frame)
        
    def create_chat_eventHandler(self):
        self.chat_manager.on_send_message.subscribe(self.on_chatManager_send_message)
        
    def center_window(self):
        """調整視窗大小和位置"""
        
        self.window.update_idletasks()

        # 計算視窗大小
        board_width = self.config.board_width * 32
        total_width = board_width * len(self.board_managers) + 250 + (20 * (len(self.board_managers) - 1))
        height = self.config.board_height * 32 + 350
        
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - total_width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{total_width}x{height}+{x}+{y}")
        # topmost 
        self.window.attributes("-topmost", True)
        
    def toggle_ready_state(self):
        self.player_board.is_ready = not self.player_board.is_ready
        if self.player_board.is_ready:
            self.ready_button.config(fg="green", text="已準備")
            self.reset_button.config(state=DISABLED)
            for btn in self.difficulty_buttons:
                btn.config(state=DISABLED)
        else:
            self.ready_button.config(fg="red", text="未準備")
            self.reset_button.config(state=ACTIVE)
            for btn in self.difficulty_buttons:
                btn.config(state=ACTIVE)
        
        message:GameMessage = GameMessage(
            type=GameMessageType.READY_STATE,
            data={"state":self.player_board.is_ready}
        )
        self.network_manager.send_game_message(message)
        if self.can_start_game():
            self.player_board.countup_timer.reset()
            self.opponent_board.countup_timer.reset()
            self.countdown_timer.start_countdown()
                     
    def opponent_toggle_ready_state(self, ready_state:bool):
        self.opponent_board.is_ready = ready_state
        if ready_state == True:        
            self.chat_manager.add_message("對手已準備", from_self=False)
        else:
            self.chat_manager.add_message("對手未準備", from_self=False)
        if self.can_start_game():
            self.player_board.countup_timer.reset()
            self.opponent_board.countup_timer.reset()
            self.countdown_timer.start_countdown()
    
    def can_start_game(self) -> bool:
        return self.player_board.is_ready and self.opponent_board.is_ready
    
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
                        
    def send_reset_message(self):
        """傳送重置的訊息"""
        # 不能放到 new_game 當中, 因為會彼此傳來傳去
        message:GameMessage = GameMessage(type=GameMessageType.RESET,data={})
        self.network_manager.send_game_message(message)

    def change_difficulty(self, difficulty: Difficulty):
        """更改難度"""
        if self.config != DifficultyConfig(difficulty):
            print("Not The Same")
            self.config = DifficultyConfig(difficulty)
            for board_manager in self.board_managers:
                board_manager.change_difficulty(self.config)
            self.center_window()
        else: 
            # 難度不變,但需要清空場地
            self.new_game()
            self.send_reset_message() 
    def send_change_difficulty_message(self, difficulty: Difficulty):
        message:GameMessage = GameMessage(GameMessageType.CHANGE_DIFFICULTY, data={"difficulty":difficulty.name})
        self.network_manager.send_game_message(message)        
    
    def _poll_incoming_message(self):
        """使用 thread, after, 每 0.1 秒就處理累積下來的請求"""
        while not self.network_manager.recv_queue.empty():
            msg = self.network_manager.recv_queue.get()
            self.resolve_message(msg)
            self.network_manager.recv_queue.task_done()
        self.container.after(100, self._poll_incoming_message)
        
    def resolve_message(self, message):
        if not isinstance(message, GameMessage):
            self.chat_manager.add_message(message, from_self=False)
            print(f"收到一般訊息: {message}")
            return             
        handler = self.message_handlers.get(message.type)
        if handler: 
            handler(self, message)
        else: 
            print("沒有找到訊息的對應處理方法")
            
    def on_networkManager_server_connect_success(self):
        self.change_difficulty(Difficulty.EASY)
        self.send_change_difficulty_message(Difficulty.EASY)
        self.config_control_panel_buttons(ACTIVE)
        
    def on_networkManager_server_disconnect_success(self):
        self.new_game()
        self.config_control_panel_buttons(DISABLED)
                
    def on_networkManager_client_connect_success(self):
        self.config_control_panel_buttons(ACTIVE)
        
    def on_networkManager_client_disconnect_success(self):
        self.new_game()
        self.config_control_panel_buttons(DISABLED)
        
    def on_networkManager_receive_message_failed(self):
        self.new_game()
        self.config_control_panel_buttons(DISABLED)
    
    def config_control_panel_buttons(self, state):
        self.ready_button.config(text="未準備", fg="red", state=state)
        self.chat_manager.send_btn.config(state=state)
        self.reset_button.config(state=state)
        for btn in self.difficulty_buttons:
            btn.config(state=state)
        
    def on_player_first_reveal_cell(self, r:int, c:int, seed:int):
        message:GameMessage = GameMessage(
            type=GameMessageType.FIRST_CELL_REVEAL,
            data={"row":r, "col":c, "seed":seed}
        )
        self.network_manager.send_game_message(message)
        
    def on_player_reveal_cell(self, r:int, c:int):
        message:GameMessage = GameMessage(
            type=GameMessageType.CELL_REVEAL,
            data={"row":r, "col":c}
        )
        self.network_manager.send_game_message(message)
        
    def on_player_toggle_flag_cell(self, r:int, c:int):
        message:GameMessage = GameMessage(
            type=GameMessageType.TOGGLE_FLAG,
            data={"row":r, "col":c}
        )
        self.network_manager.send_game_message(message)

    def on_player_chord_click_cell(self, r:int, c:int):
        message:GameMessage = GameMessage(
            type=GameMessageType.CHORD_CLICK,
            data={"row":r, "col":c}
        )
        self.network_manager.send_game_message(message)
        
    def on_player_chord_press_cell(self, r:int, c:int):
        message:GameMessage = GameMessage(
            type=GameMessageType.CHORD_PRESS,
            data={"row":r, "col":c}
        )
        self.network_manager.send_game_message(message)
        
    def on_player_chord_release_cell(self, r:int, c:int):
        message:GameMessage = GameMessage(
            type=GameMessageType.CHORD_RELEASE,
            data={"row":r, "col":c}
        )
        self.network_manager.send_game_message(message)
    
    def on_player_game_over(self, msg:str):
        message:GameMessage = GameMessage(
            type=GameMessageType.GAME_OVER,
            data={}
        )
        self.network_manager.send_game_message(message)

    def on_player_complete(self, msg:str):
        """處理遊戲板勝利事件"""
        message:GameMessage = GameMessage(
            type=GameMessageType.GAME_COMPLETE,
            data={"result":"對方完成了!"}
        )
        self.network_manager.send_game_message(message)
        
    def on_chatManager_send_message(self, message:str):
        self.network_manager.send_message(message)

    def on_timer_count_change(self, msg:str):
        self.network_manager.send_message(msg)
        
    def on_timer_count_end(self):
        for gameBoard in self.board_managers:
            gameBoard.is_game_started = True
        self.config_control_panel_buttons(DISABLED)
        
# main
if __name__ == "__main__":
    window = Tk()
    window.title("MineSweeper")
    game = MineSweeper(window)
    game.start()
