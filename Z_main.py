from tkinter import *
from tkinter.ttk import Notebook
from Zombie_rand import RankingPage
from CanvasZombie import CanvasZombie

class ZMain(Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root

        # 先設定希望縮小後的置中座標
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        w, h = 1300,900  # 妳希望視窗還原時的大小
        x = (screen_width - w) // 2
        y = (screen_height - h) // 2

        # 先設定 geometry，但等會被 zoomed 蓋掉沒關係
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # 再設定最大化
        self.root.state("zoomed")

        self.pack(fill="both", expand=True)

        # 建立 Notebook 分頁容器
        self.notebook = Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        # Zombie 遊戲頁面
        self.zombie_page = CanvasZombie(self.notebook)
        self.zombie_page.pack(fill="both", expand=True)
        self.notebook.add(self.zombie_page, text="🧟 CanvasZombie")

        # 排行榜頁面
        self.ranking_page = RankingPage(self.notebook)
        self.ranking_page.pack(fill="both", expand=True)
        self.notebook.add(self.ranking_page, text="🏆 排行榜")
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        
    def on_tab_changed(self, event):
        current_tab = event.widget.select()
        selected_widget = event.widget.nametowidget(current_tab)

        if isinstance(selected_widget, CanvasZombie):
            selected_widget.focus_set()
            if self.notebook.index(current_tab) == 0:  
                selected_widget.update_idletasks()     
                selected_widget.canvas.update()       


# main
if __name__ == "__main__":
    root = Tk()
    app = ZMain(root) 
    app.pack(fill="both", expand=True)
    root.mainloop()