from tkinter import *
from PIL import Image, ImageTk 
import random
import os


class ThreeHall:
    def __init__(self, root):
        # 創建主視窗
        self.window = root
        self.window.title('MontyHall')
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        w, h = 600, 800
        x, y = (screen_width - w) // 2, (screen_height - h) // 2
        self.window.geometry(f"{w}x{h}+{x}+{y}")
        self.window.configure(bg="BLACK")
        self.window.resizable(False, False)
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # 全域變數
        self.selected_door = IntVar()
        self.change_or_not = IntVar()
        self.car_position = None
        self.host_reveal = None

        # 設定圖片（使用絕對路徑防止錯誤）
        base_path = os.path.dirname(__file__)
        self.door_img = ImageTk.PhotoImage(Image.open(os.path.join(base_path, "ThreeHall圖片", "門.png")).resize((100, 150)))
        self.goat_img = ImageTk.PhotoImage(Image.open(os.path.join(base_path, "ThreeHall圖片", "羊.png")).resize((100, 150)))
        self.car_img  = ImageTk.PhotoImage(Image.open(os.path.join(base_path, "ThreeHall圖片", "車.png")).resize((100, 150)))

        # 設定 Frames
        self.cover_frame = Frame(self.window, bg="black")
        self.game_frame = Frame(self.window, bg="black")

        for frame in (self.cover_frame, self.game_frame):
            frame.grid(row=0, column=0, sticky="nsew")

        self.setup_cover_frame()
        self.setup_game_frame()
        self.cover_frame.tkraise()

    # 自創的grid預處理函數
    def griding(self, frame, rows, cols):
        for i in range(rows):
            frame.grid_rowconfigure(i, weight=1)
        for i in range(cols):
            frame.grid_columnconfigure(i, weight=1)

    def hide(self, widget):
        widget.config(state="disabled", bg="black", activebackground="black")

    def show(self, widget, bg="lightblue", activebackground="lightblue"):
        widget.config(state="normal", bg=bg, activebackground=activebackground)

    def start_game(self):
        self.game_frame.tkraise()
        # 元件出沒
        self.hide(self.change_checkBox)
        self.hide(self.show_btn)
        self.show(self.Game_end)
        self.show(self.choose_btn)
        self.host_label.grid_forget()
        self.choice_label.grid_forget()
        # 門可以使用
        for d in self.doors_radiobutton:
            d.config(state="normal")
        # 初始化變數
        self.car_position = random.randint(0, 2)
        self.host_reveal = None
        for d in self.doors_radiobutton:
            d.configure(image=self.door_img)

    def show_intvar(self):
        print(f"selected_door is {self.selected_door.get()}")
        print(f"change_or_not is {self.change_or_not.get()}")
        print(" ")

    def Change_or_not(self):
        # 元件出沒
        self.hide(self.choose_btn)
        self.show(self.change_checkBox)
        self.show(self.show_btn)

        # 門不可以再換了
        for d in self.doors_radiobutton:
            d.config(state="disabled")

        doors = [0, 1, 2]  # 門的號碼 

        # 主持人開門
        if self.selected_door.get() == self.car_position:
            doors.remove(self.selected_door.get())
            self.host_reveal = random.choice(doors)
        else:
            doors.remove(self.selected_door.get())
            doors.remove(self.car_position)
            self.host_reveal = doors[0]

        self.show(self.host_label, "RED", "RED")
        self.host_label.grid(row=0, column=self.host_reveal)
        self.doors_radiobutton[self.host_reveal].configure(image=self.goat_img)

        # 自己選的
        self.choice_label.grid(row=0, column=self.selected_door.get())

    def show_answer(self):
        # 元件出沒
        self.hide(self.change_checkBox)

        # 如果要換
        if self.change_or_not.get():
            doors = [0, 1, 2]
            doors.remove(self.selected_door.get())
            doors.remove(self.host_reveal)
            self.selected_door.set(doors[0])
            self.choice_label.grid_forget()
            self.choice_label.grid(row=0, column=doors[0])

        for d in self.doors_radiobutton:
            if d.cget('value') == self.car_position:
                d.configure(image=self.car_img)
            else:
                d.configure(image=self.goat_img)

        self.hide(self.show_btn)


    def end_game(self):
        self.cover_frame.tkraise()

    def setup_cover_frame(self):
        self.griding(self.cover_frame, 6, 3)
        # 開始遊戲按鈕
        self.Game_start = Button(self.cover_frame, text="開始遊戲", font=("Arial", 12), bg="lightblue",
                                 activebackground="lightblue", command=self.start_game)
        self.Game_start.grid(row=4, column=1, padx=10, pady=10, sticky="NSEW")
        
        # 回到主選單按鈕
        self.Back_to_Menu = Button(self.cover_frame, text="返回主選單", font=("Arial", 12), bg="white",
                                 activebackground="white", command=self.window.destroy) #shut down Toplevel
        self.Back_to_Menu.grid(row=5, column=1, padx=10, pady=10, sticky="NSEW")

    def setup_game_frame(self):
        self.griding(self.game_frame, 5, 3)
        self.doors_radiobutton = []
        for i in range(3):
            door = Radiobutton(self.game_frame, image=self.door_img, variable=self.selected_door, value=i, bg="black",
                               command=self.show_intvar)
            self.doors_radiobutton.append(door)
            door.grid(row=1, column=i, padx=20, pady=20)

        self.Game_end = Button(self.game_frame, text="退出遊戲", font=("Arial", 12), bg="lightblue",
                               activebackground="lightblue", command=self.end_game)
        self.Game_end.grid(row=2, column=2, padx=10, pady=10, sticky="NSEW")

        self.choose_btn = Button(self.game_frame, text="選擇", font=("Arial", 12), bg="lightblue",
                                 activebackground="lightblue", command=self.Change_or_not)
        self.choose_btn.grid(row=2, column=1, padx=10, pady=10, sticky="NSEW")

        self.change_checkBox = Checkbutton(self.game_frame, text="要換嗎", font=("Arial", 12), bg="lightblue",
                                           variable=self.change_or_not, activebackground="lightblue",
                                           command=self.show_intvar)
        self.change_checkBox.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.show_btn = Button(self.game_frame, text="揭曉", font=("Arial", 12), bg="lightblue",
                               activebackground="lightblue", command=self.show_answer)
        self.show_btn.grid(row=3, column=1, padx=10, pady=10, sticky="NSEW")

        self.host_label = Label(self.game_frame, text="主持人", font=("Arial", 12), bg="RED")
        self.choice_label = Label(self.game_frame, text="你選的", font=("Arial", 12), bg="YELLOW")

if __name__ == "__main__":
    root = Tk()
    ThreeHall(root)
    root.mainloop()
