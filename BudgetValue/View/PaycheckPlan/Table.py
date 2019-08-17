from BudgetValue._Logger import BVLog  # noqa
import tkinter as tk
import BudgetValue as BV
from decimal import Decimal
from BudgetValue.Model import CategoryType  # noqa
from BudgetValue.View import WidgetFactories as WF
from ...Model.Categories import Categories
from ..CategoryTable import CategoryTable
from ..Skin import vSkin


class Table(CategoryTable):
    def __init__(self, parent, vModel):
        super().__init__(parent, vModel)
        assert isinstance(vModel, BV.Model.Model)
        tk.Frame.__init__(self, parent)
        self.vModel = vModel
        self.parent = parent
        self.iFirstDataColumn += 1  # Make space for AddRowHeaderColumn

    def Refresh(self):
        super().Refresh()
        # Header
        for j, header_name in enumerate(['Amount', 'Period', 'Plan']):
            WF.MakeHeader(self, (0, j+self.iFirstDataColumn), text=header_name)
        # Data
        for row, category in enumerate(self.vModel.Categories.Select(), self.iFirstDataRow):
            amount_stream = None if category.name not in self.vModel.PaycheckPlan else self.vModel.PaycheckPlan[category.name].amount_stream
            try:
                period = self.vModel.PaycheckPlan[category.name].period
            except (AttributeError, KeyError):
                period = None
            if category.IsSpendable():
                self.MakeEntry_Money((row, 1))
                self.MakeEntry((row, 2), text=period)
                self.MakeEntry_Money((row, 3), text=amount_stream)
            else:
                bEditableState = category != Categories.default_category
                self.MakeEntry_Money((row, 3), text=amount_stream, bEditableState=bEditableState)

    def MakeEntry(self, cRowColumnPair, text=None, bEditableState=True):
        background = vSkin.BG_READ_ONLY if not bEditableState else vSkin.BG_DEFAULT
        w = WF.MakeEntry(self, cRowColumnPair, text=text, bEditableState=bEditableState, background=background)
        if bEditableState:
            w.bind("<FocusOut>", lambda event, w=w: self.MakeRowValid(w.row, w), add="+")
            w.bind("<FocusOut>", lambda event, w=w: self.SaveToModel(w.row), add="+")
        return w

    def MakeEntry_Money(self, cRowColumnPair, text=None, bEditableState=True):
        w = self.MakeEntry(cRowColumnPair, text, bEditableState)
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
        else:
            periodText = None
        amountText = self.GetCell(row, 3).text
        # Remove or add CategoryPlan
        if not (periodText or amountText):
            if category.name in self.vModel.PaycheckPlan:
                del self.vModel.PaycheckPlan[category.name]
            return
        elif category.name not in self.vModel.PaycheckPlan:
            self.vModel.PaycheckPlan[category.name] = BV.Model.PaycheckPlanRow()
        # Set values
        if self.GetCell(row, 2):
            self.vModel.PaycheckPlan[category.name].period = periodText
        self.vModel.PaycheckPlan[category.name].amount = amountText

    def GetCategoryOfRow(self, row):
        category_name = self.GetCell(row, 0).text
        return self.vModel.Categories[category_name]
