import TM_CommonPy as TM  # noqa
import tkinter as tk
import BudgetValue as BV
from BudgetValue.View import WidgetFactories as WF
from BudgetValue.View.Skin import vSkin  # noqa
from .. import Misc


class Table(Misc.BudgetedTable):
    def Refresh(self):
        super().Refresh()
        # Category Total
        # Header
        WF.MakeHeader(self, (0, self.iFirstDataColumn), text="Category Total")
        # Category Total
        for row, category_total_stream in enumerate(self.vModel.SpendingHistory.cCategoryTotalStreams.values()):
            self.MakeEntry((row+self.iFirstDataRow, self.iFirstDataColumn), text=category_total_stream, bEditableState=False)
        self.iFirstDataColumn += 1
        # Header
        WF.MakeHeader(self, (0, self.iFirstDataColumn), text="Import Transactions")
        # Import Transactions
        for row, category_total_stream in enumerate(self.vModel.ImportTransactionHistory.cCategoryTotalStreams.values()):
            self.MakeEntry((row+self.iFirstDataRow, self.iFirstDataColumn), text=category_total_stream, bEditableState=False)
        self.iFirstDataColumn += 1
        # Column Header
        for iColumn, split_money_history_column in enumerate(self.vModel.SpendingHistory):
            vColumnHeader = WF.MakeHeader(self, (0, iColumn+self.iFirstDataColumn), text="Column "+str(iColumn+1))
            vColumnHeader.bind("<Button-3>", lambda event: self.ShowHeaderMenu(event))
        # Data
        for row, category in enumerate(self.vModel.Categories.Select()):
            # SpendingHistory
            for iColumn, split_money_history_column in enumerate(self.vModel.SpendingHistory):
                if category.name in split_money_history_column:
                    w = self.MakeEntry((row+self.iFirstDataRow, iColumn+self.iFirstDataColumn),
                                       text=split_money_history_column[category.name].amount_stream
                                       )
                    w.bind("<FocusOut>", lambda event, w=w: self.SaveCellToModel(w), add="+")
                    w.bind("<Button-3>", lambda event: self.ShowCellMenu(event), add="+")
        #
        self.FinishRefresh()

    def MakeEntry(self, *args, **kwargs):
        w = WF.MakeEntry(self, *args, **kwargs)
        # Validation
        w.ValidationHandler = BV.MakeValid_Money_ZeroIsNone
        #
        return w

    def ShowCellMenu(self, event):
        vDropdown = tk.Menu(tearoff=False)
        vDropdown.add_command(label="Remove Entry", command=lambda cell=event.widget: self.RemoveCell(cell))
        vDropdown.post(event.x_root, event.y_root)

    def RemoveCell(self, cell):
        iColumn = cell.grid_info()['column'] - self.iFirstDataColumn
        categoryName = self.GetCell(cell.row, 0).text
        cell.text = 0
        self.SaveCellToModel(cell)
        self.vModel.SpendingHistory.RemoveEntry(iColumn, categoryName)
        self.Refresh()

    def RemoveColumn(self, iColumn):
        self.vModel.SpendingHistory.RemoveColumn(iColumn)
        self.Refresh()

    def GetAddableCategories(self, iColumn):
        cAddableCategories = list()
        for category in self.vModel.Categories.values():
            if category.name not in self.vModel.SpendingHistory[iColumn].keys():
                cAddableCategories.append(category)
        return cAddableCategories

    def AddCategoryToColumn(self, category, iColumn):
        self.vModel.SpendingHistory.AddEntry(iColumn, category.name, 0)
        self.Refresh()

    def ShowHeaderMenu(self, event):
        iColumn = event.widget.grid_info()['column'] - self.iFirstDataColumn
        vDropdown = tk.Menu(tearoff=False)
        vDropdown.add_command(label="Remove Column", command=lambda iColumn=iColumn: self.RemoveColumn(iColumn))
        vDropdown.add_command(label="Add Category", command=lambda iColumn=iColumn, x=event.x_root-self.winfo_rootx(), y=event.y_root-self.winfo_rooty():
                              BV.View.SelectCategoryPopup(self.parent, self.AddCategoryToColumn, self.GetAddableCategories(iColumn), (x, y), iColumn))
        vDropdown.post(event.x_root, event.y_root)

    def SaveCellToModel(self, cell):
        iColumn = cell.column - self.iFirstDataColumn
        categoryName = self.GetCell(cell.row, 0).text
        print('SaveCellToModel. categoryName:'+categoryName+" amount:"+str(cell.text))
        self.vModel.SpendingHistory[iColumn][categoryName].amount = cell.text
