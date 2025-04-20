from tkinter import *
from tkinter.ttk import Notebook
from Zombie import Zombie
from Zombie_rand import RankingPage

class ZMain(Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root

        # 設定視窗大小與置中
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        w, h = 700, 800
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.configure(bg="white")
        self.root.title("ShotZombie")

        self.pack(fill="both", expand=True)

        # 建立 Notebook 分頁容器
        self.notebook = Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        # Zombie 遊戲頁面
        self.zombie_page = Zombie(self.notebook)
        self.zombie_page.pack(fill="both", expand=True)
        self.notebook.add(self.zombie_page, text="🧟 Zombie")

        # 排行榜頁面
        self.ranking_page = RankingPage(self.notebook)
        self.ranking_page.pack(fill="both", expand=True)
        self.notebook.add(self.ranking_page, text="🏆 排行榜")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
    def on_tab_changed(self, event):
        current_tab = event.widget.select()
        selected_widget = event.widget.nametowidget(current_tab)
        if isinstance(selected_widget, Zombie):
            selected_widget.focus_set()

# main
if __name__ == "__main__":
    root = Tk()
    app = ZMain(root) 
    app.pack(fill="both", expand=True)
    root.mainloop()