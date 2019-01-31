import TM_CommonPy as TM  # noqa
import tkinter as tk  # noqa
import rx  # noqa
from .Skin import vSkin  # noqa
import BudgetValue as BV
from . import WidgetFactories as WF


class BudgetedTable(TM.tk.TableFrame):
    def __init__(self, parent, vModel):
        assert isinstance(vModel, BV.Model.Model)
        tk.Frame.__init__(self, parent)
        self.vModel = vModel
        self.parent = parent
        self.cDisposables = []
        self.iFirstDataColumn = 2
        self.iFirstDataRow = 1

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
        WF.MakeHeader(self, (row, 1), text="Budgeted", background=vSkin.BUDGETED)
        row += 1
        # Data
        for category in self.vModel.Categories.Select():
            # Budgeted
            if category.name in self.vModel.BudgetedSpendables.cCategoryTotalStreams:
                WF.MakeEntry_ReadOnly(self, (row, 1), text=self.vModel.BudgetedSpendables.cCategoryTotalStreams[category.name], background=vSkin.BUDGETED)
            row += 1
        # if the name of the caller is Refresh, then we are trusting that that will call FinishRefresh when it's done
        if TM.FnName(1) != "Refresh":
            self.FinishRefresh()

    def FinishRefresh(self):
        self.AddRowHeaders()
        self.AddSeparationLables()

    def AddSeparationLables(self):
        prev_type = None
        row = self.iFirstDataRow
        max_row = self.GetMaxRow()
        while row <= max_row:
            category = self.GetCategoryOfRow(row)
            if category is None:
                row += 1
                continue
            if prev_type != category.type:
                prev_type = category.type
                self.InsertRow(row)
                WF.MakeSeparationLable(self, row, "  " + prev_type.name.capitalize())
                max_row += 1
                row += 1
            row += 1

    def GetCategoryOfRow(self, row):
        try:
            return self.vModel.Categories[self.GetCell(row, 0).text]
        except AttributeError:  # cell does not have .text
            return None

    def AddRowHeaders(self):
        for row, category in enumerate(self.vModel.Categories.Select()):
            # Row Header
            if not self.GetCell(row+self.iFirstDataRow, 0) and not self.IsRowEmpty(row+self.iFirstDataRow):
                WF.MakeEntry_ReadOnly(self, (row+self.iFirstDataRow, 0), text=category.name, justify=tk.LEFT, bBold=True)
