from tkinter import IntVar, StringVar, Frame, PhotoImage
from MineSweeper_Event import MyEvent
import os 

class CountDownTimer:
    def __init__(self, container:Frame):
        self.container:Frame = container
        self.create_events()
        self.create_variable()
    
    def create_events(self):
        self.event_counter_change:MyEvent = MyEvent()
        self.event_count_end:MyEvent = MyEvent()
        
    def create_variable(self):
        self.countdown_var:IntVar = IntVar(value=3)
        self.after_id:int | None = None
        
    def reset(self):
        self.game_started = False
        self.countdown_var.set(3)
        if self.after_id is not None:
            self.container.after_cancel(self.after_id)
            self.after_id = None
            
    def start_countdown(self):
        if self.after_id is None:
            self.update_countdown()

    def update_countdown(self):
        current_time:int = self.countdown_var.get()
        if current_time > 0:
            msg = f"遊戲即將開始...倒數{current_time}秒"
            print(msg)
            current_time = current_time - 1
            self.countdown_var.set(current_time)
            self.after_id = self.container.after(1000, self.update_countdown)
            self.event_counter_change.emit(msg)
        else:
            msg = "開始!"
            print(msg)
            self.event_counter_change.emit(msg)
            self.event_count_end.emit()
            self.reset()
            
class CountUpTimer:
    def __init__(self, container:Frame):
        self.container:Frame = container
        self.load_images()
        self.create_events()
        self.create_variable()

    def load_images(self): 
        """加載圖片"""
        base_path = os.path.join(os.path.dirname(__file__), f"Images/Segment/")
        self.tile_images = {}
        self.tile_images["0"]    = PhotoImage(file=os.path.join(base_path, "0.png"))
        self.tile_images["1"]    = PhotoImage(file=os.path.join(base_path, "1.png"))
        self.tile_images["2"]    = PhotoImage(file=os.path.join(base_path, "2.png"))
        self.tile_images["3"]    = PhotoImage(file=os.path.join(base_path, "3.png"))
        self.tile_images["4"]    = PhotoImage(file=os.path.join(base_path, "4.png"))
        self.tile_images["5"]    = PhotoImage(file=os.path.join(base_path, "5.png"))
        self.tile_images["6"]    = PhotoImage(file=os.path.join(base_path, "6.png"))
        self.tile_images["7"]    = PhotoImage(file=os.path.join(base_path, "7.png"))
        self.tile_images["8"]    = PhotoImage(file=os.path.join(base_path, "8.png"))
        self.tile_images["9"]    = PhotoImage(file=os.path.join(base_path, "9.png"))
        
    def create_events(self):
        self.on_counter_change:MyEvent = MyEvent()
        
    def create_variable(self):
        self.second:int = 0
        self.countdown_var: StringVar = StringVar(value="未開始")
        self.after_id:int | None = None
        
    def reset(self):
        self.stop_countup()
        self.second = 0
        self.countdown_var.set("未開始")
        self.after_id = None
                
    def start_countdown(self):
        if self.after_id is None:
            self.update_countdown()

    def update_countdown(self):
        self.second = self.second + 1
        minutes = self.second // 60
        seconds = self.second % 60
        self.countdown_var.set(f"{minutes:02d}:{seconds:02d}")
        self.on_counter_change.emit()
        self.after_id = self.container.after(1000, self.update_countdown)

    def stop_countup(self):
        if self.after_id is not None:
            self.container.after_cancel(self.after_id)
            self.after_id = None
            
    def get_timer_image(self) -> list[PhotoImage]: 
        return [self.tile_images["0"], self.tile_images["1"], self.tile_images["2"], self.tile_images["3"]]
    
    