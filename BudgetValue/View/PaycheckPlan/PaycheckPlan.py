from BudgetValue._Logger import BVLog  # noqa
import tkinter as tk
from BudgetValue.View import Fonts


class PaycheckPlan(tk.Frame):
    name = "Paycheck Plan"

    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)

        for i, vCategory in enumerate(vModel.Categories.GetTrueCategories()):
            self.MakeText((i, 0), str(vCategory.name))
            self.MakeEntry((i, 1))

    def MakeText(self, cRowColumnPair, text):
        w = tk.Text(self, font=Fonts.FONT_SMALL, width=15,
                    borderwidth=2, height=1, relief='ridge', background='SystemButtonFace')
        w.insert(1.0, text)
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1])
        w.configure(state="disabled")

    def MakeEntry(self, cRowColumnPair):
        w = tk.Entry(self, font=Fonts.FONT_SMALL, width=15, justify=tk.RIGHT,
                     borderwidth=2, relief='ridge', background='SystemButtonFace')
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1])
        w.bind("<FocusIn>", lambda event, w=w: self.Entry_FocusIn(event, w))
        w.bind("<FocusOut>", lambda event, w=w: self.Entry_FocusOut(event, w))

    def Entry_FocusIn(self, event, w):
        w.config(justify=tk.LEFT)

    def Entry_FocusOut(self, event, w):
        w.config(justify=tk.RIGHT)
