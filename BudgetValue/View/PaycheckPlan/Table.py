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
        self.vModel.PaycheckPlan.total_Observable.subscribe(lambda total: None if not hasattr(self, 'vTotalNum') else setattr(self.vTotalNum, 'text', total))

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
                w = self.MakeEntry((row, 1))
                w = self.MakeEntry((row, 2), text=period)
                w = self.MakeEntry((row, 3), text=amount)
                self.MakeRowValid(row)
            else:
                BV.View.MakeRowHeader(self, (row, 0), text=category.name, columnspan=3)
                w = self.MakeEntry((row, 3), text=amount)
                if self.GetCategoryOfRow(w.row).name == "<Default Category>":
                    self.vTotalNum = w
            row += 1

    def MakeEntry(self, cRowColumnPair, text=None):
        w = BV.View.MakeEntry(self, cRowColumnPair, text=text)
        w.bind("<FocusOut>", lambda event, w=w: self.MakeRowValid(w.row, w), add="+")
        w.bind("<FocusOut>", lambda event, w=w: self.SaveToModel(w.row), add="+")
        return w

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
        # Determine category
        category = self.GetCategoryOfRow(row)
        #
        if category.name not in self.vModel.PaycheckPlan:
            self.vModel.PaycheckPlan[category.name] = BV.Model.CategoryPlan(category=self.vModel.Categories[category.name])
        #
        if self.GetCell(row, 2):
            self.vModel.PaycheckPlan[category.name].period = self.GetCell(row, 2).text
        self.vModel.PaycheckPlan[category.name].amount = self.GetCell(row, 3).text
        #
        if self.vModel.PaycheckPlan[category.name].IsEmpty():
            del self.vModel.PaycheckPlan[category.name]

    def GetCategoryOfRow(self, row):
        categoryName = self.GetCell(row, 0).text
        return self.vModel.Categories[categoryName]
