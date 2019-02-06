import TM_CommonPy as TM  # noqa
import tkinter as tk
import BudgetValue as BV
from BudgetValue.View import WidgetFactories as WF
from BudgetValue.View.Skin import vSkin  # noqa
from .. import Misc
from BudgetValue.Model.Categories import Categories


class Table(Misc.BudgetedTable):
    def Refresh(self):
        super().Refresh()
        # Column Header
        for iColumn, income_transaction in enumerate(self.vModel.TransactionHistory.Iter_Income()):
            vColumnHeader = WF.MakeLable(self, (0, iColumn+self.iFirstDataColumn), text=income_transaction.timestamp, font=vSkin.FONT_SMALL_BOLD, display=BV.DisplayTimestamp)
            vColumnHeader.bind("<Button-3>", lambda event: self.ShowHeaderMenu(event))
        # Data
        for row, category in enumerate(self.vModel.Categories.Select(), self.iFirstDataRow):
            for column, income_transaction in enumerate(self.vModel.TransactionHistory.Iter_Income(), self.iFirstDataColumn):
                if category.name in income_transaction.categoryAmounts.GetAll().keys():
                    background = vSkin.BG_READ_ONLY if category == Categories.default_category else vSkin.BG_DEFAULT
                    bEditableState = category != Categories.default_category
                    w = WF.MakeEntry(self,
                                     (row, column),
                                     text=income_transaction.categoryAmounts.GetAll()[category.name].amount_stream,
                                     bEditableState=bEditableState,
                                     background=background,
                                     validation=BV.MakeValid_Money
                                     )
                    if bEditableState:
                        w.bind("<Button-3>", lambda event: self.ShowCellMenu(event), add="+")

        #
        self.FinishRefresh()

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
            if category.name not in self.vModel.TransactionHistory.GetIncome()[iColumn].categoryAmounts.GetAll().keys():
                cAddableCategories.append(category)
        return cAddableCategories

    def AddCategoryToColumn_OLD(self, category, iColumn):
        self.vModel.SplitMoneyHistory.AddEntry(iColumn, category.name, 0)
        self.Refresh()

    def AddCategoryToColumn(self, category, iColumn):  # assume iColumn is already adjusted
        transaction = self.vModel.TransactionHistory.GetIncome()[iColumn]
        transaction.categoryAmounts.AddCategory(category)
        self.Refresh()

    def ShowHeaderMenu(self, event):
        iColumn = event.widget.grid_info()['column'] - self.iFirstDataColumn
        vDropdown = tk.Menu(tearoff=False)
        vDropdown.add_command(label="Remove Column", command=lambda iColumn=iColumn: self.RemoveColumn(iColumn))
        vDropdown.add_command(label="Add Category", command=lambda iColumn=iColumn, x=event.x_root-self.winfo_rootx(), y=event.y_root-self.winfo_rooty(): (
                              BV.View.SelectCategoryPopup(self.parent,
                                                          lambda category, iColumn=iColumn: self.AddCategoryToColumn(category, iColumn),
                                                          self.GetAddableCategories(iColumn),
                                                          cPos=(x, y)
                                                          )
                              ))
        vDropdown.post(event.x_root, event.y_root)

    def SaveCellToModel(self, cell):
        iColumn = cell.column - self.iFirstDataColumn
        categoryName = self.GetCell(cell.row, 0).text
        self.vModel.SplitMoneyHistory[iColumn][categoryName].amount = cell.text
