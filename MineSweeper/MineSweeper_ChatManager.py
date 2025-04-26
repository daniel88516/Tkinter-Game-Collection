from tkinter import *
from MineSweeper_Event import MyEvent

class ChatManager:
    def __init__(self):
        self.create_variable()
        self.create_events()

    def create_variable(self):
        self.entry_var:StringVar = StringVar(value="A")

    def create_events(self):
        self.on_send_message:MyEvent = MyEvent()

    def create_widget(self, parent_frame:Frame):
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
        self.canvas = Canvas(display_frame, width=130, height=130)
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

        # 輸入區塊，放在 display_frame 之下
        bottom_frame = Frame(chat_input_frame)
        bottom_frame.pack(
            side="bottom",
            fill="x",
            padx=5,
            pady=5
        )

        self.entry = Entry(bottom_frame, textvariable=self.entry_var)
        self.entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0,5)
        )

        send_btn = Button(
            bottom_frame,
            text="傳送",
            command=self.send_message
        )
        send_btn.pack(
            side="left"
        )

    def add_message(self, text, from_self):
        # 一定要讓 message_frame 填滿寬度
        message_frame = Frame(self.messages_frame)
        message_frame.pack(
            side="top",
            fill="x",      # 撐滿整行
            pady=2
        )

        label = Label(
            message_frame,
            text=text,
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
            side=LEFT if from_self else RIGHT,
            padx=10
        )
        # 新增完訊息就滑到底
        self.canvas.after(100, lambda:self.canvas.yview_moveto(1.0))

    def send_message(self):
        msg = self.entry.get().strip()
        if not msg:
            return
        self.add_message(msg, from_self=True)
        self.entry.delete(0, "end")
        self.on_send_message.emit(msg)

if __name__=="__main__":
    window:Tk = Tk()
    chat_manager = ChatManager()
    chat_manager.create_widget(window)
    window.mainloop()
