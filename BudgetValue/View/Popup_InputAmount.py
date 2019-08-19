import TM_CommonPy as TM  # noqa
import rx  # noqa
from . import WidgetFactories as WF  # noqa
import BudgetValue as BV
from .Popup_Inheritable import Popup_Inheritable
import tkinter as tk


class Popup_InputAmount(Popup_Inheritable):
    previous_popup = None

    def __init__(self, parent, handler, cPos=None, vDestroyHandler=None):
        super().__init__(parent, handler, cPos=cPos, vDestroyHandler=vDestroyHandler)
        # Show Entry box
        self.amount_stream = rx.subjects.BehaviorSubject(0)  # FIX: leaking?
        WF.MakeEntry_ReadOnly(self, (0, 0), text="Input Amount:")
        WF.MakeEntry(self, (0, 1), stream=self.amount_stream, width=10, validation=BV.MakeValid_Money)

    def OnReturn(self, event):
        if isinstance(event.widget, tk.Entry):
            return
        super().OnReturn(event)

    def GetInputValue(self):
        return self.amount_stream.value
