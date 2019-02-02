import TM_CommonPy as TM  # noqa
import tkinter as tk  # noqa
import BudgetValue as BV  # noqa
from BudgetValue.View import WidgetFactories as WF  # noqa
from BudgetValue.View.Skin import vSkin  # noqa
from .. import Misc


class Table(Misc.BudgetedTable):
    def Refresh(self):
        super().Refresh()
        # Data
        #
        self.FinishRefresh()
