import os 
from tkinter import *
from PIL import Image, ImageTk
from MineSweeper_Event import MyEvent
import random

class ChatManager:
    def __init__(self):
        self.create_variable()
        self.create_events()

    def create_variable(self):
        self.entry_var:StringVar = StringVar()
        
        self.after_id = None
        self.is_image_cooling_down = False

        base_path = os.path.dirname(os.path.abspath(__file__))
        self.sticker_map = {
            "happy": os.path.join(base_path, "Images", "Stickers", "happy.png"),
            "shock": os.path.join(base_path, "Images", "Stickers", "shock.png"),
            "cry": os.path.join(base_path, "Images", "Stickers", "cry.png"),
            "doubt": os.path.join(base_path, "Images", "Stickers", "doubt.png"),
        }
        
        self.final_message: list[str] = [
            "試圖在地雷中優雅地跳芭蕾", 
            "被逐出了人界",
            "想證明地雷很安全，他失敗了",
            "被地雷排除了",
            "被炸得血肉模糊",
            "忘了金屬探測器怎麼用", 
            "被絆倒了",
        ]

    def create_events(self):
        self.on_send_message:MyEvent = MyEvent()
        self.on_send_image:MyEvent = MyEvent()
        
    def create_widget(self, parent_frame: Frame):
        self.parent_frame = parent_frame

        # 聊天區整體容器
        chat_input_frame = LabelFrame(self.parent_frame, text="聊天室")
        chat_input_frame.pack(
            padx=10,
            pady=10,
            fill="both",
            expand=True
        )

        # 用一個中間 frame 承載 Canvas 和 Scrollbar
        display_frame = Frame(chat_input_frame)
        display_frame.pack(
            fill="both",
            expand=True
        )

        # Canvas + Scrollbar
        self.canvas = Canvas(display_frame, width=200, height=200)
        scrollbar = Scrollbar(
            display_frame,
            orient=VERTICAL,
            command=self.canvas.yview
        )
        scrollbar.pack(
            side=RIGHT,
            fill=Y
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # 訊息承載 frame
        self.messages_frame = Frame(self.canvas)
        self._messages_window = self.canvas.create_window(
            (0, 0),
            window=self.messages_frame,
            anchor="nw"
        )

        self.canvas.pack(
            side=LEFT,
            fill="both",
            expand=True
        )

        # 更新 scrollregion
        self.messages_frame.bind(
            "<Configure>",
            lambda e:
            self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        # 同步寬度
        self.canvas.bind(
            "<Configure>",
            lambda e:
            self.canvas.itemconfig(
                self._messages_window,
                width=e.width
            )
        )

        # 滑鼠滾輪
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda e:
            self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        )
        self.canvas.bind_all(
            "<Button-4>",
            lambda e: self.canvas.yview_scroll(-1, "units")
        )
        self.canvas.bind_all(
            "<Button-5>",
            lambda e: self.canvas.yview_scroll(1, "units")
        )

        # # 輸入區塊，放在 display_frame 之下
        # bottom_frame = Frame(chat_input_frame)
        # bottom_frame.pack(
        #     side="bottom",
        #     fill="x",
        #     padx=5,
        #     pady=5
        # )

        # self.entry = Entry(bottom_frame, textvariable=self.entry_var)
        # self.entry.pack(
        #     side="left",
        #     fill="x",
        #     expand=True,
        #     padx=(0, 5)
        # )

        # self.send_btn = Button(
        #     bottom_frame,
        #     text="傳送",
        #     command=self.send_message,
        #     state=ACTIVE
        # )
        # self.send_btn.pack(
        #     side="left"
        # )

        # 新增圖片按鈕區域
        image_button_frame = Frame(chat_input_frame)
        image_button_frame.pack(
            side="bottom",
            fill="x",
            padx=5,
            pady=5
        )

        # 載入圖片並新增按鈕
        self.sticker_btns = []
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.image_paths = [
            os.path.join(base_path, "Images", "Stickers", "happy.png"),
            os.path.join(base_path, "Images", "Stickers", "shock.png"),
            os.path.join(base_path, "Images", "Stickers", "cry.png"),
            os.path.join(base_path, "Images", "Stickers", "doubt.png"),
        ]
        
        for name, path in self.sticker_map.items():
            try:
                img = Image.open(path)
                img = img.resize((80, 80), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)

                btn = Button(
                    image_button_frame,
                    image=photo,
                    command=lambda name=name: self.send_image(name)
                )
                btn.image = photo
                btn.pack(side="left", padx=5)
                btn.config(state=DISABLED)
                self.sticker_btns.append(btn)
            except Exception as e:
                print(f"無法載入圖片 {path}: {e}")
    
    def send_image(self, sticker_name):
        self.add_message(sticker_name, from_self=True, is_image=True)
        self.on_send_image.emit(sticker_name)
        self.start_image_cooldown()

    def add_message(self, content, from_self, is_image=False):
        """新增訊息，支援文字和圖片"""
        # 一定要讓 message_frame 填滿寬度
        message_frame = Frame(self.messages_frame)
        message_frame.pack(
            side="top",
            fill="x",  # 撐滿整行
            pady=2
        )
        if is_image:
            try:
                image_path = self.sticker_map[content]
                img = Image.open(image_path)
                img.thumbnail((200, 200))
                photo = ImageTk.PhotoImage(img)
                label = Label(
                    message_frame,
                    image=photo,
                    padx=10,
                    pady=5,
                )
                label.image = photo
            except Exception as e:
                label = Label(
                    message_frame,
                    text=f"圖片載入失敗: {e}",
                    wraplength=200,
                    justify=LEFT,
                    bg="#FFCCCC",
                    padx=10,
                    pady=5,
                    relief="solid",
                    borderwidth=1
                )
        else: # 文字
            label = Label(
                message_frame,
                text=content,
                wraplength=200,
                justify=LEFT,
                bg="#95EC69" if from_self else "#DDDDDD",
                padx=10,
                pady=5,
                relief="solid",
                borderwidth=1
            )

        # 依 from_self 決定 side
        label.pack(
            side=RIGHT if from_self else LEFT,
            padx=10
        )
        # 新增完訊息就滑到底
        self.canvas.after(100, lambda: self.canvas.yview_moveto(1.0))

    def send_message(self):
        msg = self.entry.get().strip()
        if not msg:
            return
        # 傳送文字訊息
        self.add_message(msg, from_self=True)  
        self.entry.delete(0, "end")
        self.on_send_message.emit(msg)

    def reset(self):
        # 清除 messages_frame 中的所有子元件
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        # 重置 Canvas 的 scrollregion
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        if self.after_id: 
            self.parent_frame.after_cancel(self.after_id)
    
    def config_buttons(self, state):
        for btn in self.sticker_btns:
            btn.config(state=state)
    
    def start_image_cooldown(self):
        self.is_image_cooling_down = True
        self.config_buttons(state=DISABLED)
        self.after_id = self.parent_frame.after(2000, self.end_image_cooldown)
    
    def end_image_cooldown(self):
        self.is_image_cooling_down = False
        self.config_buttons(state=ACTIVE)
        self.after_id = None
    
    def get_random_final_message(self) -> str:
        """隨機選擇一個訊息傳送"""
        return random.choice(self.final_message)
        
if __name__=="__main__":
    window:Tk = Tk()
    chat_manager = ChatManager()
    chat_manager.create_widget(window)
    chat_manager.config_buttons(state=ACTIVE)
    # chat_manager.send_btn.config(state=ACTIVE)
    window.mainloop()
