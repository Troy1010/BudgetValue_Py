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
        #
        row = 0
        # Column Header
        for iColumn, paycheck_history_column in enumerate(self.vModel.PaycheckHistory):
            vColumnHeader = self.MakeHeader((row, iColumn+1), text="Column "+str(iColumn+1))
            vColumnHeader.bind("<Button-3>", lambda event: self.ShowHeaderMenu(event))
        iSpentColumn = len(self.vModel.PaycheckHistory)+1
        self.MakeHeader((row, iSpentColumn), text="Spent")
        self.iBudgetedColumn = len(self.vModel.PaycheckHistory)+2
        self.MakeHeader((row, self.iBudgetedColumn), text="Budgeted")
        row += 1
        # Data
        prev_type = None
        dTotalSpendableAmount = Decimal(0)
        for category in self.vModel.Categories.Select():
            bMadeEntry = False
            # make separation label if needed
            if prev_type != category.type:
                prev_type = category.type
                self.MakeSeparationLable(row, "  " + prev_type.name.capitalize())
                row += 1
            # PaycheckHistories
            for iColumn, paycheck_history_column in enumerate(self.vModel.PaycheckHistory):
                for vPaycheckHistoryEntry in paycheck_history_column:
                    if vPaycheckHistoryEntry.category.name == category.name:
                        bEditableState = True
                        if category.name == "<Default Category>":
                            bEditableState = False
                        self.MakeEntry((row, iColumn+1), text=vPaycheckHistoryEntry.amount, bEditableState=bEditableState)
                        bMadeEntry = True
            # Spent
            dSpendingHistoryTotal = self.vModel.SpendingHistory.GetTotalOfAmountsOfCategory(category)
            if dSpendingHistoryTotal:
                self.MakeEntry_ReadOnly((row, iSpentColumn), text=str(dSpendingHistoryTotal))
                bMadeEntry = True
            # Budgeted
            dSpendable = self.vModel.GetBudgetedAmount(category)
            if (dSpendable != 0 or bMadeEntry) and category.type != BV.Model.CategoryType.income:
                dTotalSpendableAmount += dSpendable
                self.MakeEntry_ReadOnly((row, self.iBudgetedColumn), text=str(dSpendable))
                bMadeEntry = True
            # Row Header
            if bMadeEntry and not self.GetCell(row, 0):
                self.MakeEntry_ReadOnly((row, 0), text=category.name, justify=tk.LEFT, bBold=True)
            #
            row += 1
        # Total
        tk.Frame(self, background='black', height=2).grid(row=row, columnspan=self.iBudgetedColumn+1, sticky="ew")
        row += 1
        vTotal = tk.Label(self, font=Fonts.FONT_LARGE, borderwidth=2, height=1,
                          relief='ridge', background='SystemButtonFace', text="Total")
        vTotal.grid(row=row, column=0, columnspan=self.iBudgetedColumn, sticky="ewn")
        self.vTotalNum = TM.tk.Entry(self, font=Fonts.FONT_SMALL, width=15,
                                     borderwidth=2, relief='ridge', justify='center', state="readonly")
        self.vTotalNum.ValidationHandler = BV.MakeValid_Money
        self.vTotalNum.grid(row=row, column=self.iBudgetedColumn, sticky="ewns")
        self.vTotalNum.text = dTotalSpendableAmount
        row += 1
        # NetWorth (to compare)
        vNetWorth = tk.Label(self, font=Fonts.FONT_LARGE, borderwidth=2, height=1,
                             relief='ridge', background='SystemButtonFace', text="Net Worth")
        vNetWorth.grid(row=row, column=0, columnspan=self.iBudgetedColumn, sticky="ewn")
        self.vNetWorthNum = TM.tk.Entry(self, font=Fonts.FONT_SMALL, width=15,
                                        borderwidth=2, relief='ridge', justify='center', state="readonly")
        self.vNetWorthNum.ValidationHandler = BV.MakeValid_Money
        self.vNetWorthNum.grid(row=row, column=self.iBudgetedColumn, sticky="ewns")
        dNetWorth = self.vModel.NetWorth.GetTotal()
        self.vNetWorthNum.text = dNetWorth
        row += 1
        # Balance
        vBalance = tk.Label(self, font=Fonts.FONT_LARGE, borderwidth=2, width=15, height=1,
                            relief='ridge', background='SystemButtonFace', text="Balance")
        vBalance.grid(row=row, column=0, columnspan=self.iBudgetedColumn, sticky="ewn")
        self.vBalanceNum = TM.tk.Entry(self, font=Fonts.FONT_SMALL, width=15,
                                       borderwidth=2, relief='ridge', justify='center', state="readonly")
        self.vBalanceNum.ValidationHandler = BV.MakeValid_Money
        self.vBalanceNum.grid(row=row, column=self.iBudgetedColumn, sticky="ewns")
        dBalance = dNetWorth - dTotalSpendableAmount
        self.vBalanceNum.text = str(dBalance)
        if dBalance != 0:
            self.vBalanceNum.config(readonlybackground="pink")
        else:
            self.vBalanceNum.config(readonlybackground="lightgreen")
        row += 1

    def RemoveColumn(self, iColumn):
        self.vModel.PaycheckHistory.RemoveColumn(iColumn)
        self.Refresh()

    def ShowHeaderMenu(self, event):
        iColumn = event.widget.grid_info()['column'] - 1
        vDropdown = tk.Menu(tearoff=False)
        vDropdown.add_command(label="Remove Column", command=lambda iColumn=iColumn: self.RemoveColumn(iColumn))
        vDropdown.post(event.x_root, event.y_root)

    def MakeHeader(self, cRowColumnPair, text=None):
        w = tk.Label(self, font=Fonts.FONT_SMALL_BOLD, borderwidth=2, width=15, height=1, relief='ridge',
                     background='SystemButtonFace', text=text)
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], sticky="ns")
        return w

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

    def SaveToModel(self, w):
        iColumn = w.column - 1
        columnName = self.GetCell(w.row, 0).text
        amount = Decimal(w.text)
        self.vModel.PaycheckHistory.SetEntryAndDirectOverflow(iColumn, columnName, amount)
        self.Refresh()

    def MakeEntry(self, cRowColumnPair, text=None, columnspan=1, bEditableState=True, justify=tk.RIGHT, bBold=False):
        if bEditableState:
            state = "normal"
            background = 'SystemButtonFace'
        else:
            state = "readonly"
            background = '#d8d8d8'
        if bBold:
            font = Fonts.FONT_SMALL_BOLD
        else:
            font = Fonts.FONT_SMALL
        w = TM.tk.Entry(self, font=font, width=15, justify=justify,
                        borderwidth=2, relief='ridge', background=background, disabledbackground=background,
                        readonlybackground=background, state=state)
        w.text = text
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], columnspan=columnspan, sticky="ns")
        w.bind('<Escape>', lambda event: self.FocusNothing())
        if bEditableState:
            w.bind("<FocusIn>", lambda event, w=w: self.OnFocusIn_MakeObvious(w))
            w.bind("<FocusOut>", lambda event, w=w: self.OnFocusOut_MakeObvious(w), add="+")
            w.bind("<FocusOut>", lambda event, w=w: self.SaveToModel(w), add="+")
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


class HeaderMenuBar(tk.Menu):
    def __init__(self, vModel, *args, **kwargs):
        tk.Menu.__init__(self, *args, **kwargs)
        self.add_command(label="Remove Column", command=self.hello)

    def hello(self):
        print("hello!")
