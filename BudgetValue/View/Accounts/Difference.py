import TM_CommonPy as TM  # noqa
import tkinter as tk  # noqa
import BudgetValue as BV  # noqa
from BudgetValue.View import WidgetFactories as WF  # noqa
from .. import Misc  # noqa


class Difference(tk.Frame):
    def __init__(self, parent, vModel):
        assert isinstance(vModel, BV.Model.Model)
        tk.Frame.__init__(self, parent)
        self.vModel = vModel
        self.parent = parent

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
        # Difference
        WF.MakeLable(self, (0, 0), text="Difference", columnspan=1, width=BV.Buffer(1))
        vDifferenceNum = WF.MakeEntry_ReadOnly(self, (0, 1), text=self.vModel.Balance.balance_stream, justify=tk.CENTER)
        vDifferenceNum.ValidationHandler = BV.MakeValid_Money

        def __HighlightBalance(balance):
            if balance:
                vDifferenceNum.config(readonlybackground="pink")
            else:
                vDifferenceNum.config(readonlybackground="lightgreen")
        self.cDisposables.append(self.vModel.Balance.balance_stream.subscribe(
            __HighlightBalance
        ))
