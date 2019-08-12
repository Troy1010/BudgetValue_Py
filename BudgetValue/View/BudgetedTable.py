import TM_CommonPy as TM  # noqa
import tkinter as tk  # noqa
import BudgetValue as BV  # noqa
from BudgetValue.View import WidgetFactories as WF  # noqa
from . import Misc  # noqa
from .Skin import vSkin
from .CategoryTable import CategoryTable


class BudgetedTable(CategoryTable):
    iFirstDataColumn = 2

    def __init__(self, parent, vModel):
        super().__init__(parent, vModel)
        assert isinstance(vModel, BV.Model.Model)

    def Refresh(self):
        super().Refresh()
        self.AddBudgetedColumn()
        self.AddRowHeaderColumn()
        self.AddSeparationLables()
        return  # fix
        row = self.GetMaxRow() + 1
        # Black bar
        tk.Frame(self, background='black', height=2).grid(row=row, columnspan=self.GetMaxColumn()+1, sticky="ew")
        row += 1
        # Budgeted Total
        WF.MakeLable(self, (row, 0), text="Total", width=WF.Buffer(1))
        WF.MakeEntry(self, (row, 1), text=self.vModel.Budgeted.total_stream, justify=tk.CENTER, bEditableState=False, background=vSkin.BG_ENTRY, display=BV.MakeValid_Money)
        row += 1

    def AddBudgetedColumn(self):
        row = 0
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
            row += 2
