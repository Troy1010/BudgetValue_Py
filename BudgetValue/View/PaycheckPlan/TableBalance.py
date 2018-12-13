import tkinter as tk
from BudgetValue.View import Fonts


class TableBalance(tk.Frame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.vModel = vModel

        w = tk.Label(self, font=Fonts.FONT_LARGE, borderwidth=2, width=15, height=1, relief='ridge',
                     background='grey', text="Balance")
        w.grid(row=0, column=0, sticky="nw")
