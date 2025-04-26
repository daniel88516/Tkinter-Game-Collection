from tkinter import * 
class ChatManager:
    def __init__(self, window):
        self.window = window
        self.create_widget()
        
    def start(self):
        self.window.mainloop()
    
    def create_widget(self):
        #── 聊天記錄區（可捲動）──
        chat_input_frame = LabelFrame(self.window, text="聊天室")
        chat_input_frame.pack(padx=10, pady=10, fill="x")
        canvas = Canvas(chat_input_frame)
        scrollbar = Scrollbar(
            chat_input_frame,
            orient="vertical",
            command=canvas.yview
        )
        scrollbar.pack(side=RIGHT, fill=Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        
        frame_messages = Frame(canvas)
        canvas.create_window(
            (0, 0),
            window=frame_messages,
            anchor="nw"
        )
        canvas.pack(
            fill="both",
            expand=True
        )

        frame_messages.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        # 輸入區塊
        bottom_frame = Frame(chat_input_frame)
        bottom_frame.pack(
            side="bottom",
            fill="x",
            padx=5,
            pady=5
        )

        self.entry = Entry(bottom_frame)
        self.entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0,5)
        )

        send_btn = Button(
            bottom_frame,
            text="傳送",
            command=self.on_send
        )
        send_btn.pack(side="left")

    def add_message(self, text, from_self):
        label = Label(
            self.frame_messages,
            text=text,
            wraplength=200,
            justify="left"
        )
        if from_self:
            label.pack(
                anchor="e",
                pady=2,
                padx=10
            )
        else:
            label.pack(
                anchor="w",
                pady=2,
                padx=10
            )
        # 每次加入訊息後，滾到最底
        self.canvas.yview_moveto(1.0)

    def on_send(self):
        txt = self.entry.get().strip()
        if not txt:
            return
        self.add_message(txt, from_self=True)
        self.entry.delete(0, "end")

        # 這裡呼叫你的 network_manager.send_message(...)
        # 並在收到對方訊息時，呼叫：
        #   self.add_message(對方傳來的文字, from_self=False)

if __name__ == "__main__":
    root = Tk()
    chat = ChatManager(root)
    root.mainloop()
