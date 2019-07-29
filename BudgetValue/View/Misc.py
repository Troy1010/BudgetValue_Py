import TM_CommonPy as TM  # noqa
import tkinter as tk  # noqa
import rx  # noqa
from .Skin import vSkin  # noqa
import BudgetValue as BV
from . import WidgetFactories as WF


class ModelTable(TM.tk.TableFrame):
    iFirstDataColumn = 0
    iFirstDataRow = 1

    def __init__(self, parent, vModel):
        super().__init__(parent)
        assert isinstance(vModel, BV.Model.Model)
        self.vModel = vModel
        self.parent = parent
        self.cDisposables = []

    def Refresh(self):
        # remove old
        for child in self.winfo_children():
            try:
                if not child.bPerminent:
                    child.grid_forget()
                    child.destroy()
            except AttributeError:
                child.grid_forget()
                child.destroy()
        # self.ClearTable()
        if hasattr(self, 'cDisposables'):
            for disposable in self.cDisposables:
                disposable.dispose()
        self.cDisposables = []


class CategoryTable(ModelTable):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iFirstDataColumn = 0
        self.iFirstDataRow = 1

    def FinishRefresh(self):
        self.AddSeparationLables()

    def AddSpacersForBudgeted(self):
        row = self.iFirstDataRow
        # Data
        for category in self.vModel.Categories.Select():
            # Budgeted
            if category.name in self.vModel.Budgeted.cCategoryTotalStreams:
                w = tk.Frame(self)
                w.grid(row=row, column=self.iFirstDataColumn)
            row += 1
        #
        self.iFirstDataColumn += 1

    def AddSeparationLables(self):
        print("***AddSeparationLabels called on:"+str(self))
        prev_type = None
        row = self.GetMaxRow()
        while row >= self.iFirstDataRow:
            category = self.GetCategoryOfRow(row)
            if category is None:
                row -= 1
                continue
            if prev_type != category.type:
                prev_type = category.type
                self.InsertRow(row)
                WF.MakeSeparationLable(self, row, "  " + category.type.name.capitalize())
                print("Creating SeparationLable:"+category.type.name.capitalize()+" from category:"+category.name+" at row:"+str(row))
            row -= 1

    def GetCategoryOfRow(self, row):
        # if not self.IsRowEmpty(row):
        #     for cell in self.grid_slaves(row):
        #         # try:
        #         return cell.spend
        #         # except
        # Only works before SeparationLables are added
        # fix: There must be a better way..
        for i, category in enumerate(self.vModel.Categories.values()):
            if i == row - self.iFirstDataRow:
                return category
        return None
        for i, category in enumerate(self.vModel.Categories.Select()):
            if i == row - self.iFirstDataRow:
                return category
        return None

    def AddRowHeaderColumn(self):
        # Column Header
        WF.MakeHeader(self, (0, 0), text="Category")
        for row, category in enumerate(self.vModel.Categories.Select()):
            # Row Header
            if not self.GetCell(row+self.iFirstDataRow, 0) and not self.IsRowEmpty(row+self.iFirstDataRow):
                WF.MakeEntry(self, (row+self.iFirstDataRow, 0), text=category.name, justify=tk.LEFT, bBold=True, bEditableState=False, background=vSkin.BG_ENTRY)
