from tkinter import *
from tkinter import messagebox
import os
from MineSweeper_Difficulty import DifficultyConfig, Difficulty
from MineSweeper_BoardManager import BoardManager
from MineSweeper_NetworkManager import NetworkManager
from MineSweeper_Event import Event

class MineSweeper:
    """主遊戲類"""
    def __init__(self, window:Tk):
        self.load_images()
        self.create_variable()
        self.create_eventHandler()
        self.create_gameBoard()
        self.create_control_panel()
        self.create_network_panel()
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
        
    def create_variable(self):
        self.window:Tk = window
        self.debug_mode = BooleanVar(value=False)
        self.config = DifficultyConfig(Difficulty.EASY)
        self.board_managers:list[BoardManager] = []
        self.network_manager:NetworkManager = NetworkManager()
        
        self.server_ip_var:StringVar = StringVar(value=self.network_manager.get_local_ip())
        self.server_port_var:StringVar = StringVar(value="12345")
        
        self.client_ip_var:StringVar = StringVar()
        self.client_port_var:StringVar = StringVar()
        
        self.server_message_var:StringVar = StringVar(value="")
        self.client_message_var:StringVar = StringVar(value="")
        
    def create_eventHandler(self):
        # server events, 開關, 連線, 斷線
        self.network_manager.on_start_server_success.subscribe(self.on_networkManager_start_server_success)
        self.network_manager.on_start_server_failed.subscribe(self.on_networkManager_start_server_failed)
        self.network_manager.on_close_server_success.subscribe(self.on_networkManager_close_server_success)
        self.network_manager.on_close_server_failed.subscribe(self.on_networkManager_close_server_failed)
        self.network_manager.on_server_connect_success.subscribe(self.on_networkManager_server_connect_success)
        self.network_manager.on_server_connect_failed.subscribe(self.on_networkManager_server_connect_failed)
        self.network_manager.on_server_disconnect_success.subscribe(self.on_networkManager_server_disconnect_success)
        self.network_manager.on_server_disconnect_failed.subscribe(self.on_networkManager_server_disconnect_failed)
        
        # client events, 連線, 斷線
        self.network_manager.on_client_connect_success.subscribe(self.on_networkManager_client_connect_success)
        self.network_manager.on_client_connect_failed.subscribe(self.on_networkManager_client_connect_failed)
        self.network_manager.on_client_disconnect_success.subscribe(self.on_networkManager_client_disconnect_success)
        self.network_manager.on_client_disconnect_failed.subscribe(self.on_networkManager_client_disconnect_failed)
        
        # 接收訊息
        self.network_manager.on_receive_message_success.subscribe(self.on_networkManager_receive_message_success)
        self.network_manager.on_receive_message_failed.subscribe(self.on_networkManager_receive_message_failed) 
    
    def create_gameBoard(self):
        """創建UI元素"""
        self.frame = Frame(self.window)
        self.frame.pack(padx=20, pady=20)
        
        self.boards_container = Frame(self.frame)
        self.boards_container.pack()
        
        self.player_board = BoardManager(
            self.boards_container,
            self.tile_images,
            "玩家遊戲板",
            self.config.board_width,
            self.config.board_height,
            self.config.mine_count,
            self.debug_mode,
            self.on_board_win
        )
        
        self.opponent_board = BoardManager(
            self.boards_container,
            self.tile_images,
            "對手遊戲板",
            self.config.board_width,
            self.config.board_height,
            self.config.mine_count,
            self.debug_mode,
            self.on_board_win
        )
        self.board_managers.append(self.player_board)
        self.board_managers.append(self.opponent_board)
   
    def create_control_panel(self):
        """控制面板"""
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
        
        reset_button = Button(control_frame, text="重置遊戲", command=self.new_game)
        reset_button.pack(side=LEFT, padx=5)
        
        self.debug_button = Button(control_frame, text="Debug 模式：關閉", command=self.toggle_debug_mode)
        self.debug_button.pack(side=LEFT, padx=5)

    def create_network_panel(self):
        server_frame = LabelFrame(self.window, text="伺服器設定")
        server_frame.pack(pady=10, padx=10, fill="x", side=LEFT)

        Label(server_frame, text="IP:").grid(row=0, column=0)
        self.server_ip_entry = Entry(server_frame, textvariable=self.server_ip_var)
        self.server_ip_entry.grid(row=0, column=1, padx=5)

        Label(server_frame, text="Port:").grid(row=1, column=0)
        self.server_port_entry = Entry(server_frame, textvariable=self.server_port_var)
        self.server_port_entry.grid(row=1, column=1, padx=5)
        
        Label(server_frame, text="訊息:").grid(row=2, column=0)
        self.server_send_message_entry = Entry(server_frame, textvariable=self.server_message_var)
        self.server_send_message_entry.grid(row=2, column=1, padx=5)

        server_button_frame = Frame(server_frame)
        self.start_server_btn = Button(
            server_button_frame,
            text="開啟伺服器",
            command=lambda :self.network_manager.toggle_server(self.server_ip_var.get(), int(self.server_port_var.get()))
        )
        self.start_server_btn.pack(side=LEFT, padx=5)

        self.server_send_message_btn = Button(
            server_button_frame,
            text="發送訊息",
            command=lambda :self.network_manager.send_message(f"[伺服器訊息]{self.server_message_var.get()}")
        )
        self.server_send_message_btn.pack(side=LEFT, padx=5)
        server_button_frame.grid(row=3, columnspan=2, pady=5)

        self.server_status = Label(
            server_frame, 
            text="[伺服器狀態] 未啟動"
        )
        self.server_status.grid(row=4, columnspan=2)
        
        # 客戶端區塊
        client_frame = LabelFrame(self.window, text="客戶端設定")
        client_frame.pack(pady=10, padx=10, fill="x", side=LEFT)

        Label(client_frame, text="目標IP:").grid(row=0, column=0)
        self.client_ip_entry = Entry(client_frame, textvariable=self.client_ip_var)
        self.client_ip_entry.grid(row=0, column=1, padx=5)

        Label(client_frame, text="目標Port:").grid(row=1, column=0)
        self.client_port_entry = Entry(client_frame, textvariable=self.client_port_var)
        self.client_port_entry.grid(row=1, column=1, padx=5)
        
        Label(client_frame, text="訊息:").grid(row=2, column=0)
        self.client_send_message_entry = Entry(client_frame, textvariable=self.client_message_var)
        self.client_send_message_entry.grid(row=2, column=1, padx=5)
        
        client_button_frame = Frame(client_frame)
        self.connect_btn = Button(
            client_button_frame,
            text="連接伺服器",
            command=lambda :self.network_manager.toggle_connection(self.client_ip_var.get(), int(self.client_port_var.get()))
        )
        self.connect_btn.pack(side=LEFT, padx=5)

        self.client_send_message_btn = Button(
            client_button_frame,
            text="發送訊息",
            command=lambda :self.network_manager.send_message(f"[客戶端訊息]{self.client_message_var.get()}")
        )
        self.client_send_message_btn.pack(side=LEFT, padx=5)
        client_button_frame.grid(row=3, columnspan=2, pady=5)


        self.client_status = Label(
            client_frame,
            text="[連線狀態] 未連接"
        )
        self.client_status.grid(row=4, columnspan=2)
        
    def center_window(self):
        """調整視窗大小和位置"""
        self.window.update_idletasks()

        # 計算視窗大小
        board_width = self.config.board_width * 32
        total_width = board_width * len(self.board_managers) + 80 + (20 * (len(self.board_managers) - 1))
        height = self.config.board_height * 32 + 300
        
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - total_width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{total_width}x{height}+{x}+{y}")
        # topmost 
        self.window.attributes("-topmost", True)
              
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
    
    def on_board_win(self):
        """處理遊戲板勝利事件"""
        for i in range(len(self.board_managers)):
            if self.board_managers[i].is_game_over:
                self.board_managers[i].show_all_mines()
                messagebox.showinfo("恭喜", f"{self.board_managers[i].name} 完成了遊戲！")
                
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
    
    def on_networkManager_start_server_success(self, ip:str, port:int):
        self.start_server_btn.config(text="關閉伺服器")
        self.server_status.config(
            text=f"[伺服器狀態] 運行中 ({ip}:{port})", 
            fg="green"
        )
        # disable client buttons
        self.client_send_message_btn.config(state="disabled")
        self.connect_btn.config(state="disabled")
        
    def on_networkManager_start_server_failed(self, e):
        self.server_status.config(
            text=f"[錯誤] 伺服器啟動失敗: {str(e)}", 
            fg="red"
        )
        
    def on_networkManager_close_server_success(self):
        self.start_server_btn.config(text="開啟伺服器")
        self.server_status.config(text="[伺服器狀態] 已關閉", fg="black")

        self.client_send_message_btn.config(state="active")
        self.connect_btn.config(state="active")

    
    def on_networkManager_close_server_failed(self, e):
        self.server_status.config(
            text=f"[錯誤] 伺服器關閉失敗: {str(e)}", 
            fg="red"
        )

    def on_networkManager_server_connect_success(self, addr):
        self.client_status.config(
            text=f"[連線狀態] 已連接 {addr[0]}:{addr[1]}", 
            fg="green"
        )
        print(f"[連線狀態] 已連接 {addr[0]}:{addr[1]}")
    
    def on_networkManager_server_connect_failed(self, e):
        self.client_status.config(
            text=f"[錯誤] 伺服器連接失敗: {str(e)}", 
            fg="red"
        )
        print(f"[錯誤] 伺服器連接失敗: {str(e)}")
        
    def on_networkManager_client_connect_success(self, ip:str, port:int, client_ip:str, client_port:int):
        self.connect_btn.config(text="斷開連接")
        self.server_status.config(
            text=f"[伺服器狀態] 已連接到 {ip}:{port}", 
            fg="green"
        )
        self.client_status.config(text=f"[連線狀態] 已連接 {client_ip}:{client_port}", fg="green")
        self.server_send_message_btn.config(state="disabled")
        self.start_server_btn.config(state="disabled")

    def on_networkManager_server_disconnect_success(self):
        self.client_status.config(text="[連線狀態] 已斷線", fg="red")
        print("[連線狀態] 已斷線")
        self.server_send_message_btn.config(state="active")
        self.start_server_btn.config(state="active")
    
    def on_networkManager_server_disconnect_failed(self, e):
        self.client_status.config(
            text=f"[錯誤] 伺服器斷線失敗: {str(e)}", 
            fg="red"
        )
        print(f"[錯誤] 伺服器斷線失敗: {str(e)}")

    def on_networkManager_client_connect_failed(self, e):
        self.client_status.config(
            text=f"[錯誤] 連接失敗: {str(e)}", 
            fg="red"
        )

    def on_networkManager_client_disconnect_success(self):
        self.connect_btn.config(text="連接伺服器")
        self.client_status.config(text="[連線狀態] 已斷線", fg="red")
        print("客戶端斷掉了")

    def on_networkManager_client_disconnect_failed(self, e):
        self.client_status.config(
            text=f"[錯誤] 客戶端斷線失敗: {str(e)}", 
            fg="red"
        )
        print(f"[錯誤] 客戶端斷線失敗: {str(e)}")

    def on_networkManager_receive_message_success(self, message:str):
        self.client_message_var.set(message)
        print(f"收到訊息: {message}")

    def on_networkManager_receive_message_failed(self, e):
        messagebox.showerror("斷開連線", f"{str(e)}")
# main
if __name__ == "__main__":
    window = Tk()
    window.title("MineSweeper")
    game = MineSweeper(window)
    game.start()
