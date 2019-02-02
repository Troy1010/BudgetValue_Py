import TM_CommonPy as TM  # noqa
import tkinter as tk  # noqa
import BudgetValue as BV  # noqa
from BudgetValue.View import WidgetFactories as WF  # noqa
from BudgetValue.View.Skin import vSkin  # noqa
from .. import Misc  # noqa


class Table(Misc.ModelTable):
    def Refresh(self):
        super().Refresh()
        # Header
        WF.MakeHeader(self, (0, 1), text="Timestamp")
        WF.MakeHeader(self, (0, 2), text="Category")
        WF.MakeHeader(self, (0, 3), text="Amount")
        WF.MakeHeader(self, (0, 4), text="Description")
        # Data
        for row, spend in enumerate(self.vModel.SpendHistory.values_flat(), self.iFirstDataRow):
            assert(isinstance(spend, BV.Model.SpendEntry))
            WF.MakeEntry(self, (row, 1), text=spend.timestamp_stream, justify=tk.LEFT, bTextIsTimestamp=True)
            WF.MakeEntry(self, (row, 2), text=spend.category_stream, justify=tk.LEFT)
            WF.MakeEntry(self, (row, 3), text=spend.amount_stream)
            WF.MakeEntry(self, (row, 4), text=spend.description_stream, justify=tk.LEFT)
