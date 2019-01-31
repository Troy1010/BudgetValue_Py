import TM_CommonPy as TM
import tkinter as tk
import BudgetValue as BV
from BudgetValue.View import WidgetFactories as WF


class Table(TM.tk.TableFrame):
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
                    bEditableState = category.name != "<Default Category>"
                    w = WF.MakeEntry(self, (row, iColumn+1), text=split_money_history_column[category.name].amount_stream, bEditableState=bEditableState)
                    if bEditableState:
                        w.bind("<FocusOut>", lambda event, w=w: self.SaveCellToModel(w), add="+")
                        w.bind("<Button-3>", lambda event: self.ShowCellMenu(event), add="+")
                    bMadeEntry = True
            # Spent
            if self.vModel.SpendingHistory.cCategoryTotalStreams[category.name].value:
                w = WF.MakeEntry_ReadOnly(self, (row, self.iSpentColumn), text=self.vModel.SpendingHistory.cCategoryTotalStreams[category.name])
                bMadeEntry = True
            # Budgeted
            if bMadeEntry and category.type != BV.Model.CategoryType.income:
                WF.MakeEntry_ReadOnly(self, (row, self.iBudgetedColumn), text=self.vModel.BudgetedSpendables.cCategoryTotalStreams[category.name])
                bMadeEntry = True
            # Row Header
            if bMadeEntry and not self.GetCell(row, 0):
                WF.MakeEntry_ReadOnly(self, (row, 0), text=category.name, justify=tk.LEFT, bBold=True)
            #
            row += 1
        # Black bar
        tk.Frame(self, background='black', height=2).grid(row=row, columnspan=self.iBudgetedColumn+1, sticky="ew")
        row += 1
        # Total
        WF.MakeLable(self, (row, 0), text="Total", columnspan=self.iBudgetedColumn)
        WF.MakeEntry_ReadOnly(self, (row, self.iBudgetedColumn), text=self.vModel.BudgetedSpendables.total_stream, justify=tk.CENTER)
        row += 1
        # Accounts
        WF.MakeLable(self, (row, 0), text="Net Worth", columnspan=self.iBudgetedColumn)
        WF.MakeEntry_ReadOnly(self, (row, self.iBudgetedColumn), text=self.vModel.Accounts.total_stream, justify=tk.CENTER)
        row += 1
        # Balance
        WF.MakeLable(self, (row, 0), text="Balance", columnspan=self.iBudgetedColumn)
        vBalanceNum = WF.MakeEntry_ReadOnly(self, (row, self.iBudgetedColumn), text=self.vModel.Balance.balance_stream, justify=tk.CENTER)

        def __HighlightBalance(balance):
            if balance:
                vBalanceNum.config(readonlybackground="pink")
            else:
                vBalanceNum.config(readonlybackground="lightgreen")
        self.cDisposables.append(self.vModel.Balance.balance_stream.subscribe(
            __HighlightBalance
        ))
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

    def GetAddableCategories(self, iColumn):
        cAddableCategories = list()
        for category in self.vModel.Categories.values():
            if category.name not in self.vModel.SplitMoneyHistory[iColumn].keys():
                cAddableCategories.append(category)
        return cAddableCategories

    def AddCategoryToColumn(self, category, iColumn):
        self.vModel.SplitMoneyHistory.AddEntry(iColumn, category.name, 0)
        self.Refresh()

    def ShowHeaderMenu(self, event):
        iColumn = event.widget.grid_info()['column'] - 1
        vDropdown = tk.Menu(tearoff=False)
        vDropdown.add_command(label="Remove Column", command=lambda iColumn=iColumn: self.RemoveColumn(iColumn))
        vDropdown.add_command(label="Add Category", command=lambda iColumn=iColumn, x=event.x_root-self.winfo_rootx(), y=event.y_root-self.winfo_rooty():
                              BV.View.SelectCategoryPopup(self.parent, self.AddCategoryToColumn, self.GetAddableCategories(iColumn), (x, y), iColumn))
        vDropdown.post(event.x_root, event.y_root)

    def RemoveRow(self, iRow):
        self.vModel.Accounts.RemoveRow(iRow-1)  # skip header
        self.Refresh()

    def SaveCellToModel(self, cell):
        iColumn = cell.column - 1
        categoryName = self.GetCell(cell.row, 0).text
        self.vModel.SplitMoneyHistory[iColumn][categoryName].amount = cell.text
