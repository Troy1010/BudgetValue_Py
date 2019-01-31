import TM_CommonPy as TM  # noqa
import tkinter as tk  # noqa
import BudgetValue as BV  # noqa
from BudgetValue.View import WidgetFactories as WF  # noqa
from .. import Misc  # noqa


class BudgetedTable(Misc.BudgetedTable):
    def Refresh(self):
        super().Refresh()
        self.AddRowHeaders()
        self.AddSeparationLables()
        row = self.GetMaxRow() + 1
        # Black bar
        tk.Frame(self, background='black', height=2).grid(row=row, columnspan=self.GetMaxColumn()+1, sticky="ew")
        row += 1
        # Budgeted Total
        WF.MakeLable(self, (row, 0), text="Budgeted Total", width=WF.Buffer(1))
        WF.MakeEntry_ReadOnly(self, (row, 1), text=self.vModel.BudgetedSpendables.total_stream, justify=tk.CENTER)
        row += 1
