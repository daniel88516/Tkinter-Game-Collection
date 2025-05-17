import random
from tkinter import *
from tkinter import messagebox  
from PIL import Image, ImageTk 



class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("圈圈叉叉")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        w, h = 600, 600
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        
        self.root.configure(bg="BLACK")  
        self.root.resizable(False, False) 

        # 遊戲變數
        self.board = [""] * 9  # 棋盤狀態
        self.player_symbol = "O"  # 玩家是 O
        self.computer_symbol = "X"  # 電腦是 X
        self.turn = "玩家"  # 當前回合
        self.game_active = False  # 遊戲是否進行中

        # 標題
        self.label = Label(root, text="請選擇先手", font=("Arial", 14), bg="BLACK", fg="WHITE")
        self.label.pack(pady=10)

        # 選擇先手
        self.first_move_frame = Frame(root, bg="BLACK")
        self.first_move_frame.pack()

        self.player_first_button = Button(self.first_move_frame, text="玩家先手",width = 12 , height = 4,bg = "lightblue" , activebackground = "lightblue", command=self.set_player_first)
        self.player_first_button.pack(side=LEFT, padx=10)

        self.computer_first_button = Button(self.first_move_frame, text="電腦先手",width = 12 , height = 4,bg = "lightcoral" , activebackground = "lightcoral", command=self.set_computer_first)
        self.computer_first_button.pack(side=LEFT, padx=10)

        # 棋盤
        self.buttons = []
        self.board_frame = Frame(root, bg="BLACK")
        self.board_frame.pack()

        for i in range(3):
            for j in range(3):
                btn = Button(self.board_frame, text="", font=("Arial", 20), width=6, height=3,
                                command=lambda idx=i * 3 + j: self.player_move(idx))
                btn.grid(row=i, column=j)
                self.buttons.append(btn)

        # 開始 + 離開
        self.start_exit_frame = Frame(root, bg="BLACK")
        self.start_exit_frame.pack()

        self.start_button = Button(self.start_exit_frame, text="開始新遊戲", width = 12 , height = 4,bg = "White" , activebackground = "White",command=self.start_game)
        self.start_button.pack(pady=10 , side=LEFT)

        self.exit_button = Button(self.start_exit_frame, text="返回主選單",width = 12 , height = 4,bg = "White" , activebackground = "White", command=self.root.destroy)
        self.exit_button.pack(pady=10 , side=LEFT)
    
    def start_game(self):
        """ 初始化遊戲 """
        self.board = [""] * 9
        self.game_active = True
        self.label.config(text=f"{self.turn}的回合")
        for btn in self.buttons:
            btn.config(text="", state=NORMAL)
        if self.turn == "電腦":
            self.computer_move()

    def set_player_first(self):
        """ 設定玩家先手 """
        self.turn = "玩家"
        self.start_game()

    def set_computer_first(self):
        """ 設定電腦先手 """
        self.turn = "電腦"
        self.start_game()

    def player_move(self, idx):
        """ 處理玩家的落子 """
        if self.board[idx] == "" and self.game_active:
            self.board[idx] = self.player_symbol
            self.buttons[idx].config(text=self.player_symbol)
            if self.check_winner(self.player_symbol):
                messagebox.showinfo("遊戲結束", "恭喜玩家獲勝！")
                self.game_active = False
                return
            self.turn = "電腦"
            self.label.config(text="電腦的回合")
            self.root.after(500, self.computer_move)  # 延遲 500ms 執行電腦回合

    def computer_move(self):
        """ 電腦 AI 決策 """
        if not self.game_active:
            return

        # 嘗試先贏
        for i in range(9):
            if self.board[i] == "":
                self.board[i] = self.computer_symbol
                if self.check_winner(self.computer_symbol):
                    self.buttons[i].config(text=self.computer_symbol)
                    messagebox.showinfo("遊戲結束", "電腦獲勝！")
                    self.game_active = False
                    return
                self.board[i] = ""

        # 嘗試阻擋玩家獲勝
        for i in range(9):
            if self.board[i] == "":
                self.board[i] = self.player_symbol
                if self.check_winner(self.player_symbol):
                    self.board[i] = self.computer_symbol
                    self.buttons[i].config(text=self.computer_symbol)
                    self.turn = "玩家"
                    self.label.config(text="玩家的回合")
                    return
                self.board[i] = ""

        # 嘗試選擇最佳位置
        best_moves = [4, 0, 2, 6, 8, 1, 3, 5, 7]  # 中間 -> 角落 -> 邊緣
        for i in best_moves:
            if self.board[i] == "":
                self.board[i] = self.computer_symbol
                self.buttons[i].config(text=self.computer_symbol)
                break

        # 檢查是否結束
        if self.check_winner(self.computer_symbol):
            messagebox.showinfo("遊戲結束", "電腦獲勝！")
            self.game_active = False
            return

        # 檢查是否平手
        if "" not in self.board:
            messagebox.showinfo("遊戲結束", "雙方平手！")
            self.game_active = False
            return

        self.turn = "玩家"
        self.label.config(text="玩家的回合")

    def check_winner(self, symbol):
        """ 判斷勝利條件 """
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # 橫排
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # 直排
            [0, 4, 8], [2, 4, 6]              # 斜線
        ]
        for condition in win_conditions:
            if all(self.board[i] == symbol for i in condition):
                return True
        return False

# main
if __name__ == "__main__":
    root = Tk()
    app = TicTacToe(root)
    root.mainloop()
