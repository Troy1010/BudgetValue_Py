import TM_CommonPy as TM  # noqa
import tkinter as tk
import BudgetValue as BV
from BudgetValue.View import WidgetFactories as WF
from BudgetValue.View.Skin import vSkin  # noqa
from BudgetValue.Model.Categories import Categories
from BudgetValue.Model.Categories import CategoryType
from ..CategoryTable import CategoryTable


class Table(CategoryTable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # bind income_transactions M->V

        def GetColumnOfCategoryAmounts(categoryAmounts):  # fix: should just stream the transaction
            for i, x in enumerate(self.vModel.TransactionHistory.Iter_Income()):
                if id(x.categoryAmounts) == id(categoryAmounts):
                    return i + self.iFirstDataColumn
            else:
                return None

        def M_to_V_IncomeTransactions(col_edit):
            assert isinstance(col_edit, BV.Model.Misc.StreamInfo)
            if (col_edit.parent_collection == transaction.categoryAmounts for transaction in self.vModel.TransactionHistory.Iter_Income()):
                column = GetColumnOfCategoryAmounts(col_edit.parent_collection)
                if col_edit.bAdd:
                    self.MakeTransactionEntry(col_edit.stream, col_edit.category_name, column)
                else:
                    row = self.GetRowOfVMValue(col_edit.category_name)
                    if row is None:
                        pass  # cell has been removed by VM_CategoryTable
                    else:
                        cell = self.GetCell(row, column)
                        cell.grid_forget()
                        cell.destroy()
        self.vModel.TransactionHistory._merged_amountStream_stream.subscribe(M_to_V_IncomeTransactions)

    def Refresh(self):
        super().Refresh()
        # Refresh Transactions
        for column, income_transaction in enumerate(self.vModel.TransactionHistory.Iter_Income(), self.iFirstDataColumn):
            vColumnHeader = WF.MakeLable(self, (0, column), text=income_transaction.timestamp, font=vSkin.FONT_SMALL_BOLD, display=BV.DisplayTimestamp)
            vColumnHeader.transaction = income_transaction  # for GetTransactionOfColumn
            vColumnHeader.bind("<Button-3>", lambda event: self.ShowHeaderMenu(event))
            for category_name in income_transaction.categoryAmounts.GetAll():
                self.MakeTransactionEntry(income_transaction.categoryAmounts.GetAll()[category_name].amount_stream, category_name, column)

    def MakeTransactionEntry(self, amount_stream, category_name, column):
        category = self.vModel.Categories[category_name]
        row = self.GetRowOfVMValue(category_name)
        background = vSkin.BG_READ_ONLY if category == Categories.default_category else vSkin.BG_DEFAULT
        bEditableState = category != Categories.default_category
        w = WF.MakeEntry(self,
                         (row, column),
                         text=amount_stream,
                         bEditableState=bEditableState,
                         background=background,
                         validation=BV.MakeValid_Money,
                         display=BV.MakeValid_Money_ZeroIsNone
                         )
        w.category_name = category_name
        if bEditableState:
            w.bind("<Button-3>", lambda event: self.ShowCellMenu(event), add="+")

    def ShowCellMenu(self, event):
        vDropdown = tk.Menu(tearoff=False)
        vDropdown.add_command(label="Remove", command=lambda cell=event.widget: self.RemoveCell(cell))
        vDropdown.post(event.x_root, event.y_root)

    def ShowHeaderMenu(self, event):
        assert isinstance(event.widget.transaction, BV.Model.Transaction)
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
                if self.vModel.Categories[category_name].type == CategoryType.excess:
                    pass
                else:
                    event.widget.transaction.categoryAmounts.AddCategory(self.vModel.Categories[category_name], amount=paycheck_plan_row.amount)
            balance_amount = event.widget.transaction.categoryAmounts.balance_stream.value
            if self.vModel.Categories.savings.name in event.widget.transaction.categoryAmounts.keys():
                balance_amount += event.widget.transaction.categoryAmounts[self.vModel.Categories.savings.name].amount
            event.widget.transaction.categoryAmounts.AddCategory(self.vModel.Categories.savings, amount=balance_amount)
        vDropdown.add_command(label="Implement Paycheck Plan", command=lambda: ImplementPlan(self))
        vDropdown.post(event.x_root, event.y_root)

    def RemoveCell(self, cell):
        iColumn = cell.column - self.iFirstDataColumn
        self.vModel.TransactionHistory.GetIncome()[iColumn].categoryAmounts.RemoveCategory(cell.category_name)

    def GetTransactionOfColumn(self, iColumn):
        header = self.GetCell(0, iColumn)
        assert hasattr(header, 'transaction')
        return header.transaction

    def ForgetTransaction(self, transaction):
        self.vModel.TransactionHistory.RemoveTransaction(transaction)

    def GetAddableCategories(self, iColumn):
        iColumn -= self.iFirstDataColumn
        cAddableCategories = list()
        for category in self.vModel.Categories.values():
            if category.name not in self.vModel.TransactionHistory.GetIncome()[iColumn].categoryAmounts.GetAll().keys():
                cAddableCategories.append(category)
        return cAddableCategories

    def AddCategoryToColumn(self, category, transaction):
        transaction.categoryAmounts.AddCategory(category)
