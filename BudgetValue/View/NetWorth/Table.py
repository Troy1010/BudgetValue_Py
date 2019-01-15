import TM_CommonPy as TM
import tkinter as tk
import BudgetValue as BV
from BudgetValue.View import Fonts


class Table(TM.tk.TableFrame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.parent = parent

    def Refresh(self):
        # remove old
        for child in BV.GetAllChildren(self):
            child.grid_forget()
            child.destroy()
        # add new
        row = 0
        # Header
        for j, header_name in enumerate(['Account', 'Amount']):
            self.MakeHeader((row, j), text=header_name)
        row += 1
        # Data
        for net_worth_row in self.vModel.NetWorth:
            assert isinstance(net_worth_row, BV.Model.NetWorthRow)
            self.MakeEntry((row, 0), text=net_worth_row.name)
            self.MakeEntry((row, 1), text=net_worth_row.amount)
            row += 1

    def MakeHeader(self, cRowColumnPair, text=None):
        w = tk.Label(self, font=Fonts.FONT_SMALL_BOLD, borderwidth=2, width=15, height=1, relief='ridge',
                     background='SystemButtonFace', text=text)
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1])

    def MakeEntry(self, cRowColumnPair, text=None, columnspan=1):
        w = TM.tk.Entry(self, font=Fonts.FONT_SMALL, width=15, justify=tk.RIGHT,
                        borderwidth=2, relief='ridge', background='SystemButtonFace')
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], columnspan=columnspan)
        # w.bind("<FocusIn>", lambda event, w=w: self.Entry_FocusIn(w))
        # w.bind("<FocusOut>", lambda event, w=w: self.Entry_FocusOut(w))
        # w.bind("<Return>", lambda event, w=w: self.Entry_Return(w))
        w.text = text
