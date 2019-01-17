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
            self.MakeX((row, 2))
            row += 1
        # Total
        tk.Frame(self, background='black', height=2).grid(row=row, columnspan=4, sticky="ew")
        row += 1
        vTotal = tk.Label(self, font=Fonts.FONT_LARGE, borderwidth=2, height=1,
                          relief='ridge', background='SystemButtonFace', text="Total")
        vTotal.grid(row=row, column=0, columnspan=1, sticky="ewn")
        self.vTotalNum = TM.tk.Entry(self, font=Fonts.FONT_SMALL, width=15,
                                     borderwidth=2, relief='ridge', justify='center', state="readonly")
        self.vTotalNum.grid(row=row, column=1, sticky="ewns")
        row += 1
        #
        self.CalcAndShowTotal()

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
        w.bind("<FocusOut>", lambda event, w=w: self.SaveEntryInModel(w), add="+")
        w.bind("<FocusOut>", lambda event, w=w: self.OnFocusOut_MakeObvious(w), add="+")
        w.bind("<FocusOut>", lambda event: self.CalcAndShowTotal(), add="+")
        w.bind("<Return>", lambda event, w=w: self.FocusNextWritableCell(w))
        w.bind("<B1-Motion>", self.OnDrag)
        w.bind("<ButtonRelease-1>", self.OnDrop)

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
