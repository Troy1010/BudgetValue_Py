import TM_CommonPy as TM
import tkinter as tk
from tkinter import ttk
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
        column = 0
        # Data
        print("self.vModel.PaycheckHistory:"+TM.Narrate(self.vModel.PaycheckHistory))
        for paycheck_history_column in self.vModel.PaycheckHistory:
            self.MakeAddEntryButton((0, column))
            for row, cCategoryAmountPair in enumerate(paycheck_history_column):
                self.MakeEntry((row+1, column), text=cCategoryAmountPair[1])
            column += 1

    def OnFocusIn_MakeObvious(self, cell):
        cell.config(justify=tk.LEFT)
        cell.select_text()

    def OnFocusOut_MakeObvious(self, cell):
        cell.config(justify=tk.RIGHT)

    def CalcAndShowTotal(self):
        dBalance = self.CalculateTotal()
        self.vTotalNum.text = str(dBalance)

    def CalculateTotal(self):
        dBalance = 0
        for row in self.vModel.NetWorth:
            if row.amount is None:
                continue
            dBalance += row.amount
        return dBalance

    def MakeX(self, cRowColumnPair):
        w = tk.Button(self, text="X", font=Fonts.FONT_SMALL_BOLD, borderwidth=2, width=3, relief='ridge',
                      command=lambda self=self: self.RemoveRow(cRowColumnPair[0]))
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], sticky="ns")

    def RemoveRow(self, iRow):
        self.vModel.NetWorth.RemoveRow(iRow-1)  # skip header
        self.Refresh()

    def MakeHeader(self, cRowColumnPair, text=None):
        w = tk.Label(self, font=Fonts.FONT_SMALL_BOLD, borderwidth=2, width=15, height=1, relief='ridge',
                     background='SystemButtonFace', text=text)
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1])

    def MakeEntry(self, cRowColumnPair, text=None, columnspan=1):
        w = TM.tk.Entry(self, font=Fonts.FONT_SMALL, width=15, justify=tk.RIGHT,
                        borderwidth=2, relief='ridge', background='SystemButtonFace')
        w.text = text
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], columnspan=columnspan, sticky="ns")
        w.bind("<FocusIn>", lambda event, w=w: self.OnFocusIn_MakeObvious(w))
        w.bind("<FocusOut>", lambda event, w=w: self.OnFocusOut_MakeObvious(w), add="+")
        w.bind("<Return>", lambda event, w=w: self.FocusNextWritableCell(w))

    def MakeAddEntryButton(self, cRowColumnPair):
        w = ttk.Button(self, text="Add Entry",
                       command=lambda self=self, column=cRowColumnPair[1]: self.AddEntry(column))
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], sticky="ew")

    def AddEntry(self, column):
        self.vModel.PaycheckHistory.AddEntry(column)
        self.Refresh()

    def OnDrag(self, event):
        x, y = event.widget.winfo_pointerxy()
        target = event.widget.winfo_containing(x, y)
        if target.row != event.widget.row:
            # Grey out the From row
            for cell in self.grid_slaves(row=event.widget.row):
                cell.config(background="grey")
            # Blue out the target
            if not hasattr(self, "blueOutRow") or self.blueOutRow != target.row:
                if hasattr(self, "blueOutRow"):
                    for cell in self.grid_slaves(row=self.blueOutRow):
                        cell.config(background="SystemButtonFace")
                for cell in self.grid_slaves(row=target.row):
                    cell.config(background="lightblue")
                self.blueOutRow = target.row

    def OnDrop(self, event):
        x, y = event.widget.winfo_pointerxy()
        target = event.widget.winfo_containing(x, y)
        if target.row != event.widget.row:
            self.vModel.NetWorth[target.row-1], self.vModel.NetWorth[event.widget.row-1] = self.vModel.NetWorth[event.widget.row-1], self.vModel.NetWorth[target.row-1]
        self.Refresh()

    def SaveEntryInModel(self, cell):
        if cell.column == 0:
            self.vModel.NetWorth[cell.row-1].name = cell.text
        elif cell.column == 1:
            self.vModel.NetWorth[cell.row-1].amount = cell.text
