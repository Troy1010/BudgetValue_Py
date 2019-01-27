from BudgetValue._Logger import BVLog  # noqa
import tkinter as tk
import TM_CommonPy as TM
import BudgetValue as BV
from decimal import Decimal
from BudgetValue.Model import CategoryType  # noqa
from BudgetValue.View.Skin import vSkin
from BudgetValue.View import WidgetFactories as WF


class Table(TM.tk.TableFrame):
    def __init__(self, parent, vModel):
        assert isinstance(vModel, BV.Model.Model)
        tk.Frame.__init__(self, parent)
        self.vModel = vModel
        self.parent = parent

        def ShowNewTotal(self):
            if hasattr(self, 'vTotalNum'):
                self.vTotalNum.text = self.vModel.PaycheckPlan["<Default Category>"].amount
        self.vModel.PaycheckPlan.total_stream.subscribe(lambda total: ShowNewTotal(self))

    def Refresh(self):
        # remove old
        for child in BV.GetAllChildren(self):
            child.grid_forget()
            child.destroy()
        # add new
        row = 0
        # Header
        for j, header_name in enumerate(['Category', 'Amount', 'Period', 'Plan']):
            WF.MakeHeader(self, (row, j), text=header_name)
        row += 1
        # Data
        prev_type = None
        for category in self.vModel.Categories.Select():
            # make separation label if needed
            if prev_type != category.type:
                prev_type = category.type
                WF.MakeSeparationLable(self, row, "  " + prev_type.name.capitalize())
                row += 1
            # generate row
            amount = None if category.name not in self.vModel.PaycheckPlan else self.vModel.PaycheckPlan[category.name].amount
            try:
                period = self.vModel.PaycheckPlan[category.name].period
            except (AttributeError, KeyError):
                period = None
            WF.MakeRowHeader(self, (row, 0), text=category.name, columnspan=3)
            if category.IsSpendable():
                self.MakeEntry_Money((row, 1))
                self.MakeEntry((row, 2), text=period)
                self.MakeEntry_Money((row, 3), text=amount)
                self.MakeRowValid(row)
            else:
                if category.name == "<Default Category>":
                    w = WF.MakeEntry_ReadOnly(self, (row, 3), text=amount, background=vSkin.READ_ONLY)
                else:
                    w = self.MakeEntry_Money((row, 3), text=amount)
                if self.GetCategoryOfRow(w.row).name == "<Default Category>":
                    self.vTotalNum = w
            row += 1

    def MakeEntry(self, cRowColumnPair, text=None):
        w = WF.MakeEntry(self, cRowColumnPair, text=text)
        w.bind("<FocusOut>", lambda event, w=w: self.MakeRowValid(w.row, w), add="+")
        w.bind("<FocusOut>", lambda event, w=w: self.SaveToModel(w.row), add="+")
        return w

    def MakeEntry_Money(self, cRowColumnPair, text=None):
        w = self.MakeEntry(cRowColumnPair, text)
        w.ValidationHandler = BV.MakeValid_Money
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
        # Retrieve text
        if self.GetCell(row, 2):
            periodText = self.GetCell(row, 2).text
        amountText = self.GetCell(row, 3).text
        # Remove or add CategoryPlan
        if not (periodText or amountText):
            if category.name in self.vModel.PaycheckPlan:
                del self.vModel.PaycheckPlan[category.name]
            return
        elif category.name not in self.vModel.PaycheckPlan:
            self.vModel.PaycheckPlan[category.name] = BV.Model.PaycheckPlanRow(category=self.vModel.Categories[category.name])
        # Set values
        if self.GetCell(row, 2):
            self.vModel.PaycheckPlan[category.name].period = periodText
        self.vModel.PaycheckPlan[category.name].amount = amountText

    def GetCategoryOfRow(self, row):
        categoryName = self.GetCell(row, 0).text
        return self.vModel.Categories[categoryName]
