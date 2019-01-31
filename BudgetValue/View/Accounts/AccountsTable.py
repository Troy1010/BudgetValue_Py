import TM_CommonPy as TM
import tkinter as tk
import BudgetValue as BV
from BudgetValue.View import WidgetFactories as WF


class AccountsTable(TM.tk.TableFrame):
    def __init__(self, parent, vModel):
        assert isinstance(vModel, BV.Model.Model)
        tk.Frame.__init__(self, parent)
        self.vModel = vModel
        self.parent = parent

    def Refresh(self):
        # remove old
        for child in BV.GetAllChildren(self):
            child.grid_forget()
            child.destroy()
        if hasattr(self, 'cDisposables'):
            for disposable in self.cDisposables:
                disposable.dispose()
        self.cDisposables = []
        # add new
        row = 0
        # Header
        WF.MakeHeader(self, (row, 0), text='Account')
        WF.MakeHeader(self, (row, 1), text='Amount')
        row += 1
        # Data
        for net_worth_row in self.vModel.Accounts:
            assert isinstance(net_worth_row, BV.Model.AccountsRow)
            self.MakeEntry((row, 0), text=net_worth_row.name)
            w = self.MakeEntry((row, 1), text=net_worth_row.amount_stream)
            w.ValidationHandler = BV.MakeValid_Money_ZeroIsNone
            WF.MakeX(self, (row, 2), command=lambda row=row: self.RemoveRow(row))
            row += 1
        # Black bar
        tk.Frame(self, background='black', height=2).grid(row=row, columnspan=4, sticky="ew")
        row += 1
        # Accounts Total
        WF.MakeLable(self, (row, 0), text="Accounts Total", width=WF.Buffer(1))
        WF.MakeEntry_ReadOnly(self, (row, 1), text=self.vModel.Accounts.total_stream, justify=tk.CENTER)
        row += 1

    def RemoveRow(self, iRow):
        self.vModel.Accounts.RemoveRow(iRow-1)  # skip header
        self.Refresh()

    def MakeEntry(self, cRowColumnPair, text=None):
        w = WF.MakeEntry(self, cRowColumnPair, text=text)
        w.bind("<FocusOut>", lambda event, w=w: self.SaveEntryInModel(w), add="+")
        w.bind("<B1-Motion>", self.OnDrag, add="+")
        w.bind("<ButtonRelease-1>", self.OnDrop, add="+")
        return w

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
            self.vModel.Accounts[target.row-1], self.vModel.Accounts[event.widget.row-1] = self.vModel.Accounts[event.widget.row-1], self.vModel.Accounts[target.row-1]
            self.Refresh()

    def SaveEntryInModel(self, cell):
        if cell.column == 0:
            self.vModel.Accounts[cell.row-1].name = cell.text
        elif cell.column == 1:
            self.vModel.Accounts[cell.row-1].amount = cell.text
