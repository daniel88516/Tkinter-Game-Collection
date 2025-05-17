from tkinter import *
from PIL import Image, ImageTk 
import random

# 創建主視窗
window = Tk()
window.title('GUI')
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
w, h = 600, 800
x, y = (screen_width - w) // 2, (screen_height - h) // 2
window.geometry(f"{w}x{h}+{x}+{y}")
window.configure(bg="BLACK")
window.resizable(False, False)
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

#grid函數
def griding(frame, rows, cols):
    for i in range(rows):
        frame.grid_rowconfigure(i, weight=1)
    for i in range(cols):
        frame.grid_columnconfigure(i, weight=1)

#出來又消失
def hide(widget):
    widget.config(state="disabled", bg="black", activebackground="black")  
def show(widget, bg="lightblue", activebackground="lightblue"):
    widget.config(state="normal", bg=bg, activebackground=activebackground)

#全域變數
selected_door = IntVar() #只要寫一次就好，因為radiobutton會隨時隨地更新該值
change_or_not  = IntVar() 
car_position = None
host_reveal = None 


#遊戲rundown
def start_game():
    game_frame.tkraise()
    #元件出沒
    hide(change_checkBox)
    hide(show_btn)
    show(Game_end)
    show(choose_btn)
    host_label.grid_forget()
    choice_label.grid_forget()
    #門可以使用
    for d in doors_radiobutton:
        d.config(state="normal")
    #初始化變數
    global selected_door,car_position,host_reveal,change_or_not
    car_position = random.randint(0,2)
    host_reveal = None
    for d in doors_radiobutton:
        d.configure(image = door_img)

def show_intvar():
    print(f"selected_door is +{selected_door.get()}")
    print(f"change_or_not is +{change_or_not.get()}")
    print(" ")

def Change_or_not():
    global selected_door, car_position, host_reveal, change_or_not
    #元件出沒
    hide(choose_btn)
    show(change_checkBox)
    show(show_btn)

    #門不可以再換了
    for d in doors_radiobutton:
        d.config(state="disabled")
                  
    doors = [0, 1, 2] # 門的號碼 

    #主持人開門
    if selected_door.get() == car_position:
        doors.remove(selected_door.get())  
        host_reveal = random.choice(doors)  
    else:
        doors.remove(selected_door.get())  
        doors.remove(car_position)  
        host_reveal = doors[0]  

    show(host_label,"RED" ,"RED" )
    host_label.grid(row=0, column=host_reveal)
    doors_radiobutton[host_reveal].configure(image=goat_img)  

    #自己選的
    choice_label.grid(row = 0, column = selected_door.get()  )
    print("UUUUUUUU")
    print(selected_door.get())


def show_answer():
    global selected_door,car_position,host_reveal,change_or_not
    #元件出沒
    hide(change_checkBox)

    #如果要換
    if(change_or_not.get()):
         doors = [0, 1, 2] # 門的號碼 
         doors.remove(selected_door.get())  
         doors.remove(host_reveal)  
         selected_door.set(doors[0])
         choice_label.grid_forget()
         choice_label.grid(row=0,column=doors[0])
    
    for d in doors_radiobutton:
        if d.cget('value') == car_position:
            d.configure(image = car_img)
        else:
            d.configure(image = goat_img)


def end_game():
    global selected_door,car_position,host_reveal,change_or_not
    cover_frame.tkraise()


#建立frames
cover_frame = Frame(window , bg="black")
game_frame = Frame(window , bg="black")
for frame in (cover_frame, game_frame):
    frame.grid(row=0, column=0, sticky="nsew") 

#cover_frame
griding(cover_frame, 5, 3)
Game_start = Button(cover_frame,
                    text = "開始遊戲" ,
                    font = ("Arial",12),
                    bg="lightblue",
                    activebackground="lightblue",
                    command=start_game
                    )
Game_start.grid(row=2 , column=1,padx=100 ,pady=100,sticky="NSEW")



#game_frame
griding(game_frame ,5 ,3)
door_img = ImageTk.PhotoImage(Image.open(r"C:\Users\danie\OneDrive\圖片\桌面\TK\Tk圖片\螢幕擷取畫面 2025-03-17 034637.png").resize((100, 150)))  
goat_img = ImageTk.PhotoImage(Image.open(r"C:\Users\danie\OneDrive\圖片\桌面\TK\Tk圖片\螢幕擷取畫面 2025-03-17 045154.png").resize((100, 150)))  
car_img = ImageTk.PhotoImage(Image.open(r"C:\Users\danie\OneDrive\圖片\桌面\TK\Tk圖片\螢幕擷取畫面 2025-03-17 045813.png").resize((100, 150)))  
doors_radiobutton = []
for i in range(3):
    door = Radiobutton(game_frame, image=door_img, variable=selected_door, value=i, bg="black",command=show_intvar)  
    doors_radiobutton.append(door)
    door.grid(row=1, column=i, padx=20, pady=20)


Game_end = Button(game_frame,text = "退出遊戲" ,font = ("Arial",12),bg="lightblue",activebackground="lightblue",command=end_game)
Game_end.grid(row=2 , column=2,padx=10 ,pady=10,sticky="NSEW")

choose_btn = Button(game_frame,text = "選擇" ,font = ("Arial",12),bg="lightblue",activebackground="lightblue",command=Change_or_not)
choose_btn.grid(row=2 , column=1,padx=10 ,pady=10,sticky="NSEW")

change_checkBox = Checkbutton(game_frame,text = "要換嗎" ,font = ("Arial",12), bg="lightblue",variable = change_or_not,activebackground="lightblue",command = show_intvar)
change_checkBox.grid(row=2, column=0,padx=10 ,pady=10,  sticky="nsew")

show_btn = Button(game_frame,text = "揭曉" ,font = ("Arial",12),bg="lightblue",activebackground="lightblue",command=show_answer)
show_btn.grid(row=3 , column=1,padx=10 ,pady=10,sticky="NSEW")

host_label = Label(game_frame,text = "主持人" ,font = ("Arial",12), bg="RED")
choice_label = Label(game_frame,text = "你選的" ,font = ("Arial",12), bg="YELLOW")


cover_frame.tkraise()


# 進入 Tkinter 事件迴圈
window.mainloop()
