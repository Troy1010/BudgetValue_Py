import TM_CommonPy as TM  # noqa
import tkinter as tk
import BudgetValue as BV
from BudgetValue.View import WidgetFactories as WF
from BudgetValue.View.Skin import vSkin  # noqa
from .. import Misc
from BudgetValue.Model.Categories import Categories
from BudgetValue.Model.Categories import CategoryType


class Table(Misc.CategoryTable):
    def Refresh(self):
        super().Refresh()
        self.AddSpacersForBudgeted()
        # Column Header
        for iColumn, income_transaction in enumerate(self.vModel.TransactionHistory.Iter_Income()):
            vColumnHeader = WF.MakeLable(self, (0, iColumn+self.iFirstDataColumn), text=income_transaction.timestamp, font=vSkin.FONT_SMALL_BOLD, display=BV.DisplayTimestamp)
            vColumnHeader.transaction = income_transaction  # for GetTransactionOfColumn
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
                                     validation=BV.MakeValid_Money,
                                     display=BV.MakeValid_Money_ZeroIsNone
                                     )
                    if bEditableState:
                        w.bind("<Button-3>", lambda event: self.ShowCellMenu(event), add="+")
        #
        self.AddSeparationLables(no_text=True)

    def ShowCellMenu(self, event):
        vDropdown = tk.Menu(tearoff=False)
        vDropdown.add_command(label="Remove", command=lambda cell=event.widget: self.RemoveCell(cell))
        vDropdown.post(event.x_root, event.y_root)

    def ShowHeaderMenu(self, event):
        vDropdown = tk.Menu(tearoff=False)
        vDropdown.add_command(label="Forget Transaction", command=lambda: self.ForgetTransaction(event.widget.transaction))
        vDropdown.add_command(label="Add Category", command=lambda x=event.x_root-self.winfo_toplevel().winfo_rootx(), y=event.y_root-self.winfo_toplevel().winfo_rooty(): (
                              BV.View.Popup_SelectCategory(self.winfo_toplevel(),
                                                           lambda category: self.AddCategoryToColumn(category, event.widget.transaction),
                                                           self.GetAddableCategories(event.widget.column),
                                                           cPos=(x, y)
                                                           )
                              ))

        def ImplementPlan(self):
            for category_name, paycheck_plan_row in self.vModel.PaycheckPlan.items():
                if self.vModel.Categories[category_name].type == CategoryType.income or self.vModel.Categories[category_name].type == CategoryType.excess:
                    pass  # -event.widget.transaction.amount
                else:
                    event.widget.transaction.categoryAmounts.AddCategory(self.vModel.Categories[category_name], amount=paycheck_plan_row.amount)
            event.widget.transaction.categoryAmounts.AddCategory(self.vModel.Categories.savings, amount=-event.widget.transaction.amount)  # -event.widget.transaction.categoryAmounts[category_name].amount)
            self.Refresh()
        vDropdown.add_command(label="Implement Paycheck Plan", command=lambda: ImplementPlan(self))
        vDropdown.post(event.x_root, event.y_root)

    def RemoveCell(self, cell):
        iColumn = cell.column - self.iFirstDataColumn
        category = self.vModel.Categories[self.GetCell(cell.row, 0).text]
        self.vModel.TransactionHistory.GetIncome()[iColumn].categoryAmounts.RemoveCategory(category)
        self.Refresh()

    def GetTransactionOfColumn(self, iColumn):
        header = self.GetCell(0, iColumn)
        assert hasattr(header, 'transaction')
        return header.transaction

    def ForgetTransaction(self, transaction):
        self.vModel.TransactionHistory.RemoveTransaction(transaction)
        self.Refresh()

    def GetAddableCategories(self, iColumn):
        iColumn -= self.iFirstDataColumn
        cAddableCategories = list()
        for category in self.vModel.Categories.values():
            if category.name not in self.vModel.TransactionHistory.GetIncome()[iColumn].categoryAmounts.GetAll().keys():
                cAddableCategories.append(category)
        return cAddableCategories

    def AddCategoryToColumn(self, category, transaction):
        transaction.categoryAmounts.AddCategory(category)
        self.Refresh()
