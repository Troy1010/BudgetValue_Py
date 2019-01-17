import TM_CommonPy as TM
import tkinter as tk
from tkinter import ttk
import BudgetValue as BV
from BudgetValue.View import Fonts
from BudgetValue.Model import CategoryType  # noqa
from decimal import Decimal


class Table(TM.tk.TableFrame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.parent = parent
        #
        self.Refresh()

    def Refresh(self):
        # remove old
        for child in BV.GetAllChildren(self):
            child.grid_forget()
            child.destroy()
        # add new
        row = 0
        # Column Header
        for iColumn, paycheck_history_column in enumerate(self.vModel.PaycheckHistory):
            self.MakeHeader((row, iColumn+1), text="Column "+str(iColumn+1))
        iSpentColumn = len(self.vModel.PaycheckHistory)+1
        self.MakeHeader((row, iSpentColumn), text="Spent")
        self.iSpendablesColumn = len(self.vModel.PaycheckHistory)+2
        self.MakeHeader((row, self.iSpendablesColumn), text="Spendables")
        row += 1
        # Data
        prev_type = None
        for category in self.vModel.Categories.Select(types_exclude=[CategoryType.extra]):
            # make separation label if needed
            if prev_type != category.type:
                prev_type = category.type
                self.MakeSeparationLable(row, "  " + prev_type.name.capitalize())
                row += 1
            # generate row
            dRowTotal = 0
            for iColumn, paycheck_history_column in enumerate(self.vModel.PaycheckHistory):
                for vPaycheckHistoryEntry in paycheck_history_column:
                    if vPaycheckHistoryEntry.category.name == category.name:
                        self.MakeEntry((row, iColumn+1), text=vPaycheckHistoryEntry.amount)
                        # Row Header
                        if not self.GetCell(row, 0):
                            self.MakeEntry_ReadOnly((row, 0), text=category.name, justify=tk.LEFT)
                        # dRowTotal
                        dRowTotal += vPaycheckHistoryEntry.amount
            #  Spent
            dSpendingHistoryTotal = self.vModel.SpendingHistory.GetTotalOfAmountsOfCategory(category.name)
            if dSpendingHistoryTotal:
                self.MakeEntry_ReadOnly((row, iSpentColumn), text=str(dSpendingHistoryTotal))
                # Row Header
                if not self.GetCell(row, 0):
                    self.MakeEntry_ReadOnly((row, 0), text=category.name, justify=tk.LEFT)
                # dRowTotal
                dRowTotal += dSpendingHistoryTotal
            #  Spendables
            if self.GetCell(row, 0) and category.type != BV.Model.CategoryType.income:
                self.MakeEntry_ReadOnly((row, self.iSpendablesColumn), text=str(dRowTotal))
            #
            row += 1
        # Total
        tk.Frame(self, background='black', height=2).grid(row=row, columnspan=self.iSpendablesColumn+1, sticky="ew")
        row += 1
        vTotal = tk.Label(self, font=Fonts.FONT_LARGE, borderwidth=2, height=1,
                          relief='ridge', background='SystemButtonFace', text="Total")
        vTotal.grid(row=row, column=0, columnspan=self.iSpendablesColumn, sticky="ewn")
        self.vTotalNum = TM.tk.Entry(self, font=Fonts.FONT_SMALL, width=15,
                                     borderwidth=2, relief='ridge', justify='center', state="readonly")
        self.vTotalNum.grid(row=row, column=self.iSpendablesColumn, sticky="ewns")
        self.row = int(row)
        self.CalcAndShowTotal()
        row += 1
        # NetWorth (to compare)
        vNetWorth = tk.Label(self, font=Fonts.FONT_LARGE, borderwidth=2, height=1,
                             relief='ridge', background='SystemButtonFace', text="Net Worth")
        vNetWorth.grid(row=row, column=0, columnspan=self.iSpendablesColumn, sticky="ewn")
        self.vNetWorthNum = TM.tk.Entry(self, font=Fonts.FONT_SMALL, width=15,
                                        borderwidth=2, relief='ridge', justify='center', state="readonly")
        self.vNetWorthNum.grid(row=row, column=self.iSpendablesColumn, sticky="ewns")
        dNetWorth = BV.View.NetWorth.Table.CalculateTotal(self)
        self.vNetWorthNum.text = str(dNetWorth)
        #self.MakeEntry((row, self.iSpendablesColumn), text=str(BV.View.NetWorth.Table.CalculateTotal(self)))
        row += 1
        # Balance
        vBalance = tk.Label(self, font=Fonts.FONT_LARGE, borderwidth=2, width=15, height=1,
                            relief='ridge', background='SystemButtonFace', text="Balance")
        vBalance.grid(row=row, column=0, columnspan=self.iSpendablesColumn, sticky="ewn")
        self.vBalanceNum = TM.tk.Entry(self, font=Fonts.FONT_SMALL, width=15,
                                       borderwidth=2, relief='ridge', justify='center', state="readonly")
        self.vBalanceNum.grid(row=row, column=self.iSpendablesColumn, sticky="ewns")
        dBalance = dNetWorth - self.CalculateTotal()
        self.vBalanceNum.text = str(dBalance)
        if dBalance != 0:
            self.vBalanceNum.config(readonlybackground="pink")
        else:
            self.vBalanceNum.config(readonlybackground="lightgreen")
        row += 1
        #

    def CalcAndShowTotal(self):
        self.vTotalNum.text = str(self.CalculateTotal())

    def CalculateTotal(self):
        dBalance = 0
        for row in range(0, self.row):
            if hasattr(self.GetCell(row, self.iSpendablesColumn), "text"):
                s = self.GetCell(row, self.iSpendablesColumn).text
                if s:
                    dBalance += Decimal(s)
        return dBalance

    def MakeHeader(self, cRowColumnPair, text=None):
        w = tk.Label(self, font=Fonts.FONT_SMALL_BOLD, borderwidth=2, width=15, height=1, relief='ridge',
                     background='SystemButtonFace', text=text)
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], sticky="ns")

    def MakeSeparationLable(self, row, text):
        w = tk.Label(self, font=Fonts.FONT_SMALL_BOLD, width=15, borderwidth=2, height=1, relief=tk.FLAT,
                     background='lightblue', text=text, anchor="w")
        w.grid(row=row, columnspan=1000, sticky="ew")  # columnspan?

    def OnFocusIn_MakeObvious(self, cell):
        cell.config(justify=tk.LEFT)
        cell.select_text()

    def OnFocusOut_MakeObvious(self, cell):
        cell.config(justify=tk.RIGHT)

    def MakeX(self, cRowColumnPair):
        w = tk.Button(self, text="X", font=Fonts.FONT_SMALL_BOLD, borderwidth=2, width=3, relief='ridge',
                      command=lambda self=self: self.RemoveRow(cRowColumnPair[0]))
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], sticky="ns")

    def RemoveRow(self, iRow):
        self.vModel.NetWorth.RemoveRow(iRow-1)  # skip header
        self.Refresh()

    def MakeEntry_ReadOnly(self, *args, **kwargs):
        kwargs["bEditableState"] = False
        self.MakeEntry(*args, **kwargs)

    def MakeEntry(self, cRowColumnPair, text=None, columnspan=1, bEditableState=True, justify=tk.RIGHT):
        if bEditableState:
            state = "normal"
        else:
            state = "readonly"
        w = TM.tk.Entry(self, font=Fonts.FONT_SMALL, width=15, justify=justify,
                        borderwidth=2, relief='ridge', background='SystemButtonFace', state=state)
        w.text = text
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], columnspan=columnspan, sticky="ns")
        w.bind('<Escape>', lambda event: self.FocusNothing())
        if bEditableState:
            w.bind("<FocusIn>", lambda event, w=w: self.OnFocusIn_MakeObvious(w))
            w.bind("<FocusOut>", lambda event, w=w: self.OnFocusOut_MakeObvious(w), add="+")
            w.bind("<Return>", lambda event, w=w: self.FocusNextWritableCell(w))

    def FocusNothing(self):
        self.winfo_toplevel().focus_set()

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
