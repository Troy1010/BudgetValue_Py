import TM_CommonPy as TM  # noqa
import tkinter as tk
import BudgetValue as BV
from BudgetValue.View import WidgetFactories as WF
from BudgetValue.View.Skin import vSkin  # noqa
from .. import Misc


class Table(Misc.BudgetedTable):
    def Refresh(self):
        super().Refresh()
        # Column Header
        for iColumn, split_money_history_column in enumerate(self.vModel.SplitMoneyHistory):
            vColumnHeader = WF.MakeHeader(self, (0, iColumn+self.iFirstDataColumn), text="Column "+str(iColumn+1))
            vColumnHeader.bind("<Button-3>", lambda event: self.ShowHeaderMenu(event))
        # Data
        for row, category in enumerate(self.vModel.Categories.Select()):
            # SplitMoneyHistory
            for iColumn, split_money_history_column in enumerate(self.vModel.SplitMoneyHistory):
                if category.name in split_money_history_column:
                    bEditableState = category.name != "<Default Category>"
                    w = WF.MakeEntry(self, (row+self.iFirstDataRow, iColumn+self.iFirstDataColumn), text=split_money_history_column[category.name].amount_stream, bEditableState=bEditableState)
                    if bEditableState:
                        w.bind("<FocusOut>", lambda event, w=w: self.SaveCellToModel(w), add="+")
                        w.bind("<Button-3>", lambda event: self.ShowCellMenu(event), add="+")
        #
        super().FinishRefresh()

    def ShowCellMenu(self, event):
        vDropdown = tk.Menu(tearoff=False)
        vDropdown.add_command(label="Remove Entry", command=lambda cell=event.widget: self.RemoveCell(cell))
        vDropdown.post(event.x_root, event.y_root)

    def RemoveCell(self, cell):
        iColumn = cell.grid_info()['column'] - self.iFirstDataColumn
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
        iColumn = event.widget.grid_info()['column'] - self.iFirstDataColumn
        vDropdown = tk.Menu(tearoff=False)
        vDropdown.add_command(label="Remove Column", command=lambda iColumn=iColumn: self.RemoveColumn(iColumn))
        vDropdown.add_command(label="Add Category", command=lambda iColumn=iColumn, x=event.x_root-self.winfo_rootx(), y=event.y_root-self.winfo_rooty():
                              BV.View.SelectCategoryPopup(self.parent, self.AddCategoryToColumn, self.GetAddableCategories(iColumn), (x, y), iColumn))
        vDropdown.post(event.x_root, event.y_root)

    def SaveCellToModel(self, cell):
        iColumn = cell.column - self.iFirstDataColumn
        categoryName = self.GetCell(cell.row, 0).text
        self.vModel.SplitMoneyHistory[iColumn][categoryName].amount = cell.text
