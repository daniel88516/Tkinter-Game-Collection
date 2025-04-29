from tkinter import IntVar, StringVar, Frame
from MineSweeper_Event import MyEvent
class CountDownTimer:
    def __init__(self, container:Frame):
        self.container:Frame = container
        self.create_events()
        self.create_variable()

    def create_events(self):
        self.on_counter_change:MyEvent = MyEvent()
        self.on_count_end:MyEvent = MyEvent()
        
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
            self.on_counter_change.emit(msg)
        else:
            msg = "開始!"
            print(msg)
            self.on_counter_change.emit(msg)
            self.on_count_end.emit()
            self.reset()
            
class CountUpTimer:
    def __init__(self, container:Frame):
        self.container:Frame = container
        self.create_events()
        self.create_variable()

    def create_events(self):
        self.on_counter_change:MyEvent = MyEvent()
        
    def create_variable(self):
        self.second:int = 0
        self.countdown_var: StringVar = StringVar(value="未開始")
        self.after_id:int | None = None
        
    def reset(self):
        self.stop_countdown()
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

    def stop_countdown(self):
        if self.after_id is not None:
            self.container.after_cancel(self.after_id)
            self.after_id = None