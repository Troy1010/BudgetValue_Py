from BudgetValue._Logger import BVLog  # noqa
import tkinter as tk
import TM_CommonPy as TM
import BudgetValue as BV
from decimal import Decimal
from BudgetValue.Model import CategoryType  # noqa


class Table(TM.tk.TableFrame):
    def __init__(self, parent, vModel):
        tk.Frame.__init__(self, parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.parent = parent
        self.vTotalCell = None
        self.vModel.PaycheckPlan.total_Observable.subscribe(on_next=lambda value: self.ShowTotal(value))

    def ShowTotal(self, value):
        if self.vTotalCell is not None:
            self.vTotalCell.text = value

    def Refresh(self):
        # remove old
        for child in BV.GetAllChildren(self):
            child.grid_forget()
            child.destroy()
        # add new
        row = 0
        # Header
        for j, header_name in enumerate(['Category', 'Amount', 'Period', 'Plan']):
            BV.View.MakeHeader(self, (row, j), text=header_name)
        row += 1
        # Data
        prev_type = None
        for category in self.vModel.Categories.Select():
            # make separation label if needed
            if prev_type != category.type:
                prev_type = category.type
                BV.View.MakeSeparationLable(self, row, "  " + prev_type.name.capitalize())
                row += 1
            # generate row
            amount = None if category.name not in self.vModel.PaycheckPlan else self.vModel.PaycheckPlan[category.name].amount
            period = None if category.name not in self.vModel.PaycheckPlan else self.vModel.PaycheckPlan[category.name].period
            if category.IsSpendable():
                BV.View.MakeRowHeader(self, (row, 0), text=category.name)
                w = BV.View.MakeEntry(self, (row, 1))
                w.bind("<FocusOut>", lambda event, row=row: self.SaveToModel(row), add="+")
                w = BV.View.MakeEntry(self, (row, 2), text=period)
                w.bind("<FocusOut>", lambda event, row=row: self.SaveToModel(row), add="+")
                w = BV.View.MakeEntry(self, (row, 3), text=amount)
                w.bind("<FocusOut>", lambda event, row=row: self.SaveToModel(row), add="+")
                self.MakeRowValid(row)
            else:
                BV.View.MakeRowHeader(self, (row, 0), text=category.name, columnspan=3)
                w = BV.View.MakeEntry(self, (row, 3), text=amount)
                w.bind("<FocusOut>", lambda event, row=row: self.SaveToModel(row), add="+")
                if self.GetCategoryOfRow(w.row).name == "<Default Category>":
                    self.vTotalCell = w
            row += 1

    def MakeRowValid(self, row, cellToKeep=None):
        columnToKeep = -1 if cellToKeep is None else cellToKeep.column
        if self.GetCategoryOfRow(row).IsSpendable():
            # Get values of row
            amount = None if not self.GetCell(row, 1).text else Decimal(str(self.GetCell(row, 1).text))
            period = None if not self.GetCell(row, 2).text else Decimal(str(self.GetCell(row, 2).text))
            plan = None if not self.GetCell(row, 3).text else Decimal(str(self.GetCell(row, 3).text))
            # if we can complete the row, do so.
            if columnToKeep != 3 and amount and period:
                self.GetCell(row, 3).text = amount / period
            elif columnToKeep != 2 and amount and plan:
                self.GetCell(row, 2).text = amount / plan
            elif columnToKeep != 1 and period and plan:
                self.GetCell(row, 1).text = plan * period

    def SaveToModel(self, row):
        # Get category
        category = self.GetCategoryOfRow(row)
        # Make a category_plan out of the view's data
        category_plan = BV.Model.CategoryPlan(category)
        if category.IsSpendable():
            category_plan.amount = self.GetCell(row, 3).text
            category_plan.period = self.GetCell(row, 2).text
        else:
            category_plan.amount = self.GetCell(row, 3).text
        # Add category_plan to model
        if category_plan.IsEmpty():
            if category.name in self.vModel.PaycheckPlan:
                del self.vModel.PaycheckPlan[category.name]
        else:
            self.vModel.PaycheckPlan[category.name] = category_plan

    def GetCategoryOfRow(self, row):
        categoryName = self.GetCell(row, 0).text
        return self.vModel.Categories[categoryName]
