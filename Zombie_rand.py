from tkinter import *
from tkinter import ttk
import sqlite3
import os

class RankingPage(Frame):
    def __init__(self, parent):
        super().__init__(parent)

        db_path = os.path.join(os.path.dirname(__file__), "zombie_rand.db")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        self.selected_time = IntVar(value=30)

        # --- 模式選擇區 ---
        btn_frame = Frame(self)
        btn_frame.pack(pady=20)
        Label(btn_frame, text="選擇模式：", font=("微軟正黑體", 16 ,"bold")).pack(side=LEFT, padx=10)

        for sec in [30, 60]:
            Radiobutton(btn_frame, text=f"{sec} 秒", variable=self.selected_time, value=sec,
                        command=self.refresh, font=("微軟正黑體", 16,"bold")).pack(side=LEFT, padx=10)

        # --- 排行榜區域 ---
        tree_frame = Frame(self)
        tree_frame.pack(padx=40, pady=10, expand=True, fill="both")

        scrollbar = Scrollbar(tree_frame, orient=VERTICAL)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.tree = ttk.Treeview(tree_frame, columns=("rank", "name", "score"), show="headings", height=20,
                                 yscrollcommand=scrollbar.set)

        # 樣式設定：大字體、加行高
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("微軟正黑體", 18, "bold"))
        style.configure("Treeview", font=("微軟正黑體", 16,"bold"), rowheight=40)

        self.tree.heading("rank", text="名次")
        self.tree.heading("name", text="名字")
        self.tree.heading("score", text="分數")

        self.tree.column("rank", width=100, anchor="center")
        self.tree.column("name", width=300, anchor="center")
        self.tree.column("score", width=200, anchor="center")
        self.tree.pack(side=LEFT, expand=True, fill="both")

        scrollbar.config(command=self.tree.yview)

        # 初始顯示資料
        self.refresh()

    def refresh(self):
        time_mode = self.selected_time.get()
        self.tree.delete(*self.tree.get_children())

        self.cursor.execute("""
            SELECT name, score FROM scores
            WHERE time = ?
            ORDER BY score DESC
            LIMIT 50
        """, (time_mode,))
        results = self.cursor.fetchall()

        for idx, (name, score) in enumerate(results, start=1):
            self.tree.insert("", "end", values=(idx, name, score))


# --- 執行入口（全螢幕大介面） ---
if __name__ == "__main__":
    def center_root(win, w=1080, h=900):
        win.update_idletasks()
        x = (win.winfo_screenwidth() - w) // 2
        y = (win.winfo_screenheight() - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

    root = Tk()
    root.title("Zombie 排行榜")
    center_root(root)
    root.configure(bg="white")

    page = RankingPage(root)
    page.pack(fill="both", expand=True)

    root.mainloop()