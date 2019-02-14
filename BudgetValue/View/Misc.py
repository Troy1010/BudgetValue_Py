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
        self.ClearTable()
        if hasattr(self, 'cDisposables'):
            for disposable in self.cDisposables:
                disposable.dispose()
        self.cDisposables = []


class CategoryTable(ModelTable):
    iFirstDataColumn = 1
    iFirstDataRow = 1

    def __init__(self, parent, vModel):
        super().__init__(parent, vModel)
        self._cRowToCategory = {}

    def Refresh(self):
        super().Refresh()
        # add new
        # Column Header
        WF.MakeHeader(self, (0, 0), text="Category")
        # if the name of the caller is Refresh, then we are trusting that that will call FinishRefresh when it's done
        if TM.FnName(1) != "Refresh":
            self.FinishRefresh()

    def FinishRefresh(self):
        self.AddRowHeaders()
        self.AddSeparationLables()
        self._PopulateRowToCategory()

    def _PopulateRowToCategory(self):
        # Populate _cRowToCategory
        row = self.iFirstDataRow
        max_row = self.GetMaxRow()
        while row <= max_row:
            category = self.__GetCategoryOfRow_ByRowHeaderText(row)
            if category is not None:
                self._cRowToCategory[row] = category
            row += 1

    def AddSeparationLables(self):
        prev_type = None
        row = self.iFirstDataRow
        max_row = self.GetMaxRow()
        while row <= max_row:
            category = self.__GetCategoryOfRow_ByRowHeaderText(row)
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
        return self.__cRowToCategory[row]

    def __GetCategoryOfRow_ByRowHeaderText(self, row):
        try:
            return self.vModel.Categories[self.GetCell(row, 0).text]
        except AttributeError:  # cell does not have .text
            return None

    def AddRowHeaders(self):
        for row, category in enumerate(self.vModel.Categories.Select()):
            # Row Header
            if not self.GetCell(row+self.iFirstDataRow, 0) and not self.IsRowEmpty(row+self.iFirstDataRow):
                WF.MakeEntry(self, (row+self.iFirstDataRow, 0), text=category.name, justify=tk.LEFT, bBold=True, bEditableState=False, background=vSkin.BG_ENTRY)


class BudgetedTable(CategoryTable):
    iFirstDataColumn = 2

    def __init__(self, parent, vModel):
        super().__init__(parent, vModel)
        assert isinstance(vModel, BV.Model.Model)
        # Refresh when new values come in
        vModel.TransactionHistory._merged_amountStream_stream.subscribe(lambda x: self.Refresh())

    def Refresh(self):
        super().Refresh()
        #
        row = 0
        #
        WF.MakeHeader(self, (row, 1), text="Budgeted", background=vSkin.BG_BUDGETED)
        row += 1
        # Data
        for category in self.vModel.Categories.Select():
            # Budgeted
            if category.name in self.vModel.Budgeted.cCategoryTotalStreams:
                w = WF.MakeEntry_ReadOnly(self, (row, 1), text=self.vModel.Budgeted.cCategoryTotalStreams[category.name], validation=BV.MakeValid_Money, display=BV.MakeValid_Money_ZeroIsNone)
                # Highlight

                def HighlightBudgeted(budgeted_amount, w):
                    if budgeted_amount < 0:
                        w.configure(readonlybackground=vSkin.BG_BUDGETED_BAD)
                    else:
                        w.configure(readonlybackground=vSkin.BG_BUDGETED)
                disposable = self.vModel.Budgeted.cCategoryTotalStreams[category.name].subscribe(
                    lambda budgeted_amount, w=w: HighlightBudgeted(budgeted_amount, w)
                )
                self.cDisposables.append(disposable)
            row += 1
        # if the name of the caller is Refresh, then we are trusting that that will call FinishRefresh when it's done
        if TM.FnName(1) != "Refresh":
            self.FinishRefresh()
