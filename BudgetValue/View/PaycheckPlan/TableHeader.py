import tkinter as tk
from BudgetValue.View import Fonts


class TableHeader(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.header_list = ['Category', 'Amount', 'Period', 'Plan']

        for j, vItem in enumerate(self.header_list):
            w = tk.Text(self, font=Fonts.FONT_SMALL_BOLD, borderwidth=2, width=15, height=1, relief='ridge', background='SystemButtonFace')
            w.insert(1.0, str(vItem))
            w.grid(row=0, column=j)
            w.configure(state="disabled")
