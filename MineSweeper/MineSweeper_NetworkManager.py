import socket, threading, json, queue, time
from MineSweeper_Event import MyEvent
from MineSweeper_GameMessage import GameMessage, GameMessageType
from tkinter import * 

class NetworkManager:    
    def __init__(self):
        self.create_events()
        self.create_variable()
        
        self.send_queue = queue.Queue()
        self.recv_queue = queue.Queue()
        
        self.sent_messages = [] # 記錄所有傳送過的訊息 (message, interval)
        self.last_message_time = None
        
        threading.Thread(target=self._send_loop, daemon=True).start()
        
    def create_events(self):
        self.on_server_connect_success: MyEvent = MyEvent()   
        self.on_server_disconnect_success: MyEvent = MyEvent()
        self.on_client_connect_success: MyEvent = MyEvent()
        self.on_client_disconnect_success: MyEvent = MyEvent() 
        self.on_receive_message_failed: MyEvent = MyEvent() 
        # 訊息使用 polling 讀取   
                
    def create_variable(self):
        self.server_socket = None
        self.client_socket = None
        self.is_server_running = False
        self.connection_status = False

        self.server_ip_var:StringVar = StringVar(value=self.get_local_ip())
        self.server_port_var:StringVar = StringVar(value="12345")
        
        self.client_ip_var:StringVar = StringVar(value=self.get_local_ip())
        self.client_port_var:StringVar = StringVar(value="12345")
        
    def create_widget(self, parent_frame:Frame):
        # self.network_frame = parent_frame
        self.network_frame = Frame(parent_frame)
        self.network_frame.pack(padx=20, side=LEFT)
        
        server_frame = LabelFrame(self.network_frame, text="伺服器設定")
        server_frame.pack(pady=10, fill="x", side=TOP)
        
        Label(server_frame, text="IP:").grid(row=0, column=0)
        self.server_ip_entry = Entry(server_frame, textvariable=self.server_ip_var)
        self.server_ip_entry.grid(row=0, column=1, padx=5)

        Label(server_frame, text="Port:").grid(row=1, column=0)
        self.server_port_entry = Entry(server_frame, textvariable=self.server_port_var)
        self.server_port_entry.grid(row=1, column=1, padx=5)
        
        self.start_server_btn = Button(
            server_frame,
            text="開啟伺服器",
            command=lambda :self.toggle_server(self.server_ip_var.get(), int(self.server_port_var.get()))
        )
        self.start_server_btn.grid(row=2, columnspan=2, padx=5)

        self.server_status = Label(
            server_frame, 
            text="[伺服器狀態] 未啟動"
        )
        self.server_status.grid(row=4, columnspan=2)

        # 客戶端區塊
        client_frame = LabelFrame(self.network_frame, text="客戶端設定")
        client_frame.pack(pady=10, fill="x")

        Label(client_frame, text="目標IP:").grid(row=0, column=0)
        self.client_ip_entry = Entry(client_frame, textvariable=self.client_ip_var)
        self.client_ip_entry.grid(row=0, column=1, padx=5)

        Label(client_frame, text="目標Port:").grid(row=1, column=0)
        self.client_port_entry = Entry(client_frame, textvariable=self.client_port_var)
        self.client_port_entry.grid(row=1, column=1, padx=5)
        
        self.connect_btn = Button(
            client_frame,
            text="連接伺服器",
            command=lambda :self.toggle_connection(self.client_ip_var.get(), int(self.client_port_var.get()))
        )
        self.connect_btn.grid(row=3, columnspan=2, padx=5)

        self.client_status = Label(
            client_frame,
            text="[連線狀態] 未連接"
        )
        self.client_status.grid(row=4, columnspan=2, padx=5)
        
        self.debug_frame = LabelFrame(self.network_frame, text="除錯工具")
        # 使用 thread 接收訊息
        self.debug_window = Toplevel(parent_frame)
        self.debug_window.title("除錯工具")
        self.debug_window.geometry("300x200")
        self.debug_frame = LabelFrame(self.debug_window, text="除錯工具")
        self.debug_frame.pack(padx=10, pady=10, fill="both", expand=True)

        Button(self.debug_frame, text="儲存傳送訊息", command=self.export_sent_messages).pack(fill="x", pady=2)
        Button(self.debug_frame, 
            text="發送測試訊息", 
            command=lambda: threading.Thread(target=self.auto_sent_message, daemon=True).start()).pack(fill="x", pady=2)
        Button(self.debug_frame, 
            text="接收測試訊息", 
            command=lambda: threading.Thread(target=self.auto_receive_message, daemon=True).start()).pack(fill="x", pady=2)
    
    def get_local_ip(self):
        try:
            # 建立一個 UDP socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # 連接到一個外部伺服器（不需要真的發送數據）
            s.connect(("8.8.8.8", 80))
            # 獲取本機 IP
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"  # 如果取得失敗，返回 localhost
        
    def toggle_server(self, ip:str, port:int):
        if not self.is_server_running:
           self.start_server(ip, port) 
        else:
            self.stop_server()

    def start_server(self, ip:str, port:int):
        try:
            self.is_server_running = True
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((ip, port))
            self.server_socket.listen(5)
            # 啟動伺服器監聽線程
            server_thread = threading.Thread(target=self.listen_clients, daemon=True)
            server_thread.start()
            print(f"NetworkManager: 伺服器啟動成功, {ip}:{port}")
            self.on_start_server_success(ip, port)
        except Exception as e:
            print(f"NetworkManager: 伺服器啟動失敗: {str(e)}")
            self.start_server_failed(e)
            return False
        
    def stop_server(self):
        if not self.is_server_running:
            return
        try:
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
            self.is_server_running = False
            self.connection_status = False
            print("NetworkManager: 伺服器關閉")
            self.close_server_success()
            self.client_disconnect_success()
            self.on_server_disconnect_success.emit()
    
        except Exception as e:
            print("NetworkManager: 伺服器關閉失敗" + str(e))
            self.close_server_failed(e)
        
    def listen_clients(self):
        while self.is_server_running:
            try:
                client, addr = self.server_socket.accept()
                
                # 如果已經連上，拒絕新的連線
                if self.client_socket: 
                    print(f"NetworkManager: 已有客戶端連線，拒絕新的連線，來自 {addr}")
                    client.close()
                    continue

                self.client_socket = client
                self.connection_status = True
                self.receive_thread = threading.Thread(target=self.receive_message, daemon=True)
                self.receive_thread.start()
                print(f"NetworkManager: 連上了客戶端, {addr}")   
                self.server_connect_success(addr)
            # winerror 10038: socket operation on non-socket
            except OSError as e:
                pass
            except Exception as e:
                print("NetworkManager: 傾聽客戶端失敗" + str(e))
                self.server_connect_failed(e)
                return False

    def toggle_connection(self, ip:str, port:int):
        try: 
            if not self.connection_status:
                self.connect_to_server(ip, port)
            else:
                self.disconnect()
        except ValueError as e:
            self.on_error(e)

    def connect_to_server(self, ip:str, port:int):
        try:
            self.connection_status = True
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, port))
            print(f"NetworkManager: 客戶端連線成功")
            client_ip, client_port = self.client_socket.getsockname()
            self.client_connect_success(ip, port, client_ip, client_port)
            
            hostname = socket.gethostname()
            identify_msg:GameMessage = GameMessage(
                type=GameMessageType.IDENTIFY,
                data={"identify": hostname}
            )
            self.send_game_message(identify_msg)
            
            self.receive_thread = threading.Thread(target=self.receive_message, daemon=True)
            self.receive_thread.start()
        except Exception as e:
            print(f"NetworkManager: 客戶端連線失敗: {str(e)}")
            self.client_connect_failed(e)

    def disconnect(self):
        try:
            self.client_socket.close()
            self.client_socket = None
            self.connection_status = False
            print(f"NetworkManager: 客戶端斷線成功")
            self.client_disconnect_success()
        except Exception as e:
            print(f"NetworkManager: 客戶端斷線失敗: {str(e)}")
            self.client_disconnect_failed(e)

    def _send_loop(self):
        while True:
            msg = self.send_queue.get()
            if self.client_socket and self.connection_status:
                try: 
                    self.client_socket.send((msg+"\n").encode('utf-8'))
                    print(f"NetworkManager: 傳送訊息: {msg}")
                except Exception as e:
                    print(f"Network Manager: 傳送訊息失敗 {e}")
                finally:
                    self.send_queue.task_done()
                
    def send_game_message(self, message:GameMessage):
        """傳送遊戲訊息"""
        try: 
            json_str = message.to_json()
            self.send_message(json_str)
        except Exception as e:
            print(f"NetworkManager: 傳送遊戲訊息失敗{str(e)}")
            
    def send_message(self, message:str):
        """傳送訊息"""
        if not self.client_socket:
            print("NetworkManager: 沒有連線, 無法傳訊")
            return            
        try:
            # 紀錄訊息和傳送間隔
            now = time.time()
            if self.last_message_time is None: 
                interval = 0.0
            else: 
                interval = now - self.last_message_time
            self.last_message_time = now 
            self.sent_messages.append((message, interval))
            
            self.send_queue.put(message)
            # self.client_socket.send(message.encode('utf-8'))
            print(f"NetworkManager: 放入訊息: {message}")
        except Exception as e:
            print(f"NetworkManager: 放入訊息失敗: {str(e)}")
            
    def receive_message(self):
        buffer = ""
        while self.connection_status:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                buffer += data
                while '\n' in buffer:
                    msg, buffer = buffer.split('\n', 1)
                    if not msg:
                        continue
                    # 嘗試解析遊戲訊息
                    try:
                        game_message = GameMessage.from_json(msg)
                        print(f"NetworkManager: 收到遊戲訊息: {game_message}")
                        if game_message.type == GameMessageType.IDENTIFY:
                            self.handle_identify_message(game_message)
                        else:
                            self.recv_queue.put(game_message)
                    except json.JSONDecodeError:
                        # 如果不是遊戲訊息，當作一般訊息處理
                        self.recv_queue.put(msg)
            except Exception as e:
                self.receive_message_failed(e)
                print(f"NetworkManager: 接收訊息失敗: {str(e)}")
                break
        if self.is_server_running == False:
            self.stop_server()
            print("NetworkManager: 伺服器關閉")
        else:
            self.disconnect()
            print("NetworkManager: 客戶端斷線")
        
    def handle_identify_message(self, message: GameMessage):
        """處理 IDENTIFY 訊息"""
        hostname = message.data.get("identify", "未知主機")
        print(f"NetworkManager: 來自主機 {hostname} 的連線")
        self.recv_queue.put(f"來自主機 {hostname} 的連線")
        
    """UI"""
    def on_start_server_success(self, ip:str, port:int):
        self.start_server_btn.config(text="關閉伺服器")
        self.server_status.config(
            text=f"[伺服器狀態] 運行中 ({ip}:{port})", 
            fg="green"
        )
        # disable client buttons
        self.connect_btn.config(state="disabled")
        
    def start_server_failed(self, e):
        self.server_status.config(
            text=f"[錯誤] 伺服器啟動失敗: {str(e)}", 
            fg="red"
        )
        
    def close_server_success(self):
        self.start_server_btn.config(text="開啟伺服器")
        self.server_status.config(text="[伺服器狀態] 已關閉", fg="black")
        self.connect_btn.config(state="active")

    def close_server_failed(self, e):
        self.server_status.config(
            text=f"[錯誤] 伺服器關閉失敗: {str(e)}", 
            fg="red"
        )

    def server_connect_success(self, addr):
        self.client_status.config(
            text=f"[連線狀態] 已連接 {addr[0]}:{addr[1]}", 
            fg="green"
        )
        print(f"[連線狀態] 已連接 {addr[0]}:{addr[1]}")
        self.on_server_connect_success.emit()
    
    def server_connect_failed(self, e):
        self.client_status.config(
            text=f"[錯誤] 伺服器連接失敗: {str(e)}", 
            fg="red"
        )
        print(f"[錯誤] 伺服器連接失敗: {str(e)}")
        
    def server_disconnect_success(self):
        self.client_status.config(text="[連線狀態] 已斷線", fg="red")
        print("[連線狀態] 已斷線")
        self.start_server_btn.config(state="active")
        self.on_server_disconnect_success.emit()
    
    def server_disconnect_failed(self, e):
        self.client_status.config(
            text=f"[錯誤] 伺服器斷線失敗: {str(e)}", 
            fg="red"
        )
        print(f"[錯誤] 伺服器斷線失敗: {str(e)}")
    def client_connect_success(self, ip:str, port:int, client_ip:str, client_port:int):
        self.connect_btn.config(text="斷開連接")
        self.server_status.config(
            text=f"[伺服器狀態] 已連接到 {ip}:{port}", 
            fg="green"
        )
        self.client_status.config(text=f"[連線狀態] 已連接 {client_ip}:{client_port}", fg="green")
        self.start_server_btn.config(state="disabled")
        self.on_client_connect_success.emit()

    def client_connect_failed(self, e):
        self.client_status.config(
            text=f"[錯誤] 連接失敗: {str(e)}", 
            fg="red"
        )

    def client_disconnect_success(self):
        self.connect_btn.config(text="連接伺服器")
        self.client_status.config(text="[連線狀態] 已斷線", fg="red")
        print("客戶端斷掉了")
        self.on_client_disconnect_success.emit()

    def client_disconnect_failed(self, e):
        self.client_status.config(
            text=f"[錯誤] 客戶端斷線失敗: {str(e)}", 
            fg="red"
        )
        print(f"[錯誤] 客戶端斷線失敗: {str(e)}")

    def receive_message_failed(self, e):
        if self.is_server_running: 
            self.client_status.config(fg="red", text=f"斷開連線{str(e)}")
        else:
            self.server_status.config(fg="red", text=f"斷開連線{str(e)}")
        self.on_receive_message_failed.emit()
        
    def export_sent_messages(self, filename="sent_messages.log"):
            with open(filename, "w", encoding="utf-8") as f:
                for msg, interval in self.sent_messages:
                    f.write(f"{interval:.3f},{msg}\n")
            print(f"訊息已儲存到 {filename}")    
    
    def auto_sent_message(self, filename="sent_messages.log"):
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # 只分割第一個逗號
                interval_str, msg = line.split(",", 1)
                interval = float(interval_str)
                self.send_queue.put(msg)
                time.sleep(interval)
                print(f"自動傳送訊息: {msg}")  
                
    def auto_receive_message(self, filename="received_messages.log"):
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # 只分割第一個逗號
                interval_str, msg = line.split(",", 1)
                interval = float(interval_str)
                
                try:
                    game_message = GameMessage.from_json(msg)
                    print(f"自動化工具: 模擬收到遊戲訊息: {game_message}")
                    if game_message.type == GameMessageType.IDENTIFY:
                        self.handle_identify_message(game_message)
                    else:
                        self.recv_queue.put(game_message)
                except json.JSONDecodeError:
                    # 如果不是遊戲訊息，當作一般訊息處理
                    self.recv_queue.put(msg)
                    
                time.sleep(interval)
                print(f"自動接收訊息: {msg}")

if __name__=="__main__":
    window:Tk = Tk()
    networkManager = NetworkManager()
    networkManager.create_widget(window)
    window.mainloop()
    