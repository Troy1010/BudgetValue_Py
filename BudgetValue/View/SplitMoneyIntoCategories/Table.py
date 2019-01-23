import TM_CommonPy as TM
import tkinter as tk
import BudgetValue as BV
from BudgetValue.View import Fonts
from decimal import Decimal
from BudgetValue.View import WidgetFactories as WF


class Table(TM.tk.TableFrame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.parent = parent
        #
        self.vModel.SpendingHistory.ObserveUpdatedCategory.subscribe(lambda category: self.Refresh())
        #
        self.dBalance = Decimal(0)
        #
        self.vNetWorthTotal = 0
        self.vModel.NetWorth.total_Observable.subscribe(lambda sum_: self.AssignTotal(sum_))

    def AssignTotal(self, sum_):
        self.vNetWorthTotal = sum_
        if hasattr(self, "vNetWorthNum"):
            self.vNetWorthNum.text = sum_

    def Refresh(self):
        # remove old
        for child in BV.GetAllChildren(self):
            child.grid_forget()
            child.destroy()
        #
        row = 0
        # Column Header
        WF.MakeHeader(self, (row, 0), text="Category")
        for iColumn, split_money_history_column in enumerate(self.vModel.SplitMoneyHistory):
            vColumnHeader = WF.MakeHeader(self, (row, iColumn+1), text="Column "+str(iColumn+1))
            vColumnHeader.bind("<Button-3>", lambda event: self.ShowHeaderMenu(event))
        self.iSpentColumn = len(self.vModel.SplitMoneyHistory)+1
        WF.MakeHeader(self, (row, self.iSpentColumn), text="Spent")
        self.iBudgetedColumn = len(self.vModel.SplitMoneyHistory)+2
        WF.MakeHeader(self, (row, self.iBudgetedColumn), text="Budgeted")
        row += 1
        # Data
        prev_type = None
        dTotalSpendableAmount = Decimal(0)
        self.cActiveCategories = list()
        for category in self.vModel.Categories.Select():
            bMadeEntry = False
            # make separation label if needed
            if prev_type != category.type:
                prev_type = category.type
                WF.MakeSeparationLable(self, row, "  " + prev_type.name.capitalize())
                row += 1
            # SplitMoneyHistory
            for iColumn, split_money_history_column in enumerate(self.vModel.SplitMoneyHistory):
                if category.name in split_money_history_column:
                    bEditableState = True
                    if category.name == "<Default Category>":
                        bEditableState = False
                    w = WF.MakeEntry(self, (row, iColumn+1), text=split_money_history_column[category.name].amount, bEditableState=bEditableState)
                    w.bind("<FocusOut>", lambda event, w=w: self.SaveCellToModel(w), add="+")
                    w.bind("<Button-3>", lambda event: self.ShowCellMenu(event), add="+")
                    w.bind("<FocusOut>", lambda event: self.Refresh(), add="+")
                    bMadeEntry = True
            # Spent
            dSpendingHistoryTotal = self.vModel.SpendingHistory.GetTotalOfAmountsOfCategory(category)
            if dSpendingHistoryTotal:
                WF.MakeEntry_ReadOnly(self, (row, self.iSpentColumn), text=str(dSpendingHistoryTotal))
                bMadeEntry = True
            # Budgeted
            dSpendable = self.vModel.GetBudgetedAmount(category)
            if (dSpendable != 0 or bMadeEntry) and category.type != BV.Model.CategoryType.income:
                dTotalSpendableAmount += dSpendable
                WF.MakeEntry_ReadOnly(self, (row, self.iBudgetedColumn), text=str(dSpendable))
                bMadeEntry = True
            # Row Header
            if bMadeEntry and not self.GetCell(row, 0):
                WF.MakeEntry_ReadOnly(self, (row, 0), text=category.name, justify=tk.LEFT, bBold=True)
                self.cActiveCategories.append(category)
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
        self.vNetWorthNum.text = self.vNetWorthTotal
        row += 1
        # Balance
        vBalance = tk.Label(self, font=Fonts.FONT_LARGE, borderwidth=2, width=15, height=1,
                            relief='ridge', background='SystemButtonFace', text="Balance")
        vBalance.grid(row=row, column=0, columnspan=self.iBudgetedColumn, sticky="ewn")
        self.vBalanceNum = TM.tk.Entry(self, font=Fonts.FONT_SMALL, width=15,
                                       borderwidth=2, relief='ridge', justify='center', state="readonly")
        self.vBalanceNum.ValidationHandler = BV.MakeValid_Money
        self.vBalanceNum.grid(row=row, column=self.iBudgetedColumn, sticky="ewns")
        self.dBalance = self.vNetWorthTotal - dTotalSpendableAmount
        self.vBalanceNum.text = self.dBalance
        if self.dBalance != 0:
            self.vBalanceNum.config(readonlybackground="pink")
        else:
            self.vBalanceNum.config(readonlybackground="lightgreen")
        row += 1

    def ShowCellMenu(self, event):
        vDropdown = tk.Menu(tearoff=False)
        vDropdown.add_command(label="Remove Entry", command=lambda cell=event.widget: self.RemoveCell(cell))
        vDropdown.post(event.x_root, event.y_root)

    def RemoveCell(self, cell):
        iColumn = cell.grid_info()['column'] - 1
        categoryName = self.GetCell(cell.row, 0).text
        cell.text = 0
        self.SaveCellToModel(cell)
        self.vModel.SplitMoneyHistory.RemoveEntry(iColumn, categoryName)
        self.Refresh()

    def RemoveColumn(self, iColumn):
        self.vModel.SplitMoneyHistory.RemoveColumn(iColumn)
        self.Refresh()

    def GetCategoriesOfColumn(self, iColumn):
        cCategories = list()
        for vEntry in self.vModel.SplitMoneyHistory[iColumn].values():
            cCategories.append(vEntry.category)
        return cCategories

    def GetAddableCategories(self, iColumn):
        cAddableCategories = list()
        for category in self.vModel.Categories.values():
            if category.name not in [x.name for x in self.GetCategoriesOfColumn(iColumn)]:
                cAddableCategories.append(category)
        return cAddableCategories

    def AddCategoryToColumn(self, category, iColumn):
        self.vModel.SplitMoneyHistory.AddEntry(iColumn, category, 0)
        self.Refresh()

    def ShowHeaderMenu(self, event):
        iColumn = event.widget.grid_info()['column'] - 1
        vDropdown = tk.Menu(tearoff=False)
        vDropdown.add_command(label="Remove Column", command=lambda iColumn=iColumn: self.RemoveColumn(iColumn))
        vDropdown.add_command(label="Add Category", command=lambda iColumn=iColumn, x=event.x_root-self.winfo_rootx(), y=event.y_root-self.winfo_rooty():
                              BV.View.SelectCategoryPopup(self.parent, self.AddCategoryToColumn, self.GetAddableCategories(iColumn), (x, y), iColumn))
        vDropdown.post(event.x_root, event.y_root)

    def MakeX(self, cRowColumnPair):
        w = tk.Button(self, text="X", font=Fonts.FONT_SMALL_BOLD, borderwidth=2, width=3, relief='ridge',
                      command=lambda self=self: self.RemoveRow(cRowColumnPair[0]))
        w.grid(row=cRowColumnPair[0], column=cRowColumnPair[1], sticky="ns")

    def RemoveRow(self, iRow):
        self.vModel.NetWorth.RemoveRow(iRow-1)  # skip header
        self.Refresh()

    def SaveCellToModel(self, cell):
        iColumn = cell.column - 1
        categoryName = self.GetCell(cell.row, 0).text
        self.vModel.SplitMoneyHistory[iColumn][categoryName].amount = 0 if cell.text == "" else cell.text
        self.Refresh()
