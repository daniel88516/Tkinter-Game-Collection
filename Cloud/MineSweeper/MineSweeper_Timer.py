from tkinter import IntVar, StringVar, Frame, PhotoImage
from MineSweeper_Event import MyEvent
import os, time

class CountDownTimer:
    def __init__(self, container: Frame):
        self.container: Frame = container
        self.create_events()
        self.create_variable()

    def create_events(self):
        self.event_counter_change: MyEvent = MyEvent()
        self.event_count_end: MyEvent = MyEvent()

    def create_variable(self):
        self.start_time: float | None = None
        self.remaining_time: int = 3
        self.running: bool = False
        self.countdown_var: IntVar = IntVar(value=self.remaining_time)
        self.after_id: int | None = None

    def reset(self):
        self.stop_countdown()
        self.start_time = None
        self.remaining_time = 3
        self.countdown_var.set(self.remaining_time)
        self.after_id = None

    def start_countdown(self):
        if not self.running:
            self.running = True
            self.start_time = time.perf_counter()
            self._update_countdown()

    def _update_countdown(self):
        if not self.running:
            return
        now = time.perf_counter()
        elapsed = int(now - self.start_time)
        current_time = max(self.remaining_time - elapsed, 0)
        self.countdown_var.set(current_time)

        if current_time > 0:
            msg = f"遊戲即將開始...倒數{current_time}秒"
            print(msg)
            self.event_counter_change.emit(msg)
            self.after_id = self.container.after(1000, self._update_countdown)  # 每 100ms 更新
        else:
            msg = "開始!"
            print(msg)
            self.event_counter_change.emit(msg)
            self.event_count_end.emit()
            self.reset()

    def stop_countdown(self):
        if self.running:
            self.running = False
            if self.after_id is not None:
                self.container.after_cancel(self.after_id)
                self.after_id = None
class CountUpTimer:
    def __init__(self, container: Frame):
        self.container: Frame = container
        self.create_events()
        self.create_variable()

    def create_events(self):
        self.on_counter_change: MyEvent = MyEvent()

    def create_variable(self):
        self.start_time: float | None = None
        self.elapsed: int = 0
        self.running: bool = False
        self.countdown_var: StringVar = StringVar(value="未開始")
        self.after_id: int | None = None

    def reset(self):
        self.stop_countup()
        self.start_time = None
        self.elapsed = 0
        self.countdown_var.set("未開始")
        self.after_id = None

    def start_countup(self):
        if not self.running:
            self.running = True
            self.start_time = time.perf_counter() - self.elapsed
            self._update_countup()

    def _update_countup(self):
        if not self.running:
            return
        now = time.perf_counter()
        self.elapsed = int(now - self.start_time)
        minutes = self.elapsed // 60
        seconds = self.elapsed % 60
        self.countdown_var.set(f"{minutes:02d}:{seconds:02d}")
        self.on_counter_change.emit()
        self.after_id = self.container.after(100, self._update_countup)  # 每 100ms 更新

    def stop_countup(self):
        if self.running:
            self.running = False
            if self.after_id is not None:
                self.container.after_cancel(self.after_id)
                self.after_id = None             
class HighPrecisionCountUpTimer:
    def __init__(self, container: Frame):
        self.container: Frame = container
        self.create_events()
        self.create_variable()

    def create_events(self):
        self.on_counter_change: MyEvent = MyEvent()

    def create_variable(self):
        self.start_time: float | None = None
        self.elapsed: float = 0.0
        self.running: bool = False
        self.countdown_var: StringVar = StringVar(value="未開始")
        self.after_id: int | None = None

    def reset(self):
        self.stop_countup()
        self.start_time = None
        self.elapsed = 0.0
        self.countdown_var.set("未開始")
        self.after_id = None

    def start_countup(self):
        if not self.running:
            self.running = True
            self.start_time = time.perf_counter() - self.elapsed  # 設定開始時間
            self._update_high_precision()

    def _update_high_precision(self):
        if not self.running:
            return
        now = time.perf_counter()
        self.elapsed = now - self.start_time  # 計算實際經過的時間
        minutes = int(self.elapsed // 60)
        seconds = int(self.elapsed % 60)
        millis = int((self.elapsed - int(self.elapsed)) * 1000)
        self.countdown_var.set(f"{minutes:02d}:{seconds:02d}.{millis:03d}")
        self.on_counter_change.emit()
        self.after_id = self.container.after(10, self._update_high_precision)  # 每 10ms 更新一次

    def stop_countup(self):
        if self.running:
            self.running = False
            if self.after_id is not None:
                self.container.after_cancel(self.after_id)
                self.after_id = None