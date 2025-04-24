import tkinter as tk
import socket
import threading
from MineSweeper_Event import Event

class NetworkManager:    
    def __init__(self):
        self.create_callbacks()
        self.create_variable()
        
    def create_callbacks(self):
        self.on_toggle_server:Event = Event() 
        self.on_start_server_failed:Event = Event()
        self.on_connect_server_success:Event = Event()
        self.on_connect_server_failed:Event = Event()
        self.on_client_disconnect:Event = Event()
        self.on_listen_client_successs:Event = Event()
        
    def create_variable(self):
        self.server_socket = None
        self.client_socket = None
        self.is_server_running = False
        self.connection_status = False

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
        success:bool = True
        if not self.is_server_running:
            success = self.start_server(ip, port) 
        else:
            self.stop_server()
            
        if success:
            self.on_toggle_server.emit(self.is_server_running)            

    def start_server(self, ip:str, port:int) -> bool:
        try:
            self.is_server_running = True
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((ip, port))
            self.server_socket.listen(5)
            # 啟動伺服器監聽線程
            server_thread = threading.Thread(target=self.listen_clients, daemon=True)
            server_thread.start()
            print("NetworkManager: 伺服器啟動成功")
            return True
        except Exception as e:
            print(f"NetworkManager: 伺服器啟動失敗: {str(e)}")
            self.on_start_server_failed.emit(e)
            return False
    
    def stop_server(self):
        self.is_server_running = False
        try:
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(
                self.server_socket.getsockname()
        )
        except:
            print("我連不上假的自己!")
        try:
            if self.client_socket:
                self.client_socket.close()
            if self.server_socket:
                self.server_socket.close()
            print("NetworkManager: 伺服器關閉")
        except Exception as e:
            print("伺服器關閉失敗" + str(e))
            pass
        
    def listen_clients(self):
        while self.is_server_running:
            try:
                client, addr = self.server_socket.accept()
                self.client_socket = client
                self.connection_status = True
                self.on_listen_client_successs.emit(addr)
            except Exception as e:
                print("傾聽客戶端失敗" + str(e))

    def toggle_connection(self, ip:str, port:int):
        if not self.connection_status:
            self.connect_to_server(ip, port)
        else:
            self.disconnect()

    def connect_to_server(self, ip:str, port:int):
        try:
            self.connection_status = True
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, port))
            self.on_connect_server_success.emit()
            print(f"NetworkManager: 客戶端連線成功")
        except Exception as e:
            print(f"NetworkManager: 客戶端連線失敗: {str(e)}")
            self.on_connect_server_failed.emit(e)

    def disconnect(self):
        try:
            self.client_socket.close()
            print(f"NetworkManager: 客戶端斷線成功")
        except Exception as e:
            print(f"NetworkManager: 客戶端斷線失敗: {str(e)}")
        
        self.connection_status = False
        self.on_client_disconnect.emit()

    def start(self):
        self.create_widgets()
        self.window.mainloop()

if __name__ == "__main__":
    app = NetworkManager()
    app.start()