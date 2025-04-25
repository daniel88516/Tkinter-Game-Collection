import socket
import threading
from MineSweeper_Event import Event

class NetworkManager:    
    def __init__(self):
        self.create_callbacks()
        self.create_variable()
        
    def create_callbacks(self):
        # server events, 開關, 連線, 斷線
        self.on_start_server_success:Event = Event()
        self.on_start_server_failed:Event = Event()
        self.on_close_server_success:Event = Event()
        self.on_close_server_failed:Event = Event()
        self.on_server_connect_success:Event = Event()
        self.on_server_connect_failed:Event = Event()
        self.on_server_disconnect_success:Event = Event()
        self.on_server_disconnect_failed:Event = Event()
        
        # client events, 連線, 斷線
        self.on_client_connect_success:Event = Event()
        self.on_client_connect_failed:Event = Event()
        self.on_client_disconnect_success:Event = Event()
        self.on_client_disconnect_failed:Event = Event()      
        
        # 接收訊息
        self.on_receive_message_success:Event = Event()
        self.on_receive_message_failed:Event = Event()
        
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
            self.on_start_server_success.emit(ip, port)
        except Exception as e:
            print(f"NetworkManager: 伺服器啟動失敗: {str(e)}")
            self.on_start_server_failed.emit(e)
            return False
    
    def stop_server(self):
        """關掉伺服器"""
        if not self.is_server_running:
            return
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.connect(('127.0.0.1', self.server_socket.getsockname()[1]))
            test_socket.close()
        except Exception as e:
            print(f"測試連接異常: {str(e)}")
        finally:
            self.is_server_running = False
            self.connection_status = False

        self._safe_close(self.client_socket)
        self._safe_close(self.server_socket)
        print("NetworkManager: 伺服器已关闭")
        self.on_close_server_success.emit()
    
    def _safe_close(self, sock: socket.socket):
        """關閉 socket"""
        if sock:
            try:
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
            except (OSError, AttributeError) as e:
                pass  # 處理 socket 已經關閉的情況
        
    def listen_clients(self):
        while self.is_server_running:
            try:
                client, addr = self.server_socket.accept()
                self.client_socket = client
                self.connection_status = True
                self.receive_thread = threading.Thread(target=self.receive_message, daemon=True)
                self.receive_thread.start()
                print(f"NetworkManager: 連上了客戶端, {addr}")   
                self.on_server_connect_success.emit(addr)
            except Exception as e:
                print("NetworkManager: 傾聽客戶端失敗" + str(e))
                self.on_server_connect_failed.emit(e)
                return False

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
            print(f"NetworkManager: 客戶端連線成功")
            self.on_client_connect_success.emit(ip, port)
            
            self.receive_thread = threading.Thread(target=self.receive_message, daemon=True)
            self.receive_thread.start()
        except Exception as e:
            print(f"NetworkManager: 客戶端連線失敗: {str(e)}")
            self.on_client_connect_failed.emit(e)

    def disconnect(self):
        try:
            self.client_socket.close()
            self.connection_status = False
            print(f"NetworkManager: 客戶端斷線成功")
            self.on_client_disconnect_success.emit()
        except Exception as e:
            print(f"NetworkManager: 客戶端斷線失敗: {str(e)}")
            self.on_client_disconnect_failed.emit(e)

    def send_message(self, message:str):
        """傳送訊息"""
        if not self.client_socket:
            print("NetworkManager: 沒有連線, 無法傳訊")
            return            
        try:
            self.client_socket.send(message.encode('utf-8'))
            print(f"NetworkManager: 傳送訊息: {message}")
        except Exception as e:
            print(f"NetworkManager: 傳送訊息失敗: {str(e)}")
            
    def receive_message(self):
        """接收訊息"""
        while(self.connection_status):
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                print(f"NetworkManager: 收到訊息: {message}")
                self.on_receive_message_success.emit(message)
            except Exception as e:
                # 遠端主機強制關閉現存的連線
                self.on_receive_message_failed.emit(e)
                print(f"NetworkManager: 接收訊息失敗: {str(e)}")
                break
        if self.is_server_running == False:
            self.stop_server()
            print("NetworkManager: 伺服器關閉")
        else:
            self.disconnect()
            print("NetworkManager: 客戶端斷線")
        
if __name__ == "__main__":
    app = NetworkManager()
    app.start()